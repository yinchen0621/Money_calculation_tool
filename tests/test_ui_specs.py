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
