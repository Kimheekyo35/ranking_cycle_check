from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
from path_load import make_path, create_directory
from seleniumbase import SB

path = make_path(__file__)
options = Options()
# cloudfare 우회 기능이 있는 SeleniumBase 사용
with SB(uc=True, test=True) as sb:
    try:
        url = "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&utm_source=google&utm_medium=shopping_search&utm_campaign=onpro_emnet_googlepmax_25_0101_1231&utm_content=pc_rankingtotal&utm_source=google&utm_medium=shopping_search&utm_campaign=onpro_emnet_googlepmax_25_0101_1231&utm_term=&_CAD=google_pmax&gad_source=1&gad_campaignid=19630508381&gbraid=0AAAAADKpDR5e8TMyXTal60e91ZkT2NxAn&gclid=Cj0KCQiArt_JBhCTARIsADQZaykpTdWyIwil8cqM0o0dzLhbP1ts7zhgDiOEt_TzkOlBOauhNKLTNnEaAiIzEALw_wcB"
        # reconnect_time 옵션으로 재접속 시도 시간 설정
        sb.uc_open_with_reconnect(url, reconnect_time=10)
        sb.uc_gui_handle_captcha()
        time.sleep(3)

    except Exception as e:
        print(f"Error loading page or handling CAPTCHA: {e}")
   
    try:
        sb.set_window_size(1920,1080)
        time.sleep(3)
        
        # 비율 조정 및 스크롤 다운
        sb.driver.execute_script("document.body.style.zoom='50%'")
        sb.driver.execute_script("window.scrollTo(0,200)")
        time.sleep(3)
        
        hour = time.localtime().tm_hour
        minute = time.localtime().tm_min
        create_directory(path)
        try:
            save_path = path / f"oliveyoung_{hour}시_{minute}분.png"
            image = sb.driver.save_screenshot(save_path)
        except Exception as e:
            print(f"Error saving screenshot: {e}")
    finally:
        sb.driver.quit()
