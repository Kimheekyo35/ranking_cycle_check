from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from path_load import create_directory, make_path

url = "https://www.qoo10.jp/gmkt.inc/BestSellers/?g=2"

options = Options()
# options.add_argument("--headless=new")
options.add_argument("--window-size=1728,1398")

path: Path = make_path(__file__)
create_directory(path)

driver = webdriver.Chrome(options=options)

try:
    driver.get(url)
    time.sleep(3)
    # 새로고침 실시 (콘텐츠 로딩 문제 해결용)
    driver.refresh()

    # 화면 비율 조정
    driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(3)   

    driver.execute_script("window.scrollTo(0, 5000)")
    time.sleep(3)

    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    save_path = path / f"jp_q100_{hour}시_{minute}분.png"
    driver.save_screenshot(str(save_path))
    print("캡쳐캡쳐📸")
finally:
    driver.quit()
