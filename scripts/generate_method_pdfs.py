"""Generate per-paper experimental route and methods briefing PDFs."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "papers.json"
OUTPUT = ROOT / "downloads"
WINDOWS_FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
LINUX_FONT = Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
FONT = WINDOWS_FONT if WINDOWS_FONT.exists() else LINUX_FONT

ROUTES = {
    "10.1038/s42255-025-01378-8": {
        "question": "HMGCS2 依赖的酮体信号如何驱动米色脂肪生成与产热？",
        "route": "Hmgcs2 遗传干预 → β-羟丁酸变化 → Cd81+ 前体与米色分化 → 组蛋白乙酰化/β-羟丁酰化 → 产热表型",
        "modules": [
            "动物层面：Hmgcs2 缺失或增强酮体生成模型；冷刺激后检测能量消耗、核心体温、iWAT/BAT UCP1。",
            "细胞层面：分离脂肪 SVF，流式定量 Cd81+ 前体，进行米色分化；Hmgcs2 敲低/过表达 ± β-羟丁酸补救。",
            "机制层面：检测全局 H3K9bhb/H3K27ac，并对 Ucp1、Ppargc1a 等位点实施 ChIP-qPCR；Seahorse 测 OCR。",
        ],
        "controls": "同窝对照、配对摄食、相同发育时间点；区分 β-羟丁酸信号作用与作为能量底物的作用。",
        "decision": "Hmgcs2 操作引起酮体、表观修饰及产热读出方向一致，且 β-羟丁酸补救可逆转缺失表型。",
    },
    "41620670": {
        "question": "哪些 LONP1 下游通路最适合迁移到脂肪产热或 PCOS？",
        "route": "综述证据分层 → 候选底物/通路优选 → 脂肪细胞与卵巢细胞小规模筛选 → 机制验证",
        "modules": [
            "建立 LONP1 下游候选清单：线粒体蛋白质量控制、ROS、OXPHOS、应激反应和类固醇生成。",
            "在米色脂肪细胞与卵巢膜细胞中实施 LONP1 siRNA/过表达，检测线粒体呼吸、膜电位、ROS 和细胞特异终点。",
            "用蛋白半衰期、共免疫沉淀及线粒体蛋白组筛选直接底物。",
        ],
        "controls": "至少使用两条独立 siRNA，并以回补实验排除脱靶；区分蛋白表达变化和蛋白降解变化。",
        "decision": "优先保留在两种细胞中均改变线粒体稳态，或在单一组织中强烈改变疾病核心终点的通路。",
    },
    "38870290": {
        "question": "青蒿素通过 LONP1-CYP11A1 互作降低 PCOS 高雄激素的因果链是否可复现？",
        "route": "青蒿素处理 → LONP1-CYP11A1 互作增强 → CYP11A1 降解 → 雄激素下降 → PCOS 表型改善",
        "modules": [
            "卵巢膜细胞：青蒿素剂量与时间梯度；检测 LONP1、CYP11A1、STAR、睾酮/雄烯二酮。",
            "机制验证：LONP1-CYP11A1 共免疫沉淀；CHX chase 测 CYP11A1 半衰期；LONP1 敲低后观察青蒿素效应是否消失。",
            "动物验证：DHEA 或来曲唑 PCOS 模型，检测动情周期、排卵、卵巢形态、血清雄激素和代谢表型。",
        ],
        "controls": "载体对照、LONP1 敲低/回补、蛋白酶体与线粒体蛋白酶相关抑制对照；盲法评价卵巢形态。",
        "decision": "只有 LONP1 缺失可显著消除青蒿素对 CYP11A1 周转和雄激素的作用，才支持轴依赖机制。",
    },
    "39648053": {
        "question": "LONP1 在卵巢不同细胞类型与 PCOS/衰老阶段中的作用是什么？",
        "route": "卵巢细胞类型定位 → PCOS/衰老分层 → LONP1 功能干预 → 类固醇生成与卵母细胞质量终点",
        "modules": [
            "组织定位：免疫荧光共染膜细胞、颗粒细胞和卵母细胞标记，比较 PCOS、年龄与周期阶段。",
            "细胞功能：各细胞类型实施 LONP1 敲低/过表达，检测线粒体呼吸、ROS、类固醇生成与细胞生存。",
            "整合单细胞转录组或空间转录组，确定 LONP1 变化最显著的细胞群和关联通路。",
        ],
        "controls": "动情周期匹配、年龄匹配；使用细胞类型特异标记；验证抗体特异性。",
        "decision": "选择 LONP1 变化最大且与疾病核心终点有剂量关系的细胞类型进入条件性遗传模型。",
    },
    "PPR863667": {
        "question": "循环 BMP8B 能否作为 PCOS 代谢分型或产热能力的生物标志物？",
        "route": "临床队列分层 → BMP8B 定量 → 代谢/雄激素/产热代理指标相关 → 多变量预测模型",
        "modules": [
            "招募 PCOS 与年龄/BMI 匹配对照；记录表型、用药、周期、胰岛素抵抗、血脂和雄激素。",
            "采用经验证 ELISA 重复检测血清 BMP8B；随机抽样进行批内与批间重复。",
            "条件允许时加入冷刺激前后 BMP8B、红外热成像或 BAT 相关指标，评估与产热能力的关系。",
        ],
        "controls": "采血时间、空腹状态、月经周期与药物控制；BMI 与胰岛素抵抗作为核心混杂因素。",
        "decision": "BMP8B 在多变量模型中仍与 PCOS 或代谢亚型独立相关，且效应量具备临床区分价值。",
    },
    "41696866": {
        "question": "运动是否通过恢复卵巢 LONP1 蛋白稳态改善 PCOS？",
        "route": "PCOS + 运动 → 卵巢 LONP1 恢复 → 类固醇生成蛋白周转 → 炎症/纤维化/高雄激素下降",
        "modules": [
            "DHEA-PCOS 小鼠设置静息与有氧运动组，记录运动量与体重；检测卵巢和代谢表型。",
            "检测 LONP1、STAR、CYP11A1 蛋白与半衰期，线粒体呼吸、ROS、炎症和纤维化指标。",
            "在运动组加入卵巢 LONP1 敲低，判断运动保护是否依赖 LONP1。",
        ],
        "controls": "非 PCOS 运动组、配对处理组；区分体重下降与运动本身效应；统一取材周期。",
        "decision": "LONP1 敲低若显著削弱运动对高雄激素及卵巢病理的改善，支持因果介导。",
    },
    "PMC12628819": {
        "question": "AKT-LONP1-STAR 轴如何驱动卵巢膜细胞高雄激素？",
        "route": "AKT 活性下降 → LONP1 下降 → STAR 稳定/积累 → 线粒体胆固醇输入增加 → 雄激素上升",
        "modules": [
            "膜细胞中操控 AKT 活性，检测 LONP1 转录/蛋白、STAR 半衰期和雄激素分泌。",
            "实施 LONP1 回补和 STAR 敲低的遗传互作实验，判断上下游顺序。",
            "用共免疫沉淀、线粒体定位和蛋白降解实验验证 LONP1-STAR 关系。",
        ],
        "controls": "AKT 抑制剂与遗传抑制双重验证；LONP1 催化失活突变回补；非膜细胞对照。",
        "decision": "LONP1 回补可逆转 AKT 抑制导致的 STAR 积累与雄激素上升，支持完整因果轴。",
    },
    "40181907": {
        "question": "BMP8B 是否通过雌性下丘脑葡萄糖感知调控交感神经与脂肪产热？",
        "route": "中枢 BMP8B → VMH 葡萄糖抑制神经元敏感性 → 交感输出 → BAT/iWAT 产热",
        "modules": [
            "雌性小鼠 VMH 神经元电生理或钙成像，给予 BMP8B 并改变葡萄糖浓度。",
            "中枢 BMP8B 干预后检测交感神经活性、BAT/iWAT UCP1、冷耐受和能量消耗。",
            "在 PCOS 模型中重复实验，判断高雄激素是否破坏 BMP8B 中枢响应。",
        ],
        "controls": "雄性对照、雌性周期分层、非 VMH 区域对照、AMPK 通路阻断。",
        "decision": "BMP8B 对神经元与产热表型的效应需具有性别/区域特异性，并可被通路阻断。",
    },
    "PMC12024584": {
        "question": "哪些 LONP1 小分子最适合用于 PCOS 与脂肪产热的功能筛选？",
        "route": "化合物优选 → LONP1 活性与毒性筛选 → 脂肪细胞/膜细胞功能验证 → 命中物机制确认",
        "modules": [
            "按激活/抑制机制和可获得性建立小规模化合物库；先测细胞活力、LONP1 活性和线粒体稳态。",
            "米色脂肪细胞检测 UCP1、OCR；膜细胞检测 STAR/CYP11A1 与雄激素。",
            "对命中物实施 LONP1 敲低或催化失活回补，验证作用是否靶点依赖。",
        ],
        "controls": "溶剂、阳性/阴性化合物、剂量梯度和时间梯度；排除广泛线粒体毒性。",
        "decision": "保留治疗窗明确、可改善细胞特异终点且 LONP1 敲低后效应消失的化合物。",
    },
}


def make_styles():
    pdfmetrics.registerFont(TTFont("CN", str(FONT), subfontIndex=0))
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "CN"
    styles.add(ParagraphStyle(name="CNTitle", parent=styles["Title"], fontName="CN", fontSize=18, leading=26, textColor=colors.HexColor("#174d38")))
    styles.add(ParagraphStyle(name="CNHead", parent=styles["Heading2"], fontName="CN", fontSize=12, leading=18, textColor=colors.HexColor("#287355"), spaceBefore=10, spaceAfter=5))
    styles.add(ParagraphStyle(name="CNBody", parent=styles["BodyText"], fontName="CN", fontSize=9.5, leading=16, textColor=colors.HexColor("#263c32")))
    styles.add(ParagraphStyle(name="CNSmall", parent=styles["BodyText"], fontName="CN", fontSize=8, leading=13, textColor=colors.HexColor("#66756e")))
    return styles


def build_pdf(paper: dict, route: dict, styles) -> None:
    output = OUTPUT / f"{paper['id'].replace('/', '_')}-methods.pdf"
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=17 * mm, bottomMargin=17 * mm)
    story = [
        Paragraph("实验路线与方法简报", styles["CNTitle"]),
        Paragraph(paper["title"], styles["CNHead"]),
        Paragraph(f"靶点：{' / '.join(paper['genes'])}　|　期刊：{paper['journal']}　|　来源：{paper['url']}", styles["CNSmall"]),
        Spacer(1, 8),
        Paragraph("使用说明", styles["CNHead"]),
        Paragraph("本文件基于公开题录、摘要及网站文献综合生成，用于课题设计和复现实验规划；不是论文原始 Methods 或补充材料。正式实施前应阅读全文、补充伦理审批，并根据预实验进行功效分析。", styles["CNBody"]),
        Paragraph("核心研究问题", styles["CNHead"]),
        Paragraph(route["question"], styles["CNBody"]),
        Paragraph("实验路线图", styles["CNHead"]),
        Paragraph(route["route"], styles["CNBody"]),
        Paragraph("关键实验模块", styles["CNHead"]),
    ]
    for i, module in enumerate(route["modules"], 1):
        story.append(Paragraph(f"{i}. {module}", styles["CNBody"]))
        story.append(Spacer(1, 4))
    story += [
        Paragraph("必要对照与质量控制", styles["CNHead"]),
        Paragraph(route["controls"], styles["CNBody"]),
        Paragraph("结果判定标准", styles["CNHead"]),
        Paragraph(route["decision"], styles["CNBody"]),
        Paragraph("建议通用检测面板", styles["CNHead"]),
        Table(
            [
                ["层面", "建议指标"],
                ["靶点/机制", "目标蛋白、酶活、蛋白半衰期、互作、亚细胞定位"],
                ["线粒体", "OCR、膜电位、ROS、OXPHOS、线粒体形态与质量控制"],
                ["产热", "UCP1、PGC1α、CIDEA、冷耐受、间接量热"],
                ["PCOS", "睾酮、LH/FSH、动情周期、排卵、卵巢形态、GTT/ITT"],
            ],
            colWidths=[30 * mm, 130 * mm],
            style=TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "CN"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#287355")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cdd8d1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEADING", (0, 0), (-1, -1), 13),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5f0")]),
            ]),
        ),
        Spacer(1, 10),
        Paragraph(f"生成日期：2026-06-07　|　原文直达：{paper['url']}", styles["CNSmall"]),
    ]
    doc.build(story)


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    papers = json.loads(DATA.read_text(encoding="utf-8"))["papers"]
    styles = make_styles()
    for paper in papers:
        route = ROUTES.get(str(paper["id"]))
        if route:
            build_pdf(paper, route, styles)
    print(f"Generated {len(list(OUTPUT.glob('*.pdf')))} method PDFs.")


if __name__ == "__main__":
    main()
