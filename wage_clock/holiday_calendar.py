from datetime import date

HOLIDAY_SOURCE = "国务院办公厅关于2026年部分节假日安排的通知（国办发明电〔2025〕7号）"

HOLIDAYS_2026 = {
    "2026-01-01": "元旦",
    "2026-01-02": "元旦",
    "2026-01-03": "元旦",
    "2026-02-15": "春节",
    "2026-02-16": "春节",
    "2026-02-17": "春节",
    "2026-02-18": "春节",
    "2026-02-19": "春节",
    "2026-02-20": "春节",
    "2026-02-21": "春节",
    "2026-02-22": "春节",
    "2026-02-23": "春节",
    "2026-04-04": "清明节",
    "2026-04-05": "清明节",
    "2026-04-06": "清明节",
    "2026-05-01": "劳动节",
    "2026-05-02": "劳动节",
    "2026-05-03": "劳动节",
    "2026-05-04": "劳动节",
    "2026-05-05": "劳动节",
    "2026-06-19": "端午节",
    "2026-06-20": "端午节",
    "2026-06-21": "端午节",
    "2026-09-25": "中秋节",
    "2026-09-26": "中秋节",
    "2026-09-27": "中秋节",
    "2026-10-01": "国庆节",
    "2026-10-02": "国庆节",
    "2026-10-03": "国庆节",
    "2026-10-04": "国庆节",
    "2026-10-05": "国庆节",
    "2026-10-06": "国庆节",
    "2026-10-07": "国庆节",
}

MAKEUP_WORKDAYS_2026 = {
    "2026-01-04": "元旦调休上班",
    "2026-02-14": "春节调休上班",
    "2026-02-28": "春节调休上班",
    "2026-05-09": "劳动节调休上班",
    "2026-09-20": "国庆节调休上班",
    "2026-10-10": "国庆节调休上班",
}

HOLIDAYS_BY_YEAR = {
    2026: HOLIDAYS_2026,
}

MAKEUP_WORKDAYS_BY_YEAR = {
    2026: MAKEUP_WORKDAYS_2026,
}


def date_key(day: date) -> str:
    return day.isoformat()


def holiday_name(day: date) -> str:
    return HOLIDAYS_BY_YEAR.get(day.year, {}).get(date_key(day), "")


def makeup_workday_name(day: date) -> str:
    return MAKEUP_WORKDAYS_BY_YEAR.get(day.year, {}).get(date_key(day), "")


def is_official_workday(day: date) -> bool:
    if makeup_workday_name(day):
        return True
    if holiday_name(day):
        return False
    return day.weekday() < 5


def day_label(day: date) -> str:
    makeup = makeup_workday_name(day)
    if makeup:
        return makeup
    holiday = holiday_name(day)
    if holiday:
        return holiday
    if day.weekday() >= 5:
        return "周末休息"
    return "工作日"

