from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support import expected_conditions as EC
from path_load import create_directory
from path_load import make_path
url = "https://www.musinsa.com/main/beauty/ranking?gf=A&storeCode=beauty&sectionId=231&contentsId=&categoryCode=104000&ageBand=AGE_BAND_ALL"

path = make_path(__file__)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
try:
    driver.get(url)
    time.sleep(3)

    # 화면 비율 조정 및 스크롤
    driver.execute_script("document.body.style.zoom='50%'")
    time.sleep(3)
    
    driver.execute_script("window.scrollTo(0,100)")
    time.sleep(3)

    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    create_directory(path)
    save_path = path / f"kr_musinsabeauty_{hour}시_{minute}분.png"
    driver.save_screenshot(save_path)
    print("캡쳐캡쳐📸")
    
finally:
    driver.quit()
