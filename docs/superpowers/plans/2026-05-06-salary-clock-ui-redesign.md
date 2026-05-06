# Salary Clock UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved compact black-and-white dashboard UI for the Tkinter salary clock while preserving existing salary calculation and tray behavior.

**Architecture:** Keep the existing Tkinter app structure. Add one small pure-Python UI specification module for tokens, short status labels, and action button metadata so behavior that is not tied to a live Tk root can be tested first. Use `theme.py` for ttk styling and `app.py` for layout composition.

**Tech Stack:** Python 3, Tkinter/ttk, Pillow, pystray, unittest.

---

### File Structure

- Create: `wage_clock/ui_specs.py`
  - Owns UI tokens, action button metadata, and `compact_status_text()`.
  - No Tk imports, so tests can run without opening windows.
- Create: `tests/test_ui_specs.py`
  - Verifies action order, icon labels, compact status conversion, and required color tokens.
- Modify: `wage_clock/theme.py`
  - Applies black-and-white theme tokens to ttk controls, labels, buttons, progress bars, entries, and Treeview.
- Modify: `wage_clock/app.py`
  - Rebuilds the main window as a 430x430 compact dashboard.
  - Adds dark hero area, metric cards, progress card, and icon+text action buttons.
  - Keeps current tray code and current total/workday behavior.
- Modify: `wage_clock/settings_dialog.py`
  - Applies primary button style and tighter black-and-white form rhythm.
- Modify: `wage_clock/calendar_dialog.py`
  - Aligns calendar colors with the monochrome theme while preserving workday/rest distinction.

### Task 1: UI Spec Tests And Pure Metadata

**Files:**
- Create: `tests/test_ui_specs.py`
- Create: `wage_clock/ui_specs.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ui_specs.py`:

```python
import unittest

from wage_clock.ui_specs import ACTION_BUTTONS, COLORS, compact_status_text


class UiSpecsTest(unittest.TestCase):
    def test_action_buttons_keep_approved_order_and_icons(self):
        self.assertEqual(
            [(item.key, item.label, item.icon) for item in ACTION_BUTTONS],
            [
                ("settings", "设置", "⚙"),
                ("calendar", "日历", "□"),
                ("hide", "隐藏", "−"),
                ("history", "记录", "≡"),
            ],
        )

    def test_compact_status_text_shortens_verbose_runtime_status(self):
        self.assertEqual(compact_status_text("工作时间中，工资正在增长"), "工作中")
        self.assertEqual(compact_status_text("午休中，工资暂停增长"), "午休中")
        self.assertEqual(compact_status_text("还没到上班时间"), "未开始")
        self.assertEqual(compact_status_text("今天工作时间已结束"), "已结束")
        self.assertEqual(compact_status_text("今天不是工作日，工资不增长"), "休息日")

    def test_compact_status_text_has_safe_fallback(self):
        self.assertEqual(compact_status_text("自定义状态"), "自定义状态")

    def test_required_monochrome_tokens_exist(self):
        self.assertEqual(COLORS["background"], "#f8f8f6")
        self.assertEqual(COLORS["ink"], "#171717")
        self.assertEqual(COLORS["surface"], "#ffffff")
        self.assertEqual(COLORS["muted"], "#6d6d68")
        self.assertEqual(COLORS["border"], "#deded8")
        self.assertEqual(COLORS["inverse_text"], "#f7f7f2")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python -m unittest tests.test_ui_specs -v
```

Expected: FAIL or ERROR because `wage_clock.ui_specs` does not exist.

- [ ] **Step 3: Add the minimal pure UI metadata**

Create `wage_clock/ui_specs.py`:

```python
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
```

- [ ] **Step 4: Run the tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_ui_specs -v
```

Expected: PASS.

### Task 2: Theme Tokens And ttk Styles

**Files:**
- Modify: `wage_clock/theme.py`

- [ ] **Step 1: Replace theme constants with `COLORS` imports**

Update `theme.py` to import `COLORS` from `wage_clock.ui_specs`.

- [ ] **Step 2: Configure monochrome ttk styles**

Implement styles:

```python
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
    style.configure("TButton", padding=(8, 5), font=("Microsoft YaHei UI", 9), background=SURFACE, foreground=TEXT, bordercolor=BORDER)
    style.configure("Primary.TButton", padding=(8, 5), font=("Microsoft YaHei UI", 9), background=TEXT, foreground=COLORS["inverse_text"], bordercolor=TEXT)
    style.map("Primary.TButton", background=[("active", "#2a2a2a")], foreground=[("active", COLORS["inverse_text"])])
    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
    style.configure("TRadiobutton", background=BACKGROUND, foreground=TEXT)
    style.configure("TCheckbutton", background=BACKGROUND, foreground=TEXT)
    style.configure("Horizontal.TProgressbar", troughcolor="#e6e6df", background=TEXT, bordercolor="#e6e6df", lightcolor=TEXT, darkcolor=TEXT)
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, foreground=TEXT, rowheight=26, bordercolor=BORDER)
    style.configure("Treeview.Heading", background="#eeeeea", foreground=TEXT, font=("Microsoft YaHei UI", 9, "bold"))
    style.configure("TLabelframe", background=BACKGROUND, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BACKGROUND, foreground=TEXT)
