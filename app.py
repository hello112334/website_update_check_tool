"""
update check

"""
# Basic
import os
import sys
import time
import random
import pandas as pd
from io import BytesIO  # BytesIOのインポート

# Scrapy
import requests
from bs4 import BeautifulSoup

# Image Processing
from PIL import Image, ImageChops
import cv2
import time

# selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
# webdriver_manager
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from webdriver_manager.firefox import GeckoDriverManager

# numpy
import numpy as np

# datetimeモジュールを使用
import datetime

option = Options()
option.add_argument("--window-size=1400,960")

# Parameters
output_folder = "output"

def main():
    """note"""
    

# def window_switch(id):
#     """note"""
#     # ウィンドウハンドルのリストを取得
#     window_handles = driver.window_handles
#     print(window_handles[id])

#     # 2つ目のタブ（新しく開いたタブ）に切り替え
#     driver.switch_to.window(window_handles[id])

# def click_button(get_id):
#     """note"""
#     btn = driver.find_element(By.ID , get_id)
#     btn.click()
#     sleep_random(2)

def sleep_random(sec):
    """note"""

    slp_time = random.random()*sec + 2.0
    time.sleep(slp_time)

def get_list():
    """note"""
    # リストをnpで取得
    df = pd.read_csv('list.csv', header=0, dtype=str)

    # リストをリスト型に変換
    list = df.values.tolist()

    return list

def init(i, city, town):
    """note"""
    print(f"[INFO][{i}] INIT")

    # create folder
    os.makedirs(f"{output_folder}/{city}/{town}", exist_ok=True)

def get_txt(city, town, filename):
    """note"""
    f =  open(f"{output_folder}/{city}/{town}/{filename}.txt", mode='r', encoding='utf-8')
    data = f.read()

    return data

def save_txt(city, town, text, filename):
    """note"""
    with open(f"{output_folder}/{city}/{town}/{filename}.txt", mode='w', encoding='utf-8') as f:
        f.write(text)

def check_update(i, city, town, text, now_str):
    """
    Updates the CSV file with new data and checks for changes from previous updates.

    Parameters:
    i (int): Index of the row to update.
    city, town (str): Parameters used in the get_txt function.
    text (str): The current text data to compare.
    now_str (str): The current update timestamp.
    output_folder (str): Path to the folder containing the CSV file.

    Returns:
    None: The function updates the CSV file in place.
    """
    update_list_path = f"{output_folder}/update_list.csv"

    # Load the CSV file
    df = pd.read_csv(update_list_path, header=0, dtype=str)

    print(f"[INFO][{i}] now_str: {now_str}")

    # Add the current update timestamp as a new column if it doesn't exist
    if now_str not in df.columns:
        print(f"[INFO][{i}] Add Column : {now_str}")
        df[now_str] = ""

    # Update only if last_update is not NaN
    if not pd.isna(df.at[i, 'last_update']):
        # Retrieve the last update timestamp
        last_update = df.at[i, 'last_update']
        print(f"[INFO][{i}] Last Update : {last_update}")

        # Retrieve data from last update
        last_data = get_txt(city, town, last_update)

        # Compare with current data
        check_result = last_data == text
        print(f"[INFO][{i}] Check Result : {check_result}")

        # Update the comparison result in the dataframe
        df.at[i, now_str] = check_result

        # 画像を比較して差分をハイライト
        last_image = f"{output_folder}/{city}/{town}/{last_update}.png"
        current_image = f"{output_folder}/{city}/{town}/{now_str}.png"
        checked_image = f"{output_folder}/{city}/{town}/{now_str}_checked.png"
        compare_and_highlight_diff(last_image, current_image, checked_image)

    else:
        # If last_update is NaN, mark as "-"
        df.at[i, now_str] = "-"

    # Update the last_update field
    df.at[i, 'last_update'] = now_str

    # Save the updated DataFrame back to CSV
    df.to_csv(update_list_path, index=False)

def compare_and_highlight_diff(img1_path, img2_path, output_path):
    """note"""

    # 画像を読み込み
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)

    # 差分を検出
    diff = ImageChops.difference(img1, img2)

    # 差分がある場合のみ処理を進める
    if diff.getbbox():
        # 差分画像をOpenCV形式に変換
        diff_cv = np.array(diff.convert('RGB')) 
        gray = cv2.cvtColor(diff_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

        # 差分の領域を特定
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 元の画像1をOpenCV形式に変換
        img1_cv = np.array(img1.convert('RGB'))

        # 差分のある領域に赤枠を描画
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img1_cv, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        if len(contours) > 0:
            print(f"[INFO] 差分あり")
            output_path = output_path.replace(".png", "_diff.png")

        # 結果を保存
        result_img = Image.fromarray(img1_cv)
        result_img.save(output_path)


if __name__ == '__main__':

    try:
        # 開始
        print(f"[INFO] START {'-'*10}")
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        now_str = str(now.strftime('%Y%m%d%H'))

        # Listを取得する
        datalist = get_list()
        print("[INFO] ALL URL: {0}".format(len(datalist)))

        # リスト３列目の値(URL)を順番に取得する
        for i in range(len(datalist)):

            try:
                city_name = datalist[i][0]
                town_name = datalist[i][1]

                # 初期化
                init(i, city_name, town_name)
                
                # ドライバーを初期化する
                driver = webdriver.Chrome(options=option)

                # URLの値を取得
                get_url = datalist[i][2]
                print(f"[INFO][{i}] URL : {get_url}")

                # ブラウザのHTMLを取得
                html = requests.get(get_url)
                # html.encoding = 'shift_jis'  # 文字コード
                soup = BeautifulSoup(html.content, features="html.parser", from_encoding='shift_jis')
                soup_utf8 = str(soup.encode('utf-8'))

                # URLにアクセス
                driver.get(get_url)
                sleep_random(5)

                # メイン処理
                print(f"[INFO][{i}] MAIN")
                main()

                # ブラウザのHTMLを取得
                save_txt(city_name, town_name, soup_utf8, now_str)

                # screenshotを取得する
                # ページの高さを取得
                total_height = driver.execute_script("return document.body.scrollHeight")

                # スクリーンショットのリスト
                screenshots = []

                # ページをスクロールしながらスクリーンショットを取る
                for y in range(0, total_height, 960):
                    driver.execute_script(f"window.scrollTo(0, {y})")
                    time.sleep(1)  # スクロール後にページがロードされるのを待つ
                    screenshot = driver.get_screenshot_as_png()
                    screenshots.append(Image.open(BytesIO(screenshot)))

                # 画像を合成
                total_width = screenshots[0].width
                combined_height = sum([img.height for img in screenshots])
                combined_image = Image.new('RGB', (total_width, combined_height))

                current_height = 0
                for img in screenshots:
                    combined_image.paste(img, (0, current_height))
                    current_height += img.height

                # 画像を保存
                combined_image.save(f"{output_folder}/{city_name}/{town_name}/{now_str}.png")

                # 更新チェック
                print(f"[INFO][{i}] 更新チェック")
                check_update(i, city_name, town_name, soup_utf8, now_str)

                # driver.save_screenshot(f"{output_folder}/{city_name}/{town_name}/{now_str}.png")

                # ブラウザを閉じる
                driver.quit()

                print(f"[INFO][{i}] Finish")
            except Exception as err:
                print("[ERROR] {0}".format(err))

    except Exception as err:
        print("[ERROR] {0}".format(err))
    finally:
        
        print(f"[INFO] END {'-'*10}")
