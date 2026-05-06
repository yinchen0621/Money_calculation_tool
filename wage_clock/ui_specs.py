from dataclasses import dataclass


COLORS = {
    "background": "#f8f8f6",
    "surface": "#ffffff",
    "ink": "#171717",
    "muted": "#6d6d68",
    "border": "#deded8",
    "soft_border": "#e8e8e2",
    "inverse_text": "#f7f7f2",
    "inverse_muted": "#bcbcb4",
    "rest_day": "#eeeeea",
    "work_day": "#d9d9d2",
}


@dataclass(frozen=True)
class ActionButtonSpec:
    key: str
    label: str
    icon: str


ACTION_BUTTONS = (
    ActionButtonSpec("settings", "设置", "⚙"),
    ActionButtonSpec("calendar", "日历", "□"),
    ActionButtonSpec("hide", "隐藏", "−"),
    ActionButtonSpec("history", "记录", "≡"),
)


def compact_status_text(status: str) -> str:
    mapping = {
        "工作时间中，工资正在增长": "工作中",
        "午休中，工资暂停增长": "午休中",
        "还没到上班时间": "未开始",
        "今天工作时间已结束": "已结束",
        "今天不是工作日，工资不增长": "休息日",
    }
    return mapping.get(status, status)
