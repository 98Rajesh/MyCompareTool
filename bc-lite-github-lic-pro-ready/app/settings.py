import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_DIR = Path(os.getenv("BC_LITE_CONFIG_DIR") or (Path.home() / ".bc-lite"))
CONFIG_PATH = CONFIG_DIR / "config.json"

@dataclass
class AppSettings:
    theme: str = "system"          # system | light | dark (future)
    ignore_whitespace: bool = False
    bytes_per_row: int = 16        # hex viewer bytes per row

def load_settings() -> AppSettings:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        base = AppSettings()
        base_dict = asdict(base)
        base_dict.update({k: v for k, v in data.items() if k in base_dict})
        return AppSettings(**base_dict)
    except Exception:
        return AppSettings()

def save_settings(settings: AppSettings) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
