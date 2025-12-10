import os
import time
import random
import subprocess
import calendar
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)


def load_env(env_path: Path = Path(".env")):
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


load_env()

OYOUNG_LOGIN_URL = "https://oypartner.cj.net/CJOYP/nexacro/main.fo"
OYOUNG_MENU_URL = "http://oypartner.cj.net/CJOYP/nexacro/callMain.fo"

OYOUNG_EMAIL = os.getenv("OYOUNG_EMAIL")
OYOUNG_PASSWORD = os.getenv("OYOUNG_PASSWORD")
OYOUNG_REPORT_FROM = os.getenv("OYOUNG_REPORT_FROM")
OYOUNG_REPORT_TO = os.getenv("OYOUNG_REPORT_TO")
OYOUNG_DOWNLOAD_BASE = (
    os.getenv("OYOUNG_DOWNLOAD_BASE")
    or os.getenv("PORTONE_DOWNLOAD_BASE")
    or os.getenv("HWAHAE_DOWNLOAD_BASE")
    or os.getenv("ABLY_DOWNLOAD_BASE")
)
OYOUNG_DOWNLOAD_WAIT = int(os.getenv("OYOUNG_DOWNLOAD_WAIT", "120"))

DEBUG_PORT = int(os.getenv("OYOUNG_DEBUG_PORT", os.getenv("PORTONE_DEBUG_PORT", "9222")))
USER_DATA_DIR = os.getenv(
    "OYOUNG_USER_DATA_DIR",
    os.getenv("PORTONE_USER_DATA_DIR", r"C:\chrome-debug-profile"),
)

ACTION_DELAY_MIN = 0.8
ACTION_DELAY_MAX = 1.5


def resolve_chrome_path():
    candidates = [
        os.getenv("OYOUNG_CHROME_PATH"),
        os.getenv("PORTONE_CHROME_PATH"),
        os.getenv("HWAHAE_CHROME_PATH"),
        os.getenv("ABLY_CHROME_PATH"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        str(
            Path.home()
            / "AppData"
            / "Local"
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe"
        ),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        expanded = os.path.expandvars(candidate)
        if Path(expanded).exists():
            return expanded
    raise FileNotFoundError("Chrome 실행 파일이 필요합니다. OYOUNG_CHROME_PATH를 확인하세요.")


CHROME_PATH = resolve_chrome_path()


def human_delay():
    time.sleep(random.uniform(ACTION_DELAY_MIN, ACTION_DELAY_MAX))


def start_debug_chrome():
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
    ]
    print(f"[INFO] 디버그 크롬 실행 ({CHROME_PATH})")
    subprocess.Popen(cmd)
    time.sleep(3)


def attach_to_debug_chrome(max_retry: int = 10, delay: float = 1.0):
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
    last_err = None
    for attempt in range(1, max_retry + 1):
        try:
            print(f"[INFO] 디버그 크롬 WebDriver 연결 시도 {attempt}/{max_retry}")
            driver = webdriver.Chrome(options=options)
            print("[INFO] Selenium이 디버그 크롬에 붙었습니다.")
            return driver
        except WebDriverException as exc:
            last_err = exc
            time.sleep(delay)
    raise RuntimeError(f"디버그 크롬 연결 실패: {last_err}")


def configure_download_behavior(driver, download_path: str):
    path = Path(download_path)
    path.mkdir(parents=True, exist_ok=True)
    try:
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": str(path.resolve())},
        )
        print(f"[INFO] Chrome 다운로드 경로 설정: {path}")
    except Exception as exc:
        print(f"[WARN] 다운로드 경로 설정 실패: {exc}")


def _parse_month(raw_value: Optional[str], default: date) -> date:
    text = (raw_value or "").strip()
    if not text:
        return default
    formats = [
        ("%Y-%m-%d", 10),
        ("%Y/%m/%d", 10),
        ("%Y.%m.%d", 10),
        ("%Y_%m_%d", 10),
        ("%Y-%m", 7),
        ("%Y/%m", 7),
        ("%Y.%m", 7),
    ]
    for fmt, length in formats:
        candidate = text[:length]
        try:
            parsed = datetime.strptime(candidate, fmt)
            return parsed.date().replace(day=1)
        except ValueError:
            continue
    return default


