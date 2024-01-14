"""
website update check

"""
# Basic
from dotenv import load_dotenv
import datetime
import numpy as np
from slack_sdk.webhook import WebhookClient
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import cv2
from PIL import Image, ImageChops
import os
import time
import random
import pandas as pd
from io import BytesIO  # BytesIOのインポート
import ssl
import difflib

# Scrapy
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

# OpenAI
import openai


class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')  # Lowering security level
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)


session = requests.Session()
session.mount('https://', SSLAdapter())

# .env
load_dotenv()

option = Options()
option.add_argument("--window-size=1400,960")
option.add_argument('--headless')
option.add_argument("--disable-dev-shm-usage")  # /dev/shmパーティションの使用を無効化
option.add_argument("--no-sandbox")  # サンドボックスモード無効化
option.add_argument("--disable-extensions")  # 拡張機能無効化
option.add_argument("--disable-popup-blocking")  # ポップアップブロックを無効化
option.add_argument("--lang=ja")  # 言語設定
option.add_argument("user-agent=Custom User-Agent")  # ユーザーエージェントの設定
option.add_argument('--disable-gpu')  # GPUハードウェアアクセラレーションを無効化

# .env Parameters
OUTPUT_PATH = os.getenv('OUTPUT_PATH')
WEB_HOOK_URL = os.getenv('WEB_HOOK_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# slack class


class Info_news_slack:
    """
    自治体サイト更新通知アプリSlack
    """

    def __init__(self):
        """note"""
        self.webhook = WebhookClient(WEB_HOOK_URL)
        self.update_status = []

    def update_status(self, text):
        """note"""
        self.update_status.append(text)

    def send(self, now_str):
        """note"""
        # update_statusからmd形式のテキスト
        text = ""

        # 基本情報
        text += f"[{now_str}][更新情報]\n"

        # 更新状況
        if len(self.update_status) > 0:
            for i in range(len(self.update_status)):
                text += f"{self.update_status[i]}\n"
        else:
            text += "更新なし\n"

        # テキストを送信
        print(f"[INFO] Slack Send: {text}")
        # response = self.webhook.send(
        #     text="fallback",
        #     blocks=[
        #         {
        #             "type": "section",
        #             "text": {
        #                 "type": "mrkdwn",
        #                 "text": text
        #             }
        #         }
        #     ]
        # )


def main():
    """note"""


def sleep_random(sec):
    """
    ランダムにスリープする
    :param sec: スリープする秒数
    """

    slp_time = random.random()*sec + 2.0
    time.sleep(slp_time)


def get_list():
    """
    リストを取得する
    """
    # リストをnpで取得
    df = pd.read_csv('list.csv', header=0, dtype=str, encoding='shift_jis')

    # リストをリスト型に変換
    list = df.values.tolist()

    return list


def init(i, city, town):
    """
    初期化
    :param i: インデックス
    :param city: 市区町村
    :param town: 市区町村

    フォルダを作成する
    """
    print(f"[INFO][{i}] INIT")

    # create folder
    os.makedirs(f"{OUTPUT_PATH}/{city}/{town}", exist_ok=True)


def get_txt(city, town, filename):
    """
    テキストを取得する
    :param city: 市区町村
    :param town: 市区町村
    :param filename: ファイル名(yyyyMMDDHH)
    """
    f = open(f"{OUTPUT_PATH}/{city}/{town}/{filename}.txt",
             mode='r', encoding='utf-8')
    data = f.read()

    return data


def save_txt(city, town, text, filename):
    """
    テキストを保存する
    :param city: 市区町村
    :param town: 市区町村
    :param text: テキスト
    :param filename: ファイル名(yyyyMMDDHH)
    """
    with open(f"{OUTPUT_PATH}/{city}/{town}/{filename}.txt", mode='w', encoding='utf-8') as f:
        f.write(text)


def extract_html_diff(old_html, new_html):
    """
    2つのHTML間の差分を抽出します。
    :param old_html: 古いHTMLの内容
    :param new_html: 新しいHTMLの内容
    :return: 差分の内容
    """
    old_soup = BeautifulSoup(old_html, 'html.parser', from_encoding='shift_jis')
    new_soup = BeautifulSoup(new_html, 'html.parser', from_encoding='shift_jis')

    # HTMLを整形して文字列に変換
    old_text = old_soup.prettify()
    new_text = new_soup.prettify()

    # 差分を取得
    diff = difflib.ndiff(old_text.splitlines(keepends=True),
                         new_text.splitlines(keepends=True))

    # 差分の中で追加または変更された行を抽出
    diff_text = [line for line in diff if line.startswith(
        '+ ') or line.startswith('- ')]

    return '\n'.join(diff_text)


def check_update(i, city, town, text, now_str):
    """
    Updates the CSV file with new data and checks for changes from previous updates.

    Parameters:
    i (int): Index of the row to update.
    city, town (str): Parameters used in the get_txt function.
    text (str): The current text data to compare.
    now_str (str): The current update timestamp.

    Returns:
    status (bool): True if the data has changed since the last update, False otherwise.
    summary (str): The summary of the changes between the current and previous data.

    None: The function updates the CSV file in place.
    """
    update_list_path = f"{OUTPUT_PATH}/update_list.csv"

    # Load the CSV file
    df = pd.read_csv(update_list_path, header=0, dtype=str, encoding='utf-8')
    # print(f"[INFO][{i}] now_str: {now_str}")

    # Add the current update timestamp as a new column if it doesn't exist
    if now_str not in df.columns:
        print(f"[INFO][{i}] Add Column : {now_str}")
        df[now_str] = ""

    # Update only if last_update is not NaN and current data is different from last data
    update_status = False
    summary = ""
    if not pd.isna(df.at[i, 'last_update']):
        if now_str != df.at[i, 'last_update']:
            # Retrieve the last update timestamp
            last_update = df.at[i, 'last_update']
            print(f"[INFO][{i}] Last Update : {last_update}")

            # Retrieve data from last update
            last_data = get_txt(city, town, last_update)

            # Compare with current data
            check_result = last_data == text
            diff = extract_html_diff(last_data, text)
            print(f"[INFO][{i}] Check Result : {check_result}")
            if not check_result:
                summary = gpt_summarize(diff)

            # Update the comparison result in the dataframe
            df.at[i, now_str] = check_result

            # 画像を比較して差分をハイライト
            last_image = f"{OUTPUT_PATH}/{city}/{town}/{last_update}.png"
            current_image = f"{OUTPUT_PATH}/{city}/{town}/{now_str}.png"
            checked_image = f"{OUTPUT_PATH}/{city}/{town}/{now_str}_checked.png"
            compare_and_highlight_diff(
                last_image, current_image, checked_image)

            df.at[i, 'last_update'] = now_str

            # 更新結果
            if not check_result:
                update_status = True
    else:
        # If last_update is NaN, mark as "-"
        df.at[i, now_str] = "-"
        df.at[i, 'last_update'] = now_str

    # Update the last_update field
    # df.at[i, 'last_update'] = now_str

    # Save the updated DataFrame back to CSV
    df.to_csv(update_list_path, index=False)

    return update_status, summary


def gpt_summarize(text):
    """
    GPT-3を使用してテキストを要約します。
    :param text: 要約するテキスト
    :param api_key: OpenAI APIキー

    :return: 要約されたテキスト
    """
    openai.api_key = OPENAI_API_KEY
    
    # print(f"[INFO] GPT-3 Summarize: {text}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは優秀な新聞記者です。"},
            {"role": "assistant", "content": f"{text}"},
            {"role": "user", "content": "この内容を50字以内で日本語で要約してください。"}],
        max_tokens=150
    )
    
    if response['choices'][0]['message']['content']:
        return response['choices'][0]['message']['content']
    else:
        return "要約できませんでした"


