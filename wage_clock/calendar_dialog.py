import calendar
from datetime import date
import tkinter as tk
from tkinter import ttk

from .holiday_calendar import HOLIDAY_SOURCE, day_label, is_official_workday


class MonthCalendarDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        today = date.today()
        self.year = today.year
        self.month = today.month
        self.title("当月日历")
        self.geometry("430x450")
        self.minsize(390, 420)
        self.transient(master)

        self.title_var = tk.StringVar()
        self.summary_var = tk.StringVar()
        self.days_frame = ttk.Frame(self)
        self._build()
        self._render_month()

    def _build(self) -> None:
        wrapper = ttk.Frame(self, padding=16)
        wrapper.pack(fill="both", expand=True)

        header = ttk.Frame(wrapper)
        header.pack(fill="x")
        ttk.Button(header, text="上月", command=self._prev_month).pack(side="left")
        ttk.Label(header, textvariable=self.title_var, style="Title.TLabel").pack(side="left", expand=True)
        ttk.Button(header, text="下月", command=self._next_month).pack(side="right")

        legend = ttk.Frame(wrapper)
        legend.pack(fill="x", pady=(12, 6))
        ttk.Label(legend, text="红色：需要上班").pack(side="left")
        ttk.Label(legend, text="  灰色：休息/法定假日").pack(side="left")

        weekdays = ttk.Frame(wrapper)
        weekdays.pack(fill="x")
        for index, name in enumerate(["一", "二", "三", "四", "五", "六", "日"]):
            weekdays.columnconfigure(index, weight=1)
            ttk.Label(weekdays, text=name, anchor="center").grid(row=0, column=index, sticky="ew", padx=2)

        self.days_frame.pack(fill="both", expand=True, pady=(4, 8))
        ttk.Label(wrapper, textvariable=self.summary_var).pack(anchor="w")
        ttk.Label(wrapper, text=HOLIDAY_SOURCE).pack(anchor="w", pady=(4, 0))

    def _prev_month(self) -> None:
        if self.month == 1:
            self.year -= 1
            self.month = 12
        else:
            self.month -= 1
        self._render_month()

    def _next_month(self) -> None:
        if self.month == 12:
            self.year += 1
            self.month = 1
        else:
            self.month += 1
        self._render_month()

    def _render_month(self) -> None:
        for child in self.days_frame.winfo_children():
            child.destroy()

        self.title_var.set(f"{self.year} 年 {self.month} 月")
        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(self.year, self.month)
        workdays = 0
        restdays = 0

        for row, week in enumerate(weeks):
            self.days_frame.rowconfigure(row, weight=1)
            for column, day in enumerate(week):
                self.days_frame.columnconfigure(column, weight=1)
                in_month = day.month == self.month
                is_work = in_month and is_official_workday(day)
                if in_month and is_work:
                    workdays += 1
                elif in_month:
                    restdays += 1

                bg = "#fff5f3" if is_work else "#eeeeee"
                fg = "#b42318" if is_work else "#6b7280"
                if not in_month:
                    bg = "#f7f4ef"
                    fg = "#c5c5c5"

                cell = tk.Frame(self.days_frame, bg=bg, highlightthickness=1, highlightbackground="#ddd6cc")
                cell.grid(row=row, column=column, sticky="nsew", padx=2, pady=2)
                tk.Label(cell, text=str(day.day), bg=bg, fg=fg, font=("Segoe UI", 13, "bold")).pack(
                    anchor="nw", padx=6, pady=(5, 0)
                )
                label = day_label(day) if in_month else ""
                tk.Label(cell, text=label, bg=bg, fg=fg, font=("Microsoft YaHei UI", 8)).pack(
                    anchor="nw", padx=6, pady=(0, 5)
                )

        self.summary_var.set(f"本月需要上班 {workdays} 天，休息 {restdays} 天")

