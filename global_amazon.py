from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from path_load import create_directory, make_path

url = "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care/zgbs/beauty/ref=zg_bs_nav_beauty_0"

options = Options()
# options.add_argument("--headless=new")
options.add_argument("--window-size=1728,1398")

path: Path = make_path()
create_directory(path)

driver = webdriver.Chrome(options=options)

try:
    driver.get(url)
    time.sleep(3)
    # 새로고침 설정
    driver.refresh()
    time.sleep(3)
    # 화면 비율 조정
    # wait = WebDriverWait(driver, 5)
    driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(3)
    # wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    driver.execute_script("window.scrollTo(0, 500)")
    time.sleep(5)

    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    save_path = path / f"global_amazon_{hour}시_{minute}분.png"
    driver.save_screenshot(str(save_path))
    print("캡쳐캡쳐📸")
finally:
    driver.quit()
