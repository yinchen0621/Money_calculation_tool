from datetime import date, datetime
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageDraw
import pystray

from .autostart import set_autostart
from .calendar_dialog import MonthCalendarDialog
from .core import elapsed_workdays_after, earned_today, fmt_duration, fmt_money, scheduled_work_seconds, status_for
from .models import Config
from .settings_dialog import SettingsDialog, read_settings_values
from .storage import HISTORY_PATH, HistoryStore, load_config, save_config
from .theme import apply_theme
from .ui_specs import ACTION_BUTTONS, COLORS, compact_status_text


class SalaryClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("工资时钟")
        self.geometry("430x430")
        self.minsize(410, 410)
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.bind("<Unmap>", self._hide_iconified_window)

        self.config_data = load_config()
        self.history = HistoryStore()
        self._last_saved_key = ""
        self._exiting = False
        self._tray_icon = None

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
        self._start_tray_icon()
        if not self.config_data.initialized:
            self.after(100, self.open_initial_settings)
        self._tick()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)

        topbar = ttk.Frame(frame)
        topbar.pack(fill="x")
        ttk.Label(topbar, text="工资时钟", style="Title.TLabel").pack(side="left")
        ttk.Label(topbar, text="本地记录", style="Muted.TLabel").pack(side="right", pady=(5, 0))

        hero = tk.Frame(frame, bg=COLORS["ink"], highlightthickness=0)
        hero.pack(fill="x", pady=(12, 10))
        hero.columnconfigure(0, weight=1)
        tk.Label(
            hero,
            text="今日已赚",
            bg=COLORS["ink"],
            fg=COLORS["inverse_muted"],
            font=("Microsoft YaHei UI", 9),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 0))
        tk.Label(
            hero,
            textvariable=self.status_var,
            bg=COLORS["ink"],
            fg=COLORS["inverse_text"],
            font=("Microsoft YaHei UI", 8),
        ).grid(row=0, column=1, sticky="e", padx=16, pady=(14, 0))
        tk.Label(
            hero,
            textvariable=self.today_var,
            bg=COLORS["ink"],
            fg=COLORS["inverse_text"],
            font=("Segoe UI", 30, "bold"),
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(4, 0))
        tk.Label(
            hero,
            textvariable=self.baseline_var,
            bg=COLORS["ink"],
            fg=COLORS["inverse_muted"],
            font=("Microsoft YaHei UI", 8),
            anchor="w",
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(4, 14))

        grid = ttk.Frame(frame)
        grid.pack(fill="x", pady=(0, 10))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        total_card = self._create_card(grid)
        total_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        speed_card = self._create_card(grid)
        speed_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ttk.Label(total_card, text="累计工资", style="CardLabel.TLabel").pack(anchor="w", padx=10, pady=(9, 0))
        ttk.Label(total_card, textvariable=self.month_var, style="SubMoney.TLabel").pack(anchor="w", padx=10, pady=(1, 9))
        ttk.Label(speed_card, text="当前速度", style="CardLabel.TLabel").pack(anchor="w", padx=10, pady=(9, 0))
        ttk.Label(speed_card, textvariable=self.rate_var, style="SubMoney.TLabel").pack(anchor="w", padx=10, pady=(1, 9))

        progress_card = self._create_card(frame)
        progress_card.pack(fill="x", pady=(0, 10))
        progress_header = ttk.Frame(progress_card, style="Surface.TFrame")
        progress_header.pack(fill="x", padx=10, pady=(9, 7))
        ttk.Label(progress_header, text="今日有效工时", style="CardLabel.TLabel").pack(side="left")
        ttk.Label(progress_header, textvariable=self.progress_var, style="CardLabel.TLabel").pack(side="right")
        self.progress = ttk.Progressbar(progress_card, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=10, pady=(0, 10))

        actions = ttk.Frame(frame)
        actions.pack(fill="x")
        for column in range(4):
            actions.columnconfigure(column, weight=1, uniform="actions")
        commands = {
            "settings": self.open_settings,
            "calendar": self.open_calendar,
            "hide": self.hide_to_tray,
            "history": self.show_history,
        }
        for column, spec in enumerate(ACTION_BUTTONS):
            style = "Primary.TButton" if spec.key == "settings" else "TButton"
            ttk.Button(
                actions,
                text=f"{spec.icon} {spec.label}",
                style=style,
                command=commands[spec.key],
            ).grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 4, 0 if column == 3 else 4))

    def _create_card(self, master):
        return tk.Frame(master, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])

    def _create_tray_image(self) -> Image.Image:
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill="#146c5f")
        draw.rectangle((18, 20, 46, 26), fill="white")
        draw.rectangle((18, 32, 46, 38), fill="white")
        draw.rectangle((18, 44, 34, 50), fill="white")
        return image

    def _start_tray_icon(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", self._tray_show_window, default=True),
            pystray.MenuItem("退出程序", self._tray_quit),
        )
        self._tray_icon = pystray.Icon("SalaryClock", self._create_tray_image(), "工资时钟", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _tray_show_window(self, _icon=None, _item=None) -> None:
        self.after(0, self.show_from_tray)

    def _tray_quit(self, _icon=None, _item=None) -> None:
        self.after(0, self.exit_app)

    def hide_to_tray(self) -> None:
        if self._exiting:
            return
        self.withdraw()

    def _hide_iconified_window(self, event) -> None:
        if event.widget is self and not self._exiting and self.state() == "iconic":
            self.after(0, self.hide_to_tray)

    def show_from_tray(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

    def exit_app(self) -> None:
        self._exiting = True
        if self._tray_icon is not None:
            self._tray_icon.stop()
            self._tray_icon = None
        self.destroy()

    def open_initial_settings(self) -> None:
        SettingsDialog(self, "开始计价前先确认", self.save_settings, self.exit_app)

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
        ttk.Label(frame, text="工资记录", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
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

    def _start_day(self, today: date) -> date:
        if not self.config_data.tracking_started_at:
            return today
        try:
            return datetime.fromisoformat(self.config_data.tracking_started_at).date()
        except ValueError:
            return today

    def _current_workdays(self, today: date) -> float:
        return self.config_data.base_workdays + elapsed_workdays_after(self._start_day(today), today)

    def _tick(self) -> None:
        if not self.config_data.initialized:
            self.today_var.set("等待填写")
            self.month_var.set("等待开始")
            self.rate_var.set("¥0.0000 / 秒")
            self.progress_var.set("00:00:00 / 07:45:00")
            self.status_var.set("待设置")
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
        self.status_var.set(compact_status_text(status_for(now)))
        self.baseline_var.set(
            f"当前：已上班 {self._current_workdays(today):g} 天，"
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
