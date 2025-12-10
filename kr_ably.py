from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from path_load import make_path
from path_load import create_directory

url = "https://m.a-bly.com/screens?screen_name=BEAUTY_DEPARTMENT"
options = webdriver.ChromeOptions()
# options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

path = make_path()

driver = webdriver.Chrome(options=options)
driver.set_window_size(2304,1864)

try:
    driver.get(url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0,100)")
    driver.execute_script("document.body.style.zoom='50%'")
    
    time.sleep(3)
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    create_directory(path)
    driver.save_screenshot(path/f"kr_ably_{hour}시_{minute}분.png")
    driver = webdriver.Chrome(options=Options())
    print("캡쳐캡쳐📸")
finally:
    driver.quit()