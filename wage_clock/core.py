import calendar
from datetime import date, datetime, time

from .holiday_calendar import is_official_workday
from .models import Config

WORK_START = time(8, 30)
LUNCH_START = time(11, 45)
LUNCH_END = time(13, 30)
WORK_END = time(18, 0)


def is_workday(day: date) -> bool:
    return is_official_workday(day)


def combine(day: date, clock: time) -> datetime:
    return datetime.combine(day, clock)


def scheduled_work_seconds(day: date) -> int:
    if not is_workday(day):
        return 0
    morning = combine(day, LUNCH_START) - combine(day, WORK_START)
    afternoon = combine(day, WORK_END) - combine(day, LUNCH_END)
    return int(morning.total_seconds() + afternoon.total_seconds())


def worked_seconds_at(moment: datetime) -> int:
    day = moment.date()
    if not is_workday(day):
        return 0

    ranges = [
        (combine(day, WORK_START), combine(day, LUNCH_START)),
        (combine(day, LUNCH_END), combine(day, WORK_END)),
    ]
    total = 0
    for start, end in ranges:
        if moment <= start:
            continue
        total += int((min(moment, end) - start).total_seconds())
    return max(0, min(total, scheduled_work_seconds(day)))


def working_days_in_month(year: int, month: int) -> int:
    days = calendar.monthrange(year, month)[1]
    return sum(1 for number in range(1, days + 1) if is_workday(date(year, month, number)))


def daily_pay(config: Config, day: date) -> float:
    if config.pay_mode == "monthly":
        workdays = working_days_in_month(day.year, day.month)
        return config.amount / workdays if workdays else 0.0
    if config.pay_mode == "daily":
        return config.amount
    if config.pay_mode == "hourly":
        return config.amount * (scheduled_work_seconds(day) / 3600)
    return 0.0


def earned_today(config: Config, moment: datetime) -> tuple[float, int, float]:
    seconds = worked_seconds_at(moment)
    scheduled = scheduled_work_seconds(moment.date())
    if config.pay_mode == "hourly":
        earned = config.amount * seconds / 3600
        day_total = config.amount * scheduled / 3600
    else:
        day_total = daily_pay(config, moment.date())
        earned = day_total * seconds / scheduled if scheduled else 0.0
    return earned, seconds, day_total


def status_for(moment: datetime) -> str:
    day = moment.date()
    if not is_workday(day):
        return "今天不是工作日，工资不增长"
    if moment.time() < WORK_START:
        return "还没到上班时间"
    if LUNCH_START <= moment.time() < LUNCH_END:
        return "午休中，工资暂停增长"
    if moment.time() >= WORK_END:
        return "今天工作时间已结束"
    return "工作时间中，工资正在增长"


def fmt_money(value: float) -> str:
    return f"¥{value:,.2f}"


def fmt_duration(seconds: int) -> str:
    hours, rest = divmod(max(0, seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
