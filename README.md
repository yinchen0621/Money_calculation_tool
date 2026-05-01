# 工资时钟

一个 Windows 桌面小窗，用来按工作时间实时计算工资变化。

## 已包含功能

- 支持月薪、日薪、时薪三种模式。
- 工作日按中国大陆常见作息计算：08:30-18:00。
- 午休 11:45-13:30 自动扣除，期间工资暂停增长。
- 每 1 秒刷新一次。
- 首次启动会先询问工资类型、金额、已上班天数、当前累计工资。
- 点击“开始计价”后，才会从当前累计工资继续实时增长。
- 显示今日重新计算工资、累计工资、当前每秒工资、今日有效工时进度。
- 主界面只展示计价信息，工资参数都放在“设置”弹窗里。
- 内置 2026 年国务院办公厅节假日/调休安排，本地判断工作日。
- 设置里可以查看当月日历，红色日期表示需要上班。
- 本地保存历史记录。
- 支持开机自启开关。

> 当前“工作日”按周一到周五计算，暂未接入中国法定节假日和调休表。

## 运行

需要 Windows 自带/已安装的 Python 3。

```powershell
python salary_clock.py
```

也可以双击：

```text
run_salary_clock.bat
```

配置和历史记录会保存在：

```text
%APPDATA%\SalaryClock\config.json
%APPDATA%\SalaryClock\history.json
```

## 后续可增强

- 打包成 `.exe`。
- 加右下角托盘图标。
- 支持法定节假日和调休。
- 支持加班工资规则。
- 支持窗口置顶、透明度和主题皮肤。

## 代码结构

```text
salary_clock.py              启动入口
wage_clock/app.py            主窗口
wage_clock/settings_dialog.py 设置弹窗
wage_clock/calendar_dialog.py 当月日历界面
wage_clock/core.py           工资和工时计算
wage_clock/holiday_calendar.py 本地节假日/调休规则
wage_clock/storage.py        配置和历史记录
wage_clock/theme.py          UI 样式
wage_clock/autostart.py      Windows 开机自启
```

后续美化主要改 `wage_clock/theme.py` 和 `wage_clock/app.py`，计算逻辑不用动。