def compare_and_highlight_diff(img1_path, img2_path, output_path):
    """
    画像を比較して差分をハイライト
    :param img1_path: 画像1のパス
    :param img2_path: 画像2のパス
    :param output_path: 出力画像のパス
    """

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
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 元の画像1をOpenCV形式に変換
        img1_cv = np.array(img1.convert('RGB'))

        # 差分のある領域に赤枠を描画
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img1_cv, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if len(contours) > 0:
            print(f"[INFO] 画像には差分あります")
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
        now_str2 = str(now.strftime('%Y年%m月%d日%H時'))

        # Slack init - 自治体サイト更新通知アプリ
        info_news_slack = Info_news_slack()

        # Listを取得する
        datalist = get_list()
        print("[INFO] ALL URL: {0}".format(len(datalist)))

        # リスト３列目の値(URL)を順番に取得する
        for i in range(len(datalist)):

            try:
                city_name = datalist[i][0]
                town_name = datalist[i][1]
                print(f"[INFO][{i}] {city_name} {town_name}")

                # 初期化
                init(i, city_name, town_name)

                # ドライバーを初期化する
                driver = webdriver.Chrome(options=option)

                # URLの値を取得
                get_url = datalist[i][2]
                print(f"[INFO][{i}] URL : {get_url}")

                # ブラウザのHTMLを取得
                html = session.get(get_url)

                # html.encoding = 'shift_jis'  # 文字コード
                soup = BeautifulSoup(
                    html.content, features="html.parser", from_encoding='shift_jis')
                # soup_utf8 = str(soup.encode('utf-8'))
                encoded_soup = soup.encode('utf-8')
                decoded_soup = encoded_soup.decode('utf-8')
                print(f"[INFO][{i}] soup : {decoded_soup}")

                # URLにアクセス
                driver.get(get_url)
                sleep_random(5)

                # メイン処理
                print(f"[INFO][{i}] MAIN")
                main()

                # ブラウザのHTMLを取得
                save_txt(city_name, town_name, decoded_soup, now_str)

                # ページの高さを取得
                total_height = driver.execute_script(
                    "return document.body.scrollHeight")

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
                combined_image = Image.new(
                    'RGB', (total_width, combined_height))

                current_height = 0
                for img in screenshots:
                    combined_image.paste(img, (0, current_height))
                    current_height += img.height

                # 画像を保存
                combined_image.save(
                    f"{OUTPUT_PATH}/{city_name}/{town_name}/{now_str}.png")

                # 更新チェック
                print(f"[INFO][{i}] 更新チェック")
                update_status, summary = check_update(
                    i, city_name, town_name, decoded_soup, now_str)
                if update_status:
                    info_news_slack.update_status(
                        f"[{i+1}] {city_name} {town_name} {get_url}\n```{summary}```")

                # ブラウザを閉じる
                driver.quit()

                print(f"[INFO][{i}] {'-'*10}")
            except Exception as err:
                print("[ERROR] {0}".format(err))

    except Exception as err:
        print("[ERROR] {0}".format(err))

    finally:
        # 結果をSlackに送信
        info_news_slack.send(now_str2)

        print(f"[INFO] END {'-'*10}")
