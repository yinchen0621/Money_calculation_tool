from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox, ttk

from .autostart import set_autostart
from .calendar_dialog import MonthCalendarDialog
from .core import earned_today, fmt_duration, fmt_money, scheduled_work_seconds, status_for
from .models import Config
from .settings_dialog import SettingsDialog, read_settings_values
from .storage import HISTORY_PATH, HistoryStore, load_config, save_config
from .theme import apply_theme


class SalaryClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("工资时钟")
        self.geometry("390x420")
        self.minsize(350, 390)

        self.config_data = load_config()
        self.history = HistoryStore()
        self._last_saved_key = ""

        self.pay_mode_var = tk.StringVar(value=self.config_data.pay_mode)
        self.amount_var = tk.StringVar(value=str(self.config_data.amount))
        self.autostart_var = tk.BooleanVar(value=self.config_data.autostart)
        self.base_workdays_var = tk.StringVar(value=str(self.config_data.base_workdays))
        self.base_total_var = tk.StringVar(value=str(self.config_data.base_total_earned))

        self.today_var = tk.StringVar(value="¥0.00")
        self.month_var = tk.StringVar(value="¥0.00")
        self.rate_var = tk.StringVar(value="¥0.0000 / 秒")
        self.progress_var = tk.StringVar(value="00:00:00 / 07:45:00")
        self.status_var = tk.StringVar(value="准备中")
        self.baseline_var = tk.StringVar(value="")

        apply_theme(self)
        self._build_ui()
        if not self.config_data.initialized:
            self.after(100, self.open_initial_settings)
        self._tick()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="工资时钟", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="工作日 08:30-18:00，午休 11:45-13:30 扣除").pack(anchor="w", pady=(4, 14))

        ttk.Label(frame, text="今日已赚").pack(anchor="w")
        ttk.Label(frame, textvariable=self.today_var, style="Money.TLabel").pack(anchor="w", pady=(0, 8))

        grid = ttk.Frame(frame)
        grid.pack(fill="x", pady=(4, 10))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        ttk.Label(grid, text="累计工资").grid(row=0, column=0, sticky="w")
        ttk.Label(grid, text="当前速度").grid(row=0, column=1, sticky="w")
        ttk.Label(grid, textvariable=self.month_var, style="SubMoney.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.rate_var, style="SubMoney.TLabel").grid(row=1, column=1, sticky="w")

        self.progress = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(8, 4))
        ttk.Label(frame, textvariable=self.progress_var).pack(anchor="w")
        ttk.Label(frame, textvariable=self.status_var).pack(anchor="w", pady=(0, 10))
        ttk.Label(frame, textvariable=self.baseline_var).pack(anchor="w", pady=(0, 12))

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="设置", command=self.open_settings).pack(side="left")
        ttk.Button(actions, text="日历", command=self.open_calendar).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="最小化", command=self.iconify).pack(side="left", padx=8)
        ttk.Button(actions, text="查看记录", command=self.show_history).pack(side="right")

    def open_initial_settings(self) -> None:
        SettingsDialog(self, "开始计价前先确认", self.save_settings, self.destroy)

    def open_settings(self) -> None:
        SettingsDialog(self, "设置", self.save_settings)

    def open_calendar(self) -> None:
        MonthCalendarDialog(self)

    def save_settings(self) -> bool:
        values = read_settings_values(self)
        if values is None:
            return False
        amount, base_workdays, base_total = values

        old_autostart = self.config_data.autostart
        now = datetime.now()
        start_today, start_seconds, _ = earned_today(
            Config(pay_mode=self.pay_mode_var.get(), amount=amount),
            now,
        )
        next_config = Config(
            pay_mode=self.pay_mode_var.get(),
            amount=amount,
            autostart=self.autostart_var.get(),
            initialized=True,
            base_workdays=base_workdays,
            base_total_earned=base_total,
            tracking_started_at=now.isoformat(timespec="seconds"),
            start_work_seconds=start_seconds,
            start_today_earned=start_today,
        )

        if old_autostart != next_config.autostart:
            try:
                set_autostart(next_config.autostart)
            except Exception as exc:
                self.autostart_var.set(old_autostart)
                messagebox.showwarning("开机自启设置失败", str(exc))
                return False

        self.config_data = next_config
        save_config(self.config_data)
        self._tick()
        messagebox.showinfo("已保存", "已从当前数据开始计价。")
        return True

    def show_history(self) -> None:
        win = tk.Toplevel(self)
        win.title("工资记录")
        win.geometry("420x360")

        frame = ttk.Frame(win, padding=14)
        frame.pack(fill="both", expand=True)
        columns = ("date", "earned", "time")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        tree.heading("date", text="日期")
        tree.heading("earned", text="当天工资")
        tree.heading("time", text="有效工时")
        tree.column("date", width=120)
        tree.column("earned", width=120)
        tree.column("time", width=120)
        tree.pack(fill="both", expand=True)

        for key in sorted(self.history.data.keys(), reverse=True):
            item = self.history.data[key]
            tree.insert(
                "",
                "end",
                values=(key, fmt_money(float(item.get("earned", 0))), fmt_duration(int(item.get("work_seconds", 0)))),
            )

        ttk.Label(frame, text=f"记录文件：{HISTORY_PATH}").pack(anchor="w", pady=(8, 0))

    def _tracked_total(self, today: date, earned: float) -> float:
        if not self.config_data.tracking_started_at:
            return self.config_data.base_total_earned + earned
        try:
            start_day = datetime.fromisoformat(self.config_data.tracking_started_at).date()
        except ValueError:
            start_day = today

        if today == start_day:
            live_increment = max(0.0, earned - self.config_data.start_today_earned)
            return self.config_data.base_total_earned + live_increment

        total = self.config_data.base_total_earned
        for key, item in self.history.data.items():
            try:
                item_day = date.fromisoformat(key)
            except ValueError:
                continue
            if start_day < item_day < today:
                total += float(item.get("earned", 0.0))
        return total + earned

    def _tick(self) -> None:
        if not self.config_data.initialized:
            self.today_var.set("等待填写")
            self.month_var.set("等待开始")
            self.rate_var.set("¥0.0000 / 秒")
            self.progress_var.set("00:00:00 / 07:45:00")
            self.status_var.set("请先填写数据并点击“开始计价”")
            self.baseline_var.set("")
            self.after(1000, self._tick)
            return

        now = datetime.now()
        today = now.date()
        earned, seconds, day_total = earned_today(self.config_data, now)
        scheduled = scheduled_work_seconds(today)
        tracked_total = self._tracked_total(today, earned)

        rate = earned / seconds if seconds else (day_total / scheduled if scheduled else 0.0)
        percent = (seconds / scheduled * 100) if scheduled else 0

        self.today_var.set(fmt_money(earned))
        self.month_var.set(fmt_money(tracked_total))
        self.rate_var.set(f"¥{rate:.4f} / 秒")
        self.progress_var.set(f"{fmt_duration(seconds)} / {fmt_duration(scheduled)}")
        self.status_var.set(status_for(now))
        self.baseline_var.set(
            f"起点：已上班 {self.config_data.base_workdays:g} 天，"
            f"起始累计 {fmt_money(self.config_data.base_total_earned)}"
        )
        self.progress["value"] = percent

        save_key = f"{today.isoformat()}:{int(earned * 100)}:{seconds // 30}"
        if save_key != self._last_saved_key:
            self.history.save_day(today, earned, seconds)
            self._last_saved_key = save_key

        self.after(1000, self._tick)


def main() -> None:
    app = SalaryClockApp()
    app.mainloop()
