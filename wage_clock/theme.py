from tkinter import ttk

from .ui_specs import COLORS

BACKGROUND = COLORS["background"]
TEXT = COLORS["ink"]
MUTED = COLORS["muted"]
SURFACE = COLORS["surface"]
BORDER = COLORS["border"]


def apply_theme(root) -> None:
    root.configure(bg=BACKGROUND)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=BACKGROUND)
    style.configure("Surface.TFrame", background=SURFACE, relief="flat")
    style.configure("TLabel", background=BACKGROUND, foreground=TEXT, font=("Microsoft YaHei UI", 9))
    style.configure("Muted.TLabel", background=BACKGROUND, foreground=MUTED, font=("Microsoft YaHei UI", 9))
    style.configure("Title.TLabel", background=BACKGROUND, foreground=TEXT, font=("Microsoft YaHei UI", 16, "bold"))
    style.configure("Money.TLabel", background=BACKGROUND, foreground=TEXT, font=("Segoe UI", 30, "bold"))
    style.configure("SubMoney.TLabel", background=SURFACE, foreground=TEXT, font=("Segoe UI", 15, "bold"))
    style.configure("CardLabel.TLabel", background=SURFACE, foreground=MUTED, font=("Microsoft YaHei UI", 8))
    style.configure("Hero.TFrame", background=TEXT)
    style.configure("HeroLabel.TLabel", background=TEXT, foreground=COLORS["inverse_muted"], font=("Microsoft YaHei UI", 8))
    style.configure("HeroMoney.TLabel", background=TEXT, foreground=COLORS["inverse_text"], font=("Segoe UI", 30, "bold"))
    style.configure("HeroStatus.TLabel", background=TEXT, foreground=COLORS["inverse_text"], font=("Microsoft YaHei UI", 8))
    style.configure(
        "TButton",
        padding=(8, 5),
        font=("Microsoft YaHei UI", 9),
        background=SURFACE,
        foreground=TEXT,
        bordercolor=BORDER,
    )
    style.configure(
        "Primary.TButton",
        padding=(8, 5),
        font=("Microsoft YaHei UI", 9),
        background=TEXT,
        foreground=COLORS["inverse_text"],
        bordercolor=TEXT,
    )
    style.map(
        "Primary.TButton",
        background=[("active", "#2a2a2a")],
        foreground=[("active", COLORS["inverse_text"])],
    )
    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
    style.configure("TRadiobutton", background=BACKGROUND, foreground=TEXT)
    style.configure("TCheckbutton", background=BACKGROUND, foreground=TEXT)
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#e6e6df",
        background=TEXT,
        bordercolor="#e6e6df",
        lightcolor=TEXT,
        darkcolor=TEXT,
    )
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, foreground=TEXT, rowheight=26, bordercolor=BORDER)
    style.configure("Treeview.Heading", background="#eeeeea", foreground=TEXT, font=("Microsoft YaHei UI", 9, "bold"))
    style.configure("TLabelframe", background=BACKGROUND, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BACKGROUND, foreground=TEXT)