```

- [ ] **Step 3: Run the UI spec tests**

Run:

```powershell
python -m unittest tests.test_ui_specs -v
```

Expected: PASS.

### Task 3: Main Window Dashboard Layout

**Files:**
- Modify: `wage_clock/app.py`

- [ ] **Step 1: Import UI specs**

Add:

```python
from .ui_specs import ACTION_BUTTONS, COLORS, compact_status_text
```

- [ ] **Step 2: Rebuild `_build_ui()` as compact dashboard**

Replace the old stack layout with:

- root `ttk.Frame(self, padding=14)`
- a thin top line title
- dark hero area using `tk.Frame` with `COLORS["ink"]`
- two metric cards using `tk.Frame` with white backgrounds and border highlight
- progress card
- four action buttons from `ACTION_BUTTONS`

Use button command mapping:

```python
commands = {
    "settings": self.open_settings,
    "calendar": self.open_calendar,
    "hide": self.hide_to_tray,
    "history": self.show_history,
}
```

Button labels should be `f"{spec.icon} {spec.label}"`, with `Primary.TButton` only for settings.

- [ ] **Step 3: Keep widget references used by `_tick()`**

Ensure these instance attributes still exist:

```python
self.progress
self.status_var
self.today_var
self.month_var
self.rate_var
self.progress_var
self.baseline_var
```

- [ ] **Step 4: Compact runtime status in `_tick()`**

In initialized state, compute:

```python
status = status_for(now)
self.status_var.set(compact_status_text(status))
```

Keep the uninitialized state readable:

```python
self.status_var.set("待设置")
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m unittest tests.test_ui_specs -v
```

Expected: PASS.

### Task 4: Dialog Style Alignment

**Files:**
- Modify: `wage_clock/settings_dialog.py`
- Modify: `wage_clock/calendar_dialog.py`
- Modify: `wage_clock/app.py`

- [ ] **Step 1: Settings dialog primary action**

Set the save button style:

```python
ttk.Button(actions, text="保存开始", style="Primary.TButton", command=self._save)
```

Keep existing validation and save behavior unchanged.

- [ ] **Step 2: Calendar monochrome work/rest colors**

Import `COLORS` in `calendar_dialog.py`:

```python
from .ui_specs import COLORS
```

Use:

```python
bg = COLORS["work_day"] if is_work else COLORS["rest_day"]
fg = COLORS["ink"] if is_work else COLORS["muted"]
if not in_month:
    bg = COLORS["background"]
    fg = "#b8b8b2"
```

Update legend text to:

```python
ttk.Label(legend, text="深色：需要上班").pack(side="left")
ttk.Label(legend, text="  浅色：休息/法定假日").pack(side="left")
```

- [ ] **Step 3: History window title and Treeview spacing**

In `show_history()`, keep table columns and add a title label above the table:

```python
ttk.Label(frame, text="工资记录", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m unittest tests.test_ui_specs -v
```

Expected: PASS.

### Task 5: Runtime Verification

**Files:**
- No planned code changes unless verification exposes layout defects.

- [ ] **Step 1: Run syntax compilation**

Run:

```powershell
python -m compileall salary_clock.py wage_clock
```

Expected: all relevant `.py` files compile successfully.

- [ ] **Step 2: Run automated tests**

Run:

```powershell
python -m unittest discover -v
```

Expected: PASS.

- [ ] **Step 3: Launch app smoke test**

Run:

```powershell
python salary_clock.py
```

Expected: app opens with a 430x430 compact dashboard. Close using tray menu or app close behavior after visual inspection.

- [ ] **Step 4: Visual checklist**

Confirm:

- Main window remains compact.
- Dark hero area shows today amount and short status.
- Two metric cards show cumulative pay and per-second rate.
- Progress card fits without clipping.
- Four buttons show icon plus text.
- Settings, calendar, hide, and history open or act as before.

### Self-Review Notes

- Spec coverage: main dashboard, black-and-white palette, small window, icon buttons, dialog alignment, and verification are all covered.
- No placeholders: this plan contains concrete paths, commands, and expected outcomes.
- Type consistency: `ActionButtonSpec`, `ACTION_BUTTONS`, `COLORS`, and `compact_status_text()` are introduced in Task 1 and reused in later tasks.
