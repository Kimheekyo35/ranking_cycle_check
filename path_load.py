import time
from pathlib import Path
import sys

def make_path(source_path: str | Path | None = None) -> Path:
    """
    Build a dated screenshots path that nests by script name.
    If source_path is not provided, falls back to the running script in sys.argv[0].
    """
    month = time.localtime().tm_mon
    date = time.localtime().tm_mday
    script_name = Path(source_path or sys.argv[0]).stem
    return Path(f"./screenshots_{month}_{date}") / script_name

# Useful if you want to reference the path of this helper directly.
path = make_path(__file__)

def create_directory(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory '{path}' created successfully.")
    else:
        print("already exists")
