import tkinter as tk
from tkinter import messagebox, ttk


class SettingsDialog(tk.Toplevel):
    def __init__(self, master, title: str, on_save, on_cancel=None):
        super().__init__(master)
        self.master = master
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.title(title)
        self.geometry("360x330")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="计价设置", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="保存后会从当前这一刻重新开始累计。").pack(anchor="w", pady=(4, 14))

        form = ttk.Frame(frame)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="工资类型").grid(row=0, column=0, sticky="w", pady=5)
        mode_box = ttk.Frame(form)
        mode_box.grid(row=0, column=1, sticky="ew", pady=5)
        for label, value in [("月薪", "monthly"), ("日薪", "daily"), ("时薪", "hourly")]:
            ttk.Radiobutton(mode_box, text=label, value=value, variable=self.master.pay_mode_var).pack(
                side="left", padx=(0, 8)
            )

        ttk.Label(form, text="工资金额").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.master.amount_var).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(form, text="已上班天数").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.master.base_workdays_var).grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(form, text="当前累计工资").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.master.base_total_var).grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Checkbutton(form, text="开机自启", variable=self.master.autostart_var).grid(
            row=4, column=1, sticky="w", pady=6
        )

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(18, 0))
        ttk.Button(actions, text="保存开始", style="Primary.TButton", command=self._save).pack(side="left")
        ttk.Button(actions, text="查看当月日历", command=self.master.open_calendar).pack(side="left", padx=8)
        ttk.Button(actions, text="取消", command=self._cancel).pack(side="right")

    def _save(self) -> None:
        ok = self.on_save()
        if ok:
            self.destroy()

    def _cancel(self) -> None:
        if self.on_cancel:
            self.on_cancel()
        self.destroy()


def read_settings_values(master) -> tuple[float, float, float] | None:
    try:
        amount = float(master.amount_var.get().strip())
        base_workdays = float(master.base_workdays_var.get().strip() or "0")
        base_total = float(master.base_total_var.get().strip() or "0")
        if amount < 0 or base_workdays < 0 or base_total < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("数据不正确", "工资金额、已上班天数、当前累计工资都要填写大于等于 0 的数字。")
        return None
    return amount, base_workdays, base_total
