# website_update_check_tool
## Basic files
- app.py: main program
- list.csv: url list(64 cities + 1 google website for test)
- update_list.csv: compared result of last and current website
  - True: Same
  - False: not Same

## Compare Standard
1. Html content of url
* Image file(for check)

## Description
* This tool can download HTML Script and take screenshot automatically from url list(list.csv).
* Screenshots will be compared with last image and current image, and save as a image file after adding a red frame in different part.

## Getting Started
### Dependencies
* Windows OS, Python(version should be 3.8?+).

### Main packages and APIs
1. BeautifulSoup
2. selenium
3. PIL
4. cv2
5. requests
6. ssl
7. slack-sdk

### 0. Download this project and go to the folder with CMD
```
cd (YOUR_PATH)/website_update_check_tool
```

### 1. Package Install
```
pip install -r requirements.txt
```

or you can just pickup packages you need

### 2. Set parameter in .env
1. OUTPUT_PATH
2. WEB_HOOK_URL 
3. OPENAI_API_KEY 

### 3. python script.py
```
python app.py
```

## Other
### Update requirements.txt
```
pip freeze > requirements.txt
```

## Refrence
### python-slack-sdk
https://slack.dev/python-slack-sdk/webhook/index.html