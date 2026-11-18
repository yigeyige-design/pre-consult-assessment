"""报告片段测试：必备字段、条目齐全、措辞合规。"""

import unittest
from datetime import datetime

from app.engine import score
from app.models import Answer
from app.report import render_report
from app.scales import DEMO_ANSWERS

FORBIDDEN_PHRASES = ("确诊", "诊断为", "停药", "调整用药")


def demo_result():
    """用演示数据生成计分结果"""
    answers = [Answer(item_code=item, option_code=option) for item, option in DEMO_ANSWERS["adl"].items()]
    return score("adl", answers)


class TestReportContent(unittest.TestCase):
    """报告内容完整性"""

    def setUp(self):
        self.text = render_report(demo_result(), evaluated_at=datetime(2026, 10, 21, 9, 30))

    def test_contains_headline_fields(self):
        for keyword in ("总分：", "分级：", "标准来源：", "评估对象：", "评估时间："):
            self.assertIn(keyword, self.text)

    def test_contains_score_and_level(self):
        self.assertIn("85 / 100", self.text)
        self.assertIn("轻度依赖", self.text)

    def test_contains_every_item_label(self):
        labels = (
            "进食",
            "洗澡",
            "修饰（洗脸、刷牙、梳头）",
            "穿衣",
            "大便控制",
            "小便控制",
            "如厕",
            "床椅转移",
            "平地行走",
            "上下楼梯",
        )
        for label in labels:
            self.assertIn(label, self.text)

    def test_contains_compliance_tail(self):
        self.assertIn("不作为诊断依据", self.text)
        self.assertIn("请医师结合临床确认", self.text)

    def test_item_lines_show_item_max(self):
        """分项得分行同时给出该条目满分，便于核对权重"""
        self.assertIn("进食：10 / 10 分", self.text)
        self.assertIn("洗澡：5 / 5 分", self.text)

    def test_default_subject_is_fake(self):
        text = render_report(demo_result())
        self.assertIn("演示数据", text)

    def test_time_is_rendered(self):
        self.assertIn("2026年10月21日", self.text)

    def test_contains_generator_line(self):
        """尾注需标明生成工具与版本，便于报告追溯"""
        self.assertIn("生成工具：量表评估系统 v", self.text)


class TestReportCompliance(unittest.TestCase):
    """合规：不得出现结论性、处方性措辞"""

    def test_no_forbidden_phrases(self):
        for subject in ("张三（演示数据）", "李四（演示数据）"):
            text = render_report(demo_result(), subject=subject)
            for phrase in FORBIDDEN_PHRASES:
                self.assertNotIn(phrase, text, f"报告中出现禁用词：{phrase}")

    def test_all_levels_are_compliant(self):
        """四种分级生成的报告都不得含禁用词"""
        from app.models import Level
        from app.scales import ADL

        for level in ADL.levels:
            self.assertNotIn("确诊", level.advice)
            self.assertNotIn("诊断为", level.advice)
            self.assertNotIn("停药", level.advice)
            self.assertNotIn("调整用药", level.advice)
            self.assertIsInstance(level, Level)


if __name__ == "__main__":
    unittest.main()
