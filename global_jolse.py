from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from path_load import create_directory, make_path

url = "https://jolse.com/category/best/25/"

options = Options()
# options.add_argument("--headless=new")
options.add_argument("--window-size=1728,1398")

path: Path = make_path()
create_directory(path)

driver = webdriver.Chrome(options=options)

try:
    driver.get(url)
    time.sleep(5)

    # 화면 비율 조정
    wait = WebDriverWait(driver, 5)
    driver.execute_script("document.body.style.zoom='70%'")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, 300)")
    time.sleep(3)
    # 파일 저장
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    save_path = path / f"global_jolse_{hour}시_{minute}분.png"
    driver.save_screenshot(str(save_path))
    print("캡쳐캡쳐📸")
finally:
    driver.quit()