def resolve_date_range() -> Tuple[date, date]:
    today = date.today().replace(day=1)
    start_month = _parse_month(OYOUNG_REPORT_FROM, today)
    end_month = _parse_month(OYOUNG_REPORT_TO, start_month)
    start_date = start_month.replace(day=1)
    last_day = calendar.monthrange(end_month.year, end_month.month)[1]
    end_date = end_month.replace(day=last_day)
    return start_date, end_date


def prepare_download_directory(start_date: date, end_date: date) -> str:
    folder = f"{start_date.strftime('%Y_%m_%d')}-{end_date.strftime('%Y_%m_%d')}"
    if OYOUNG_DOWNLOAD_BASE:
        base = Path(OYOUNG_DOWNLOAD_BASE).expanduser()
    else:
        base = Path.home() / "Documents" / "문서"
    base_path = base / "reports" / folder
    target = base_path / "oyoung"
    if target.exists():
        index = 1
        while (base_path / f"oyoung_{index}").exists():
            index += 1
        target = base_path / f"oyoung_{index}"
    target.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] 다운로드 폴더: {target}")
    return str(target.resolve())


def _split_base_and_index(stem: str):
    import re

    pattern = re.compile(r"^(.*)\s\((\d+)\)$")
    match = pattern.match(stem)
    if match:
        return match.group(1), int(match.group(2))
    return stem, 0


def snapshot_download_state(download_path: str):
    path = Path(download_path)
    path.mkdir(parents=True, exist_ok=True)
    snapshot = {"names": set(), "base_counts": {}}
    for file_path in path.iterdir():
        if not file_path.is_file():
            continue
        snapshot["names"].add(file_path.name)
        base, idx = _split_base_and_index(file_path.stem)
        snapshot["base_counts"][base] = max(snapshot["base_counts"].get(base, 0), idx)
    return snapshot


def finalize_new_downloads(download_path: str, snapshot, wait_seconds: Optional[int] = None):
    path = Path(download_path)
    timeout = wait_seconds or OYOUNG_DOWNLOAD_WAIT
    deadline = time.time() + timeout

    while time.time() < deadline:
        current = {p.name: p for p in path.iterdir() if p.is_file()}
        new_files = [
            file_path for name, file_path in current.items() if name not in snapshot["names"]
        ]
        if new_files:
            saved = []
            for file_path in sorted(new_files, key=lambda p: p.stat().st_mtime):
                base, _ = _split_base_and_index(file_path.stem)
                ext = file_path.suffix
                if base in snapshot["base_counts"]:
                    snapshot["base_counts"][base] += 1
                    new_name = f"{base} ({snapshot['base_counts'][base]}){ext}"
                else:
                    snapshot["base_counts"][base] = 0
                    new_name = file_path.name
                target = file_path.with_name(new_name)
                if file_path.name != new_name:
                    if target.exists():
                        target.unlink()
                    file_path.rename(target)
                    file_path = target
                snapshot["names"].add(file_path.name)
                saved.append(file_path.name)
            print(f"[INFO] 새 파일 저장: {', '.join(saved)}")
            return True
        time.sleep(0.5)
    print("[WARN] 새 다운로드 파일을 찾지 못했습니다.")
    return False


