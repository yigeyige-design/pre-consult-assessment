"""中文报告片段生成。

作用：把 ScoreResult 渲染成可直接贴进《老年综合评估报告》的文本片段。
只做文案与排版，不计算分值、不判断阈值（阈值判断在 engine / scales 中完成）。
"""

from __future__ import annotations

from datetime import datetime

from app import __version__
from app.models import ScoreResult
from app.scales import get_scale

TITLE = "【老年人预问诊量表评估报告（片段）】"
SEPARATOR = "────────────────────────────────"
COMPLIANCE_TAIL = "本报告为评估提示，不作为诊断依据；具体处置请医师结合临床确认。"


def render_report(
    result: ScoreResult,
    subject: str = "张三（演示数据）",
    evaluated_at: datetime | None = None,
) -> str:
    """渲染报告片段
    作用：输出含元信息、总分分级、分项得分与合规说明的中文文本;
    Args:
        - result: 计分结果;
        - subject: 评估对象描述，默认使用虚构演示对象;
        - evaluated_at: 评估时间，缺省取当前时间;
    Return:
        - str: 多行中文报告文本;
    """
    moment = evaluated_at if evaluated_at is not None else datetime.now()
    scale = get_scale(result.scale_code)
    lines = [
        TITLE,
        SEPARATOR,
        f"量表：{result.scale_name}",
        f"标准来源：{result.standard_ref}",
        f"评估对象：{subject}",
        f"评估时间：{moment.strftime('%Y年%m月%d日 %H:%M')}",
        "",
        "一、总分与分级",
        f"总分：{result.total} / {result.max_total} 分",
        f"分级：{result.level_label}",
        f"说明：{result.advice}",
        "",
        "二、分项得分",
    ]
    for index, item in enumerate(scale.items, start=1):
        score_value = result.item_scores.get(item.code)
        label = result.item_labels.get(item.code, "")
        item_max = max(option.score for option in item.options)
        lines.append(f"  {index}. {item.label}：{score_value} / {item_max} 分（{label}）")
    lines.extend(
        [
            "",
            "三、说明",
            COMPLIANCE_TAIL,
            f"生成工具：量表评估系统 v{__version__}",
        ]
    )
    return "\n".join(lines)
