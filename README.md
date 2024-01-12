# website_update_check_tool
## Basic files
* app.py: main program
* list.csv: url list(64 cities + 1 google website for test)
* update_list.csv: compared result of last and current website

## Compare Standard
1. Html content of url
2. Image file

## Description
* lThis tool can download HTML Script and take screenshot automatically from url list(list.csv).
* Screenshots will be compared with last image and current image, and save as a image file after adding a red frame in different part.

## Getting Started
### Dependencies
* Windows OS, Python(version should be 3.8?+).

### 0. Download this project and go to the folder with CMD
```
cd (YOUR_PATH)/website_update_check_tool
```

### 1. Package Install
```
pip install -r requirements.txt
```

### 2. python script.py
```
python app.py
```



## Other
### Update requirements.txt
```
pip freeze > requirements.txt
```
