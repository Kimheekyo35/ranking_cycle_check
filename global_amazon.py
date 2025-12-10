from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from path_load import create_directory, make_path

url = "https://www.amazon.com/stores/page/A9D20D90-ADA2-4603-8F3F-345CC1002580?ingress=0&visitId=53d8d4bd-ddc9-4dfa-8b11-8712f8234ac7&channel=SA_Amazon%20Keyword"

options = Options()
# options.add_argument("--headless=new")
options.add_argument("--window-size=1728,1398")

path: Path = make_path()
create_directory(path)

driver = webdriver.Chrome(options=options)

try:
    driver.get(url)
    time.sleep(5)
    # 새로고침 설정
    driver.refresh()
    time.sleep(2)

    # 화면 비율 조정
    wait = WebDriverWait(driver, 5)
    driver.execute_script("document.body.style.zoom='60%'")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    driver.execute_script("window.scrollTo(0, 500)")
    time.sleep(3)

    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    save_path = path / f"global_amazon_{hour}시_{minute}분.png"
    driver.save_screenshot(str(save_path))
    print("캡쳐캡쳐📸")
finally:
    driver.quit()
