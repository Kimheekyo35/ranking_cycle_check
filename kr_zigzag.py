from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from path_load import create_directory, make_path

url = "https://zigzag.kr/categories/1098?middle_category_id=1098&title=%EB%B7%B0%ED%8B%B0+%EC%A0%84%EC%B2%B4"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1728,1398")

path: Path = make_path(__file__)
create_directory(path)

driver = webdriver.Chrome(options=options)

try:
    driver.get(url)
    time.sleep(3)
    # 화면 비율 조정
    # wait = WebDriverWait(driver, 5)
    driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(3)

    driver.execute_script("window.scrollTo(0, 100)")
    time.sleep(3)

    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    save_path = path / f"kr_zigzag_{hour}시_{minute}분.png"
    driver.save_screenshot(str(save_path))
    print("캡쳐캡쳐📸")
finally:
    driver.quit()