def wait_for_element(driver, locator, timeout: int = 20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def force_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    human_delay()
    driver.execute_script("arguments[0].click();", element)


def find_elements_by_text(driver, text: str):
    script = """
        const target = arguments[0];
        const result = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT, null);
        while (walker.nextNode()) {
            const el = walker.currentNode;
            if (!el || !el.textContent) continue;
            if (el.textContent.trim().includes(target)) {
                let clickable = el;
                while (clickable && clickable !== document.body) {
                    const style = window.getComputedStyle(clickable);
                    const hasPointer = style && style.cursor && style.cursor !== 'auto';
                    const hasClick = clickable.onclick || clickable.getAttribute('onclick');
                    const id = clickable.id || '';
                    if (
                        hasPointer ||
                        hasClick ||
                        /mainframe_vFrameSet_.*_div_menu_btn/i.test(id) ||
                        /grd_menu/i.test(id)
                    ) {
                        result.push(clickable);
                        break;
                    }
                    clickable = clickable.parentElement;
                }
            }
        }
        return result;
    """
    elements = driver.execute_script(script, text)
    if not elements:
        raise NoSuchElementException(f"텍스트 '{text}' 를 포함하는 요소를 찾지 못했습니다.")
    return elements


def log_header_texts(driver):
    script = """
        const container = document.getElementById('mainframe_vFrameSet_topFrame_form_div_menuScrollableInnerContainerElement_inner');
        if (!container) {
            return [];
        }
        const items = Array.from(container.querySelectorAll('div[id^="mainframe_vFrameSet_topFrame_form_div_menu_btn"]'));
        return items.map(el => el.textContent ? el.textContent.trim() : '').filter(Boolean);
    """
    try:
        texts = driver.execute_script(script)
        print(f"[DEBUG] 상단 메뉴 텍스트: {texts}")
    except Exception as exc:
        print(f"[DEBUG] 상단 메뉴 텍스트 추출 실패: {exc}")


def log_available_frames(driver):
    script = """
        return Array.from(document.querySelectorAll('iframe, frame')).map(f => ({
            id: f.id || '',
            name: f.name || ''
        }));
    """
    try:
        frames = driver.execute_script(script)
        print(f"[DEBUG] 사용 가능한 프레임: {frames}")
    except Exception as exc:
        print(f"[DEBUG] 프레임 정보 추출 실패: {exc}")


def wait_for_frames(driver, timeout: int = 30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        frames = driver.find_elements(By.CSS_SELECTOR, "iframe,frame")
        if frames:
            log_available_frames(driver)
            return True
        time.sleep(0.5)
    log_available_frames(driver)
    return False


def switch_to_frame_by_keyword(driver, keyword: str, timeout: int = 30) -> bool:
    keyword = keyword.lower()
    deadline = time.time() + timeout
    last_len = -1
    while time.time() < deadline:
        driver.switch_to.default_content()
        frames = driver.find_elements(By.CSS_SELECTOR, "iframe,frame")
        if len(frames) != last_len:
            last_len = len(frames)
        for frame in frames:
            ident = (
                (frame.get_attribute("id") or "") + " " + (frame.get_attribute("name") or "")
            ).lower()
            if keyword in ident:
                driver.switch_to.frame(frame)
                return True
        time.sleep(0.5)
    log_available_frames(driver)
    return False


def switch_to_left_frame(driver):
    if not switch_to_frame_by_keyword(driver, "leftframe"):
        raise TimeoutException("leftFrame 전환에 실패했습니다.")


def switch_to_work_frame(driver):
    if not switch_to_frame_by_keyword(driver, "workframe"):
        raise TimeoutException("workFrame 전환에 실패했습니다.")


def find_search_input(driver):
    locators = [
        (By.CSS_SELECTOR, "input[id*='searchMenu_input']"),
        (By.CSS_SELECTOR, "div[id*='searchMenuInputElement'] input"),
        (By.CSS_SELECTOR, "div[title='edit'] input"),
    ]
    for locator in locators:
        elements = driver.find_elements(*locator)
        if elements:
            return elements[0]
    raise NoSuchElementException("좌측 검색 입력창을 찾지 못했습니다.")


def ensure_login(driver):
    driver.get(OYOUNG_LOGIN_URL)
    human_delay()
    wait = WebDriverWait(driver, 30)
    username = wait_for_element(driver, (By.ID, "loginId"))
    password = wait_for_element(driver, (By.ID, "loginPw"))
    username.clear()
    username.send_keys(OYOUNG_EMAIL or "")
    human_delay()
    password.clear()
    password.send_keys(OYOUNG_PASSWORD or "")
    human_delay()
    login_btn = driver.find_element(By.ID, "loginButton")
    force_click(driver, login_btn)
    print("[INFO] 로그인 버튼을 클릭했습니다.")


def open_oliveone(driver):
    wait = WebDriverWait(driver, 30)
    olive_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_gnb_oliveone a"))
    )
    handles_before = driver.window_handles[:]
    force_click(driver, olive_btn)
    print("[INFO] OLIVE ONE 버튼을 클릭했습니다.")
    try:
        WebDriverWait(driver, 10).until(
            lambda d: len(d.window_handles) > len(handles_before)
        )
        new_handles = [h for h in driver.window_handles if h not in handles_before]
        if new_handles:
            driver.switch_to.window(new_handles[0])
            print("[INFO] OLIVE ONE 새 창으로 전환했습니다.")
    except TimeoutException:
        pass

    time.sleep(1)
    try:
        alert = driver.switch_to.alert
        human_delay()
        alert.accept()
        print("[INFO] 알림 창을 확인했습니다.")
    except Exception:
        pass
    driver.switch_to.default_content()
    time.sleep(5)
    if wait_for_frames(driver, timeout=15):
        print("[DEBUG] 프레임이 감지되었습니다.")
    else:
        print("[WARN] 일정 시간 내에 프레임을 찾지 못했습니다.")


def open_performance_menu(driver):
    driver.switch_to.default_content()
    switch_to_left_frame(driver)
    search_input = find_search_input(driver)
    search_input.clear()
    search_input.send_keys("매장별매입실적조회")
    human_delay()
    search_input.send_keys(Keys.ENTER)
    print("[INFO] 메뉴 검색창에서 '매장별매입실적조회'를 검색했습니다.")
    time.sleep(1)

    submenu_buttons = find_elements_by_text(driver, "매장별매입실적조회")
    clicked = False
    for button in submenu_buttons:
        try:
            force_click(driver, button)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        raise TimeoutException("매장별매입실적조회 메뉴를 클릭하지 못했습니다.")

    print("[INFO] 매장별매입실적조회 화면을 열었습니다.")
    driver.switch_to.default_content()


def fill_date_range(driver, start_date: date, end_date: date):
    switch_to_work_frame(driver)
    start_input = wait_for_element(
        driver,
        (
            By.ID,
            "mainframe_vFrameSet_midFrameSet_mainFrameSet_workFrameSet_PPT013_form_div_workFrame_div_work_div_search_cal_poStrtYmd_calendaredit_input",
        ),
    )
    end_input = wait_for_element(
        driver,
        (
            By.ID,
            "mainframe_vFrameSet_midFrameSet_mainFrameSet_workFrameSet_PPT013_form_div_workFrame_div_work_div_search_cal_poEndYmd_calendaredit_input",
        ),
    )
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    start_input.clear()
    start_input.send_keys(start_str)
    human_delay()
    start_input.send_keys(Keys.TAB)
    human_delay()
    end_input.clear()
    end_input.send_keys(end_str)
    human_delay()
    end_input.send_keys(Keys.ENTER)
    print(f"[INFO] 기간 입력: {start_str} ~ {end_str}")


def click_search(driver):
    switch_to_work_frame(driver)
    search_btn = wait_for_element(
        driver,
        (
            By.ID,
            "mainframe_vFrameSet_midFrameSet_mainFrameSet_workFrameSet_PPT013_form_div_workFrame_btn_Search",
        ),
    )
    force_click(driver, search_btn)
    print("[INFO] 조회 버튼을 클릭했습니다.")
    time.sleep(10)


def click_excel_buttons(driver, download_dir: str):
    switch_to_work_frame(driver)
    buttons = [
        (
            "mainframe_vFrameSet_midFrameSet_mainFrameSet_workFrameSet_PPT013_form_div_workFrame_div_work_div_compDtls_tab_tabpg_tabitem1_div_gdsDay_btn_xlsDwld",
            "일별 엑셀다운로드",
        ),
        (
            "mainframe_vFrameSet_midFrameSet_mainFrameSet_workFrameSet_PPT013_form_div_workFrame_div_work_div_compDtls_tab_tabpg_tabitem1_div_gdsDayDtl_btn_xlsDwld",
            "상세 엑셀다운로드",
        ),
    ]
    for element_id, desc in buttons:
        snapshot = snapshot_download_state(download_dir)
        button = wait_for_element(driver, (By.ID, element_id))
        force_click(driver, button)
        print(f"[INFO] {desc} 버튼을 클릭했습니다.")
        finalize_new_downloads(download_dir, snapshot, wait_seconds=OYOUNG_DOWNLOAD_WAIT)
        human_delay()


def main():
    if not OYOUNG_EMAIL or not OYOUNG_PASSWORD:
        raise RuntimeError("OYOUNG_EMAIL / OYOUNG_PASSWORD 값을 확인하세요.")

    start_debug_chrome()
    driver = attach_to_debug_chrome()
    try:
        driver.maximize_window()
    except Exception:
        pass

    ensure_login(driver)
    open_oliveone(driver)

    start_date, end_date = resolve_date_range()
    download_dir = prepare_download_directory(start_date, end_date)
    configure_download_behavior(driver, download_dir)

    open_performance_menu(driver)
    fill_date_range(driver, start_date, end_date)
    click_search(driver)
    click_excel_buttons(driver, download_dir)

    print(f"[INFO] 현재 페이지 URL: {driver.current_url}")


if __name__ == "__main__":
    main()
