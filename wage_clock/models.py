from dataclasses import dataclass


@dataclass
class Config:
    pay_mode: str = "monthly"
    amount: float = 12000.0
    autostart: bool = False
    initialized: bool = False
    base_workdays: float = 0.0
    base_total_earned: float = 0.0
    tracking_started_at: str = ""
    start_work_seconds: int = 0
    start_today_earned: float = 0.0

