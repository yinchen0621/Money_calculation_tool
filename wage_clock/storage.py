import json
import os
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from .models import Config

APP_NAME = "SalaryClock"


def app_dir() -> Path:
    root = os.environ.get("APPDATA")
    if root:
        path = Path(root) / APP_NAME
    else:
        path = Path.home() / f".{APP_NAME.lower()}"
    path.mkdir(parents=True, exist_ok=True)
    return path


CONFIG_PATH = app_dir() / "config.json"
HISTORY_PATH = app_dir() / "history.json"


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return Config(
            pay_mode=data.get("pay_mode", "monthly"),
            amount=float(data.get("amount", 12000.0)),
            autostart=bool(data.get("autostart", False)),
            initialized=bool(data.get("initialized", False)),
            base_workdays=float(data.get("base_workdays", 0.0)),
            base_total_earned=float(data.get("base_total_earned", 0.0)),
            tracking_started_at=data.get("tracking_started_at", ""),
            start_work_seconds=int(data.get("start_work_seconds", 0)),
            start_today_earned=float(data.get("start_today_earned", 0.0)),
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return Config()


def save_config(config: Config) -> None:
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class HistoryStore:
    def __init__(self, path: Path = HISTORY_PATH):
        self.path = path
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def save_day(self, day: date, amount: float, seconds: int) -> None:
        key = day.isoformat()
        self.data[key] = {
            "earned": round(amount, 2),
            "work_seconds": int(seconds),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

