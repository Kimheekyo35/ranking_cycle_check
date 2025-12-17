from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import SB
from path_load import create_directory, make_path

options = Options()
options.add_argument("--window-size=1728,1398")

path: Path = make_path(__file__)
create_directory(path)

with SB(uc=True, test=True, headless=False) as sb:
    
    try:
        # seleniumbase로 
        url = "https://www.stylevana.com/en_US/best-sellers.html"
        sb.uc_open_with_reconnect(url, reconnect_time = 10)
        sb.uc_gui_handle_captcha()
        time.sleep(2)
        # 팝업창 떠서 새로고침 실시
        sb.driver.refresh()
        time.sleep(2)
    except Exception as e:
        print(f"Error loading page or handling CAPTCHA: {e}")
   
    try:
        sb.set_window_size(1920,1080)
        # 비율 조정 및 스크롤 다운
        sb.driver.execute_script("document.body.style.zoom='50%'")
        time.sleep(2)

        sb.driver.execute_script("window.scrollTo(0,200)")
        time.sleep(2)

        hour = time.localtime().tm_hour
        minute = time.localtime().tm_min
        create_directory(path)
        # 파일 저장
        try:
            hour = time.localtime().tm_hour
            minute = time.localtime().tm_min
            save_path = path / f"global_stylevana_{hour}시_{minute}분.png"
            print("캡쳐캡쳐📸")
        except Exception as e:
            print(f"Error:{e}")
    finally:
        sb.driver.quit()

