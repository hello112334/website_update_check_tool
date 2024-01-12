# website_update_check_tool
## Basic files
* app.py: main program
* list.csv: url list(65 cities)
* update_list.csv: compared result

## Compare Standard
1. Html content of url
2. Image file

## Description
This tool can download HTML Script and take screenshot automatically.
Screenshots will be compared with last image and current image, and save as a image file after adding a red frame in different part.

## Getting Started
### Dependencies

* ex. Windows OS, Python 3.11, etc.

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
