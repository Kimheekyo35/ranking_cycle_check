import time
from pathlib import Path

def make_path():
    month = time.localtime().tm_mon
    date = time.localtime().tm_mday
    path = Path(f"./screenshots_{month}_{date}")
    return path

path = make_path()

def create_directory(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory '{path}' created successfully.")
    else:
        print("already exists")