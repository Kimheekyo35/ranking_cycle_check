from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
from pathlib import Path
from path_load import make_path
from path_load import create_directory

url = "https://global.oliveyoung.com/display/page/best-seller?target=pillsTab1Nav1"

path = make_path(__file__)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
try:
    driver.get(url)
    time.sleep(3)
    # 스크롤 다운 및 화면 비율 조정
    driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(3)

    driver.execute_script("window.scrollTo(0,200)")
    time.sleep(3)

    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    create_directory(path)
    
    # 저장 경로
    driver.save_screenshot(path / f"kr_oliveyoungglobal_{hour}시_{minute}분.png")
    print("캡쳐캡쳐📸")
finally:
    driver.quit()
