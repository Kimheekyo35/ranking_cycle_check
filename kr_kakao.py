from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from path_load import make_path
from path_load import create_directory

url = "https://gift.kakao.com/ranking/best/delivery/2?priceRange=ALL"

path = make_path()
options = Options()
# options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080") 

driver = webdriver.Chrome(options=options)
try:
    driver.get(url)
    time.sleep(3)
    wait = WebDriverWait(driver,5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    # 스크롤 다운
    driver.execute_script("document.body.style.zoom='50%'")
    driver.execute_script("window.scrollTo(0,100)")
    wait = WebDriverWait(driver,5)
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    create_directory(path)
    driver.save_screenshot(path / f"kr_kakaogift_{hour}시_{minute}분.png")
    print("캡쳐캡쳐📸")
finally:
    driver.quit()