import time
from pathlib import Path
import sys

# make_path 함수는 문자열 경로 또는 Path 객체 또는 None을 인자로 받을 수 있음
def make_path(source_path: str | Path | None = None) -> Path:
    # 파일 경로 생성 및 파이썬 이름 별로 디렉토리 구분
    month = time.localtime().tm_mon
    date = time.localtime().tm_mday
    script_name = Path(source_path or sys.argv[0]).stem
    return Path(f"./screenshots_{month}_{date}") / script_name

path = make_path(__file__)

# 존재하면 패쓰, 없으면 생성
def create_directory(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory '{path}' created successfully.")
    else:
        print("already exists")
