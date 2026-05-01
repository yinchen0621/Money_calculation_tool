from tkinter import ttk

BACKGROUND = "#f7f4ef"
TEXT = "#263238"
ACCENT = "#146c5f"
MUTED = "#3b4a54"


def apply_theme(root) -> None:
    root.configure(bg=BACKGROUND)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=BACKGROUND)
    style.configure("TLabel", background=BACKGROUND, foreground=TEXT)
    style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
    style.configure("Money.TLabel", font=("Segoe UI", 30, "bold"), foreground=ACCENT)
    style.configure("SubMoney.TLabel", font=("Segoe UI", 15, "bold"), foreground=MUTED)
    style.configure("TButton", padding=(10, 6))
    style.configure("TRadiobutton", background=BACKGROUND)
    style.configure("TCheckbutton", background=BACKGROUND)
    style.configure("TLabelframe", background=BACKGROUND)
    style.configure("TLabelframe.Label", background=BACKGROUND, foreground=TEXT)

