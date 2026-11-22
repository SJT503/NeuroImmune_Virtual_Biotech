#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════
 顶刊清爽制图、五维数据深度与已发表竞品对标硬门禁 (figure_clean_aesthetic_gate.py)
 适用于所有科研项目的 Python 绘图脚本（单脚本多图或多脚本套件 fig1..figN）与产出图片终检。

 核心十条硬门禁 + 跨轮次锁定图与投稿包防覆盖保护锁：
   1. 【只对标已发表同类型顶刊/目标期刊论文锁】
   2. 【图内零大段解释性文本框锁 (Zero Prose-Box Clutter)】
   3. 【图注与数据区 100% 零重叠锁 (扩轴留白 + frameon=False)】
   4. 【散点/象限/火山图就近微距防重叠锁 (禁跨象限右侧梳子超长引线 & 禁半边空置 X 轴模板复刻)】
   5. 【内嵌色标条 (inset_axes) 底边距安全锁 (y >= 0.10)】
   6. 【机制图/假说图/标书路线图 BioRender 顶刊标准锁 (禁 FancyBboxPatch/SVG 伪机制图)】
   7. 【按需有机面板数与非对称主焦点构图锁 (兼容单脚本多函数与多脚本套件聚合审计!)】
   8. 【图表语汇多样性与反柱状图 (<=12%(湿实验<=35%) 独立面板) / 反横向线条图 (<=20%) 双重垄断锁 + >=6 类视觉形态】
   9. 【三层数据深度、自有重算增量锁 (禁纯重绘外部附表 X-Y) & 纯干实验路线禁未做湿实验功效诱饵面板锁 (如 IHC-Fr Power)】
  10. 【文图语言 100% 协同、零代码变量/裸代号、零外部期刊名/Official/Published 面板标题伪版权污染锁 + submission/ 禁覆盖锁】

 用法：
   python ~/.claude/scripts/figure_clean_aesthetic_gate.py <script_or_dir...> [--images <img_dir_or_files...>] [--state manuscript/MANUSCRIPT_STATE.json] [--allow-schematic] [--single-figure]
════════════════════════════════════════════════════════════════════════════
"""
import argparse
import ast
import dataclasses
import json
import pathlib
import re
import sys
from typing import Dict, List, Optional, Set, Tuple

NARRATIVE_VERBS_RE = re.compile(
    r"\b(?:confirms?|indicates?|demonstrates?|suggests?|validates?|reveals?|"
    r"shows?\s+that|consistent\s+with|eliminat(?:es|ing)|preserv(?:es|ing)|"
    r"supports?\s+the|establishes?|highlights?)\b",
    re.IGNORECASE,
)

STAT_TOKEN_RE = re.compile(
    r"(?:\b(?:r|rho|R2|R\^2|P|p|q|FDR|AUC|AUROC|OR|HR|NES|n|N|FC|log2FC|Slope|r_s|NNT|ARR)\s*[=<>≈≤≥:]|"
    r"\*{1,4}|\bns\b|±|\bSD\b|\bSEM\b|\bCI\b)",
    re.IGNORECASE,
)

FORBIDDEN_LABEL_CIPHER_RE = re.compile(
    r"(?:"
    r"\bWTSSNH2Y\b|\bPAXHWEAR\b|\bPAXHQFM\b|\bSSSNFL_H\b|"
    r"\bM[1-7]\b(?:\s+(?:Persistence|Mixed|LightGBM|Neural|Uncens|Uncoupled|Psych))|"
    r"\bM[1-7]_[A-Za-z0-9_]+\b|"
    r"\bR[0-7]\b(?:\s+(?:Natural|Sleep|Sensory|Dual|Vascular|Social|Multi|Half|Twin|Anti|\())|"
    r"\bR[0-7]_[A-Za-z0-9_]+\b|"
    r"\bArm\s+[A-D]\b|"
    r"\bSplit\s*[AB]\d*\b|"
    r"\b(?:tr20|imrc|dlrc|ser7|cesd10|phq8_nosleep|fpca_mims_pc\d|fpca_lux_pc\d)\b"
    r")"
)

FORBIDDEN_TITLE_CITATION_OR_OFFICIAL_RE = re.compile(
    r"(?:"
    r"\b(?:Nature|Science|Cell|Lancet|NEJM|JAMA|Neuron|Immunity|BMJ)\s+(?:19|20)\d{2}\b|"
    r"\bNat\.?\s+(?:Commun|Med|Neurosci|Genet|Methods|Biotechnol|Immunol|Aging|Mach)\s+(?:19|20)\d{2}\b|"
    r"\bOfficial\s+(?:DEGs?|Benchmarks?|DESeq2|GSEA|Results?|Tables?|Stats?|CC|Parity)\b|"
    r"\bOfficial\b.*\b(?:DEGs?|Benchmark|Parity|DESeq2|GSEA)\b|"
    r"^\s*Published\s+"
    r")",
    re.IGNORECASE,
)

FORBIDDEN_AXIS_PUBLISHED_RE = re.compile(
    r"(?:^\s*Published\s+|\bPublished\s+(?:Single[- ]Nucleus|Single[- ]Cell|CC|Bulk|DESeq2|limma|edgeR|MAST|Seurat|GSEA|log2\s*FC|Fold[- ]Change|FDR|P[- ]?value)\b)",
    re.IGNORECASE,
)

DRYLAB_WETLAB_BAIT_LABEL_RE = re.compile(
    r"(?:"
    r"\bIHC-Fr\b|"
    r"\b(?:IHC(?:-Fr|-P)?|mIF|Immunofluorescence|Western\s+Blot|WB|RT-qPCR|qPCR|ELISA|RNAScope|TUNEL)\s+"
    r"(?:Power|Sample\s+Size|Blueprint|50-um\s+Ring\s+Benchmark|Ring\s+Benchmark|Prospective\s+Plan)\b"
    r")",
    re.IGNORECASE,
)

RIGHT_COMB_HELPER_NAMES = {
    "radial_right_fanout_labels",
    "annotate_volcano_right_gutter",
    "right_gutter_fanout_labels",
    "right_margin_fanout_labels",
    "_place_right_margin_labels",
    "place_right_margin_labels",
}

VISIBLE_LABEL_FUNCS = {
    "set_title",
    "set_xlabel",
    "set_ylabel",
    "set_xticklabels",
    "set_yticklabels",
    "suptitle",
    "text",
    "annotate",
    "figtext",
}

PLOT_PRIMITIVE_FAMILIES: Dict[str, str] = {
    "bar": "bar_chart",
    "barh": "bar_chart",
    "fill_between": "ribbon_band",
    "fill_betweenx": "ribbon_band",
    "errorbar": "forest_or_ci",
    "violinplot": "violin_or_box",
    "boxplot": "violin_or_box",
    "hist": "histogram_or_density",
    "kdeplot": "histogram_or_density",
    "contourf": "surface_or_heatmap",
    "contour": "surface_or_heatmap",
    "imshow": "surface_or_heatmap",
    "pcolormesh": "surface_or_heatmap",
    "hexbin": "surface_or_heatmap",
    "matshow": "surface_or_heatmap",
    "heatmap": "surface_or_heatmap",
    "streamplot": "vector_or_stream_field",
    "quiver": "vector_or_stream_field",
    "scatter": "scatter_or_bubble",
    "plot": "curve_or_trajectory",
    "step": "curve_or_trajectory",
    "ecdf": "curve_or_trajectory",
}

MAIN_FIG_FUNC_RE = re.compile(
    r"^(?:build_fig|plot_fig|make_fig|render_fig|fig|build_extended_data_fig|build_ed_fig|build_supp_fig|plot_supp_fig)_?\d+",
    re.IGNORECASE,
)
SUPP_SCRIPT_NAME_RE = re.compile(r"(?:^unused_never_skip_supp$)", re.IGNORECASE)
RASTER_IMG_VAR_RE = re.compile(
    r"(?:im_ban|im_crop|sub_img|banner|biorender|illust|schematic|pil_img|img_arr|im7)",
    re.IGNORECASE,
)
HELPER_SCRIPT_NAME_RE = re.compile(r"^(?:visual_tokens|utils|helpers|common|style_tokens|__init__)\.py$", re.IGNORECASE)


@dataclasses.dataclass
class FigureUnitMetrics:
    unit_name: str
    n_panels: int
    has_asymmetry: bool
    primitives: Set[str]
    bar_axes_count: int
    horiz_axes_count: int
    naked_stick_axes: List[str] = dataclasses.field(default_factory=list)
    nominal_zigzag_axes: List[str] = dataclasses.field(default_factory=list)
    violin_box_axes_count: int = 0
    multilayer_axes_count: int = 0
    total_data_axes_count: int = 0


def _strip_latex_math(s: str) -> str:
    return re.sub(r"\$[^\$]*\$", " ", s)


def _extract_const_strings(node: ast.AST) -> List[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        segs = [v.value for v in node.values if isinstance(v, ast.Constant) and isinstance(v.value, str)]
        return [" ".join(segs)] if segs else []
    if isinstance(node, (ast.List, ast.Tuple)):
        out: List[str] = []
        for elt in node.elts:
            out.extend(_extract_const_strings(elt))
        return out
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _extract_const_strings(node.left) + _extract_const_strings(node.right)
    return []


def _audit_visible_label_string(
    s: str,
    path: pathlib.Path,
    lineno: int,
    func_name: str,
    errors: List[str],
    allow_wetlab: bool = False,
) -> None:
    clean_s = s.strip()
    if not clean_s:
        return
    if "/" in clean_s and clean_s.endswith((".csv", ".json", ".parquet", ".tsv", ".npz", ".rds")):
        return
    m_ciph = FORBIDDEN_LABEL_CIPHER_RE.search(clean_s)
    if m_ciph:
        errors.append(
            f"[{path.name}:L{lineno}] 违禁图面内部代号/代码缩写泄露 ({func_name} -> {m_ciph.group(0)!r}): "
            f"{clean_s!r} → 图面必须使用与正文一致的自然临床/科学术语 (Rule 10)"
        )
        return
    if func_name in ("set_title", "suptitle"):
        m_off = FORBIDDEN_TITLE_CITATION_OR_OFFICIAL_RE.search(clean_s)
        if m_off:
            errors.append(
                f"[{path.name}:L{lineno}] 违禁面板标题出现外部期刊名/年份或 'Official/Published' ({func_name} -> {m_off.group(0)!r}): "
                f"{clean_s!r} → 极易造成第三方盗图/版权误判且违背顶刊命名惯例！面板标题仅限写队列/生物学对象与分析维度，文献归属一律写进 Figure Legend (Rule 10)"
            )
            return
    if func_name in ("set_xlabel", "set_ylabel", "set_title"):
        m_pub = FORBIDDEN_AXIS_PUBLISHED_RE.search(clean_s)
        if m_pub:
            errors.append(
                f"[{path.name}:L{lineno}] 违禁坐标轴/标题直接写 'Published ...' ({func_name} -> {m_pub.group(0)!r}): "
                f"{clean_s!r} → 坐标轴请用规范科学统计量或 'Reference ... (<Accession>)'，并在另一轴展示本研究供体/动物级重算结果形成交叉验证，出处归入 Figure Legend (Rule 9/10)"
            )
            return
    if not allow_wetlab:
        m_wl = DRYLAB_WETLAB_BAIT_LABEL_RE.search(clean_s)
        if m_wl:
            errors.append(
                f"[{path.name}:L{lineno}] 纯干实验稿件违禁出现未执行湿实验诱饵面板标签 ({func_name} -> {m_wl.group(0)!r}): "
                f"{clean_s!r} → 纯计算稿件严禁将未执行的 IHC-Fr/mIF/WB 样本量功效曲线或湿实验计划画进主/附图（极易招致审稿人索要湿实验；确有真实湿实验请设 MANUSCRIPT_STATE has_wetlab_experiments=true 或传 --allow-wetlab）(Rule 9)"
            )
            return
    no_math = _strip_latex_math(clean_s)
    for tok in re.findall(r"\b[a-z]{2,}_[a-z0-9_]{2,}\b", no_math):
        if tok not in {
            "sans_serif",
            "tight_layout",
            "upper_left",
            "upper_right",
            "lower_left",
            "lower_right",
            "center_left",
            "center_right",
        }:
            errors.append(
                f"[{path.name}:L{lineno}] 违禁图面 snake_case 代码字段名泄露 ({func_name} -> {tok!r}): "
                f"{clean_s!r} → 严禁将代码变量名直接印在坐标轴/标题/图例上 (Rule 10)"
            )
            break


def _extract_unit_metrics(scope_node: ast.AST, unit_name: str) -> Optional[FigureUnitMetrics]:
    p_tags = 0
    subplots_added = 0
    subplots_grid_cells = 0
    has_asymmetry = False
    primitives: Set[str] = set()
    bar_axes_vars: Set[str] = set()
    horiz_axes_vars: Set[str] = set()
    stick_candidate_vars: Set[str] = set()
    categorical_tick_axes_vars: Set[str] = set()
    violin_box_axes_vars: Set[str] = set()
    axis_methods: Dict[str, Set[str]] = {}
    has_savefig_or_plot = False

    RICH_DENSITY_METHODS = {
        "fill_between",
        "fill_betweenx",
        "violinplot",
        "boxplot",
        "imshow",
        "pcolormesh",
        "contour",
        "contourf",
        "hexbin",
        "stackplot",
        "streamplot",
        "quiver",
    }
    DATA_PLOT_METHODS = RICH_DENSITY_METHODS | {
        "bar",
        "barh",
        "scatter",
        "plot",
        "step",
        "ecdf",
        "errorbar",
        "hlines",
        "vlines",
        "stem",
        "hist",
        "kdeplot",
        "add_patch",
    }

    for node in ast.walk(scope_node):
        if not isinstance(node, ast.Call):
            continue
        fname = ""
        caller_var = ""
        if isinstance(node.func, ast.Attribute):
            fname = node.func.attr
            if isinstance(node.func.value, ast.Name):
                caller_var = node.func.value.id
            elif isinstance(node.func.value, ast.Subscript):
                caller_var = ast.unparse(node.func.value) if hasattr(ast, "unparse") else f"sub_{node.lineno}"
        elif isinstance(node.func, ast.Name):
            fname = node.func.id

        if caller_var and fname in DATA_PLOT_METHODS:
            axis_methods.setdefault(caller_var, set()).add(fname)
            if fname in ("violinplot", "boxplot"):
                violin_box_axes_vars.add(caller_var)
        elif caller_var and fname in ("set_xticklabels", "set_yticklabels"):
            categorical_tick_axes_vars.add(caller_var)

        if fname == "savefig":
            has_savefig_or_plot = True
        elif fname in ("panel_tag", "add_panel_label", "label_panel"):
            p_tags += 1
        elif fname in ("hlines", "vlines", "stem"):
            ax_key = caller_var or f"stick_{node.lineno}"
            stick_candidate_vars.add(ax_key)
            if fname == "hlines":
                horiz_axes_vars.add(ax_key)
        elif fname == "errorbar":
            ax_key = caller_var or f"err_{node.lineno}"
            stick_candidate_vars.add(ax_key)
            if any(kw.arg == "xerr" for kw in node.keywords):
                horiz_axes_vars.add(ax_key)
        elif fname == "plot" and len(node.args) >= 2:
            a0, a1 = node.args[0], node.args[1]
            if (
                isinstance(a0, (ast.List, ast.Tuple))
                and isinstance(a1, (ast.List, ast.Tuple))
                and len(a0.elts) == 2
                and len(a1.elts) == 2
                and hasattr(ast, "unparse")
            ):
                u_x0, u_x1 = ast.unparse(a0.elts[0]), ast.unparse(a0.elts[1])
                u_y0, u_y1 = ast.unparse(a1.elts[0]), ast.unparse(a1.elts[1])
                is_horiz_stick = (u_y0 == u_y1) and not isinstance(a1.elts[0], ast.Constant)
                is_vert_stick = (u_x0 == u_x1) and not isinstance(a0.elts[0], ast.Constant)
                if is_horiz_stick or is_vert_stick:
                    ax_key = caller_var or f"segstick_{node.lineno}"
                    stick_candidate_vars.add(ax_key)
                    if is_horiz_stick:
                        horiz_axes_vars.add(ax_key)
        elif fname in ("add_subplot", "add_axes"):
            subplots_added += 1
            if fname == "add_axes":
                has_asymmetry = True
            for sub in ast.walk(node):
                if isinstance(sub, ast.Slice):
                    has_asymmetry = True
            for kw in node.keywords:
                if kw.arg == "projection":
                    for st in _extract_const_strings(kw.value):
                        if st == "polar":
                            primitives.add("polar_radial")
                            has_asymmetry = True
        elif fname in ("GridSpec", "subgridspec", "subplots", "subplot_mosaic", "_make_canvas"):
            if fname in ("subgridspec", "subplot_mosaic"):
                has_asymmetry = True
            if fname == "subplots" and len(node.args) >= 2:
                if all(isinstance(a, ast.Constant) and isinstance(a.value, int) for a in node.args[:2]):
                    subplots_grid_cells += int(node.args[0].value) * int(node.args[1].value)
            for kw in node.keywords:
                if kw.arg in ("width_ratios", "height_ratios", "gridspec_kw"):
                    has_asymmetry = True
        else:
            for kw in node.keywords:
                if kw.arg in ("width_ratios", "height_ratios", "gridspec_kw"):
                    has_asymmetry = True

        if fname in PLOT_PRIMITIVE_FAMILIES:
            has_savefig_or_plot = True
            fam = PLOT_PRIMITIVE_FAMILIES[fname]
            primitives.add(fam)
            if fam == "bar_chart":
                bar_axes_vars.add(caller_var or f"bar_{node.lineno}")

    if not has_savefig_or_plot and p_tags == 0 and subplots_added == 0:
        return None

    naked_sticks = sorted(
        ax_k for ax_k in stick_candidate_vars if not (axis_methods.get(ax_k, set()) & RICH_DENSITY_METHODS)
    )
    nominal_zigzags = sorted(
        ax_k
        for ax_k in categorical_tick_axes_vars
        if "plot" in axis_methods.get(ax_k, set())
        and bool(axis_methods.get(ax_k, set()) & {"fill_between", "fill_betweenx"})
        and not bool(
            axis_methods.get(ax_k, set())
            & {"violinplot", "boxplot", "imshow", "pcolormesh", "stackplot", "errorbar", "bar", "barh", "contourf", "hexbin"}
        )
    )
    multilayer_cnt = sum(1 for mset in axis_methods.values() if len(mset) >= 2 or ("imshow" in mset) or ("contourf" in mset))

    n_panels = p_tags if p_tags > 0 else (subplots_added if subplots_added > 0 else max(subplots_grid_cells, 1))
    return FigureUnitMetrics(
        unit_name=unit_name,
        n_panels=n_panels,
        has_asymmetry=has_asymmetry,
        primitives=primitives,
        bar_axes_count=len(bar_axes_vars),
        horiz_axes_count=len(horiz_axes_vars),
        naked_stick_axes=naked_sticks,
        nominal_zigzag_axes=nominal_zigzags,
        violin_box_axes_count=len(violin_box_axes_vars),
        multilayer_axes_count=multilayer_cnt,
        total_data_axes_count=max(len(axis_methods), 1),
    )


def collect_figure_units_from_script(tree: ast.AST, path: pathlib.Path) -> List[FigureUnitMetrics]:
    """Extract per-figure units whether the project uses 1 monolithic script (build_fig1..N)
    or separate per-figure scripts (fig1_overview.py .. fig6_clinical.py)."""
    if HELPER_SCRIPT_NAME_RE.match(path.name) or SUPP_SCRIPT_NAME_RE.search(path.name):
        return []
    main_funcs = [
        n for n in tree.body if isinstance(n, ast.FunctionDef) and MAIN_FIG_FUNC_RE.match(n.name)
    ]
    if len(main_funcs) >= 2:
        units = []
        for fn in main_funcs:
            m = _extract_unit_metrics(fn, f"{path.name}:{fn.name}")
            if m:
                units.append(m)
        return units

    m = _extract_unit_metrics(tree, path.name)
    return [m] if m else []


def audit_aggregated_suite(
    units: List[FigureUnitMetrics],
    state: Optional[Dict] = None,
    combined_src: str = "",
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    if len(units) < 2:
        return errors, warnings

    track = str(
        (state or {}).get("flagship_track")
        or (state or {}).get("research_track")
        or (state or {}).get("track")
        or ((state or {}).get("story_contract") or {}).get("flagship_track")
        or ""
    ).strip().lower()
    if (state or {}).get("article_mode") == "review" or (state or {}).get("deliverable") == "review":
        track = "review"

    if track == "review":
        return errors, warnings

    is_wetlab = (track == "wetlab_mechanism") or bool((state or {}).get("has_wetlab_experiments"))
    if is_wetlab:
        min_families = 3
        max_bar_ratio = 0.35
        max_bar_per_fig = 2
        min_multilayer_ratio = 0.50
        min_violin_box = 1
    else:
        min_families = 5 if len(units) == 2 else 6
        max_bar_ratio = 0.12
        max_bar_per_fig = 1
        min_multilayer_ratio = 0.75
        min_violin_box = 3

    panel_counts = [(u.unit_name, u.n_panels) for u in units]
    counts_only = [u.n_panels for u in units if u.n_panels > 0]
    asymmetric_fig_count = sum(1 for u in units if u.has_asymmetry)
    suite_primitives: Set[str] = set()
    for u in units:
        suite_primitives.update(u.primitives)

    if len(counts_only) >= 4 and len(set(counts_only)) == 1:
        errors.append(
            f"[Suite({len(units)} figs)] 违禁均质机械宫格构图 (Rule 7): 检测到 {len(counts_only)} 张主图的面板数 100% 雷同 "
            f"({panel_counts}) → 既严禁全篇死板 2x2 四宫格，也严禁机械一刀切凑成相同格数；"
            f"请按每幕故事线证据体量按需有机排布 (如 5, 6, 6, 5, 5, 6 自然错落)"
        )

    if len(counts_only) >= 4 and asymmetric_fig_count < max(2, len(counts_only) // 2):
        errors.append(
            f"[Suite({len(units)} figs)] 缺乏非对称主焦点构图 (Rule 7): {len(counts_only)} 张主图中仅有 {asymmetric_fig_count} 张使用非对称 GridSpec "
            f"(width_ratios / height_ratios / subgridspec / subplot_mosaic / 跨列跨行切片) → 主图须设置主视觉焦点面板 (Hero Panel)"
        )

    if len(suite_primitives) < min_families:
        errors.append(
            f"[Suite({len(units)} figs)] 图表语汇单一 (Rule 8): 全套主图仅使用了 {len(suite_primitives)} 类视觉形态 ({sorted(suite_primitives)}) "
            f"→ 顶刊手稿多图套件必须组合 >= {min_families} 类互补高信息密度图型 (湿实验>=3类，干实验>=6类)"
        )

    total_panels = max(sum(counts_only), 1)
    total_bar_panels = sum(u.bar_axes_count for u in units)
    over_bar_figs = [(u.unit_name, u.bar_axes_count, u.n_panels) for u in units if u.bar_axes_count > max_bar_per_fig]
    if total_bar_panels / total_panels > max_bar_ratio or over_bar_figs:
        errors.append(
            f"[Suite({len(units)} figs)] 柱状图泛滥/单图堆砌超标 (Rule 8A): 全套柱状图面板为 {total_bar_panels}/{total_panels} 格 "
            f"({100.0 * total_bar_panels / total_panels:.1f}%，上限 <= {int(max_bar_ratio*100)}% 且单图 <= {max_bar_per_fig} 格)，且单图柱状图 > {max_bar_per_fig} 格的违规图: {over_bar_figs} "
            f"→ 严禁在同一张主图或附图中堆放过多柱状图面板，且严禁偷懒用火柴棒图替代柱状图！必须改用高信息密度图型："
            f"云雨分布图 (Raincloud: Violin+Box+Swarm)、多轨复合热图 (ComplexHeatmap+Marginal)、桑基/冲积流图 (Alluvial/Sankey)、"
            f"二维核密度等高线相图 (2D KDE Contour + Scatter)、连续阈值协同包络带 (Continuous Ribbon Envelope) 或多维点阵气泡矩阵"
        )

    naked_stick_figs = [(u.unit_name, u.naked_stick_axes) for u in units if u.naked_stick_axes]
    if naked_stick_figs:
        errors.append(
            f"[Suite({len(units)} figs)] 违禁低信息密度『火柴棒图/棒棒糖图/裸森林棒图』泛滥 (Rule 8B): 检测到裸火柴棒面板 (hlines/vlines/stem/errorbar 未叠加连续分布/曲面层): {naked_stick_figs} "
            f"→ 严禁用一维火柴棒图替代柱状图！任何区间/效应量面板必须升级为『分布密度带+箱线+全量单点云 (Raincloud)』、『带完整分布条与右侧多列数值表的复合森林图 (Nature Medicine Composite Forest-Table)』、『多阶段冲积流图 (Alluvial)』或『多轨定量点阵矩阵 (Multi-Track Matrix)』"
        )

    low_density_figs = [
        (u.unit_name, f"{u.multilayer_axes_count}/{u.total_data_axes_count}")
        for u in units
        if u.n_panels >= 4 and (u.multilayer_axes_count / max(u.total_data_axes_count, 1)) < min_multilayer_ratio
    ]
    if low_density_figs:
        errors.append(
            f"[Suite({len(units)} figs)] 面板信息密度不足/缺乏顶刊多维复合图层 (Rule 8C): 以下图的多维复合面板占比 < {int(min_multilayer_ratio*100)}%: {low_density_figs} "
            f"→ 顶刊面板须融合 >= 2 层互补视觉编码 (如 KDE密度+箱线+散点、2D等高线+全量散点+边缘分布、热图+边缘轨/数值标注、均值曲线+CI色带+个体轨迹)"
        )

    zigzag_over_figs = [(u.unit_name, u.nominal_zigzag_axes) for u in units if len(u.nominal_zigzag_axes) >= 2]
    total_zigzag_panels = sum(len(u.nominal_zigzag_axes) for u in units)
    if zigzag_over_figs or (total_zigzag_panels / total_panels > 0.12):
        errors.append(
            f"[Suite({len(units)} figs)] 违禁将离散名义分类变量强行连成『折线+阴影带锯齿图』取巧过关 (Rule 8D): "
            f"检测到 {total_zigzag_panels}/{total_panels} 个分类刻度面板 ({100.0 * total_zigzag_panels / total_panels:.1f}%，上限 <= 12% 且单图 <= 1 格) "
            f"在 set_xticklabels/set_yticklabels 名义分类轴上调用 plot()+fill_between() 伪装连续轨迹: {zigzag_over_figs} "
            f"→ 严禁用折线连接无序或名义类别（如不同队列、不同模型分支、不同亚组、不同特征）！名义分类对比必须改用真实的云雨分布图 (Raincloud: violinplot/boxplot + IQR + scatter)、"
            f"配对点阵/森林区间图或连续自变量（真实时间/FPR阈值/概率分位）上的经验曲线 (ROC / PR / Calibration / Conformal Operating Curve)！"
        )

    total_violin_box_panels = sum(u.violin_box_axes_count for u in units)
    if len(units) >= 4 and total_violin_box_panels < min_violin_box:
        errors.append(
            f"[Suite({len(units)} figs)] 缺乏真实分布形态面板 (Rule 8E): 全套 {total_panels} 个面板中仅有 {total_violin_box_panels} 个使用 violinplot/boxplot (< {min_violin_box} 个最低要求) "
            f"→ 多图套件必须包含 >= {min_violin_box} 个真实云雨图/小提琴/箱线分布面板以展示个体/重采样分布厚度，严禁全部用均线或点图代替！"
        )

    # 2026-11-05：TTE 已改为非默认推荐但不拦截；TTE 是因果推断不是预测模型，不再强制 ROC/PR/校准面板（只对预测赛道要求）
    if len(units) >= 4 and combined_src and track in ("dl_dynamic_multicohort",):
        has_roc_curve = bool(
            re.search(r"roc_curve|1\s*-\s*Specificity|False\s+Positive\s+Rate", combined_src, re.I)
            and re.search(r"Sensitivity|True\s+Positive\s+Rate", combined_src, re.I)
        )
        has_pr_or_calib = bool(
            re.search(r"precision_recall_curve|Positive\s+Predictive\s+Value|Precision", combined_src, re.I)
            or (
                re.search(r"Observed\s+.*(?:rate|prob|risk|mortality|deterioration|event|incidence)", combined_src, re.I)
                and re.search(r"Predicted\s+.*(?:prob|risk)", combined_src, re.I)
            )
        )
        if not has_roc_curve:
            errors.append(
                f"[Suite({len(units)} figs)] 临床预测/多队列 AI 赛道缺失顶刊必配『真实经验 ROC 曲线 (1 - Specificity vs Sensitivity)』面板 (Rule 8F): "
                f"必须在主图或附图中绘制基于患者级预测概率的连续阈值 ROC 曲线，严禁仅画名义分类汇总点！"
            )
        if not has_pr_or_calib:
            errors.append(
                f"[Suite({len(units)} figs)] 临床预测/多队列 AI 赛道缺失顶刊必配『真实经验 PR 曲线或校准度可靠性曲线 (Observed vs Predicted)』面板 (Rule 8F)！"
            )

    return errors, warnings


audit_suite_organic_structure = audit_aggregated_suite


def _expr_contains_exists_call(node: ast.AST) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            fn = sub.func.attr if isinstance(sub.func, ast.Attribute) else (sub.func.id if isinstance(sub.func, ast.Name) else "")
            if fn in ("exists", "is_file"):
                return True
    return False


def _resolve_ast_str_targets(expr: ast.AST, var_map: Dict[str, List[str]]) -> List[str]:
    out: List[str] = []
    for sub in ast.walk(expr):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
        elif isinstance(sub, ast.Name) and sub.id in var_map:
            out.extend(var_map[sub.id])
    return out


def audit_submission_and_locked_ast_safety(
    tree: ast.AST,
    src: str,
    path: pathlib.Path,
    locked_figs: List[str],
    errors: List[str],
) -> None:
    """AST-level enforcement of:
    1) Never delete submission/ images;
    2) Never write/copy/move/savefig into submission/ without an enclosing `if not ...exists(...)` guard;
    3) Never overwrite or delete any figure listed in MANUSCRIPT_STATE.json `locked_approved_figures`.
    """
    var_map: Dict[str, List[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            lits = [c.value for c in ast.walk(node.value) if isinstance(c, ast.Constant) and isinstance(c.value, str)]
            if lits:
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        var_map.setdefault(tgt.id, []).extend(lits)

    locked_names = {pathlib.Path(x).name.lower() for x in (locked_figs or []) if str(x).strip()}
    locked_stems = {pathlib.Path(x).stem.lower() for x in (locked_figs or []) if str(x).strip()}

    DELETE_FUNCS = {"remove", "unlink", "rmtree"}
    WRITE_ARG0_FUNCS = {"savefig", "save", "write_bytes", "imsave"}
    WRITE_ARG1_FUNCS = {"copy", "copy2", "copyfile", "move", "replace", "rename"}

    def _matches_submission(s: str) -> bool:
        norm = s.replace("\\", "/").lower()
        return bool(re.search(r"(?:^|/)(?:submission|submission_package[^/]*|投稿[^/]*)(?:/|$)", norm))

    def _matches_locked(s: str) -> Optional[str]:
        if not locked_names:
            return None
        p = pathlib.Path(s.replace("\\", "/"))
        nm = p.name.lower()
        st = p.stem.lower()
        if nm in locked_names:
            return p.name
        if st and st in locked_stems and p.suffix.lower() in (".png", ".pdf", ".svg", ".tif", ".tiff", ".jpg"):
            return p.name
        return None

    def _iter_non_stmt_calls(root_stmt: ast.stmt):
        stack = [c for c in ast.iter_child_nodes(root_stmt) if not isinstance(c, (ast.stmt, ast.ExceptHandler))]
        while stack:
            cur = stack.pop()
            if isinstance(cur, ast.Call):
                yield cur
            for ch in ast.iter_child_nodes(cur):
                if not isinstance(ch, (ast.stmt, ast.ExceptHandler)):
                    stack.append(ch)

    def _walk_stmts(stmts: List[ast.stmt], guarded_by_exists: bool) -> None:
        for stmt in stmts:
            if isinstance(stmt, ast.If):
                cond_has_exists = _expr_contains_exists_call(stmt.test)
                _walk_stmts(stmt.body, guarded_by_exists or cond_has_exists)
                _walk_stmts(stmt.orelse, guarded_by_exists or cond_has_exists)
                continue
            for child_attr in ("body", "orelse", "finalbody", "handlers"):
                child_val = getattr(stmt, child_attr, None)
                if isinstance(child_val, list) and child_val and isinstance(child_val[0], (ast.stmt, ast.ExceptHandler)):
                    if isinstance(child_val[0], ast.ExceptHandler):
                        for eh in child_val:
                            _walk_stmts(eh.body, guarded_by_exists)
                    else:
                        _walk_stmts(child_val, guarded_by_exists)

            for node in _iter_non_stmt_calls(stmt):
                fn = node.func.attr if isinstance(node.func, ast.Attribute) else (node.func.id if isinstance(node.func, ast.Name) else "")
                if fn in DELETE_FUNCS:
                    targets: List[str] = []
                    for a in node.args:
                        targets.extend(_resolve_ast_str_targets(a, var_map))
                    if isinstance(node.func, ast.Attribute):
                        targets.extend(_resolve_ast_str_targets(node.func.value, var_map))
                    for t in targets:
                        if _matches_submission(t):
                            errors.append(
                                f"[{path.name}:L{node.lineno}] 触发『投稿包禁删死角铁律』: 检测到针对 submission/投稿版 目录的删除调用 {fn}({t!r})！"
                            )
                        lk = _matches_locked(t)
                        if lk:
                            errors.append(
                                f"[{path.name}:L{node.lineno}] 触发『已锁定认可图片禁删铁律』: 试图删除 MANUSCRIPT_STATE 锁定图片 {lk!r}！"
                            )
                elif fn in WRITE_ARG0_FUNCS or fn in WRITE_ARG1_FUNCS:
                    target_exprs: List[ast.AST] = []
                    if fn in WRITE_ARG0_FUNCS:
                        if node.args:
                            target_exprs.append(node.args[0])
                        if isinstance(node.func, ast.Attribute) and fn == "write_bytes":
                            target_exprs.append(node.func.value)
                        for kw in node.keywords:
                            if kw.arg in ("fname", "fp", "filename", "dst"):
                                target_exprs.append(kw.value)
                    else:
                        if len(node.args) >= 2:
                            target_exprs.append(node.args[1])
                        for kw in node.keywords:
                            if kw.arg in ("dst", "target"):
                                target_exprs.append(kw.value)
                    targets = []
                    for te in target_exprs:
                        targets.extend(_resolve_ast_str_targets(te, var_map))
                    for t in targets:
                        if _matches_submission(t) and not guarded_by_exists:
                            errors.append(
                                f"[{path.name}:L{node.lineno}] 触发『投稿包图片不覆盖铁律』: 检测到未加 exists() 保护直接向 submission/投稿版 写入/复制/移动 ({fn} -> {t!r})！"
                            )
                        lk = _matches_locked(t)
                        if lk and not guarded_by_exists:
                            errors.append(
                                f"[{path.name}:L{node.lineno}] 触发『已锁定用户认可图片禁覆盖铁律』: 脚本试图无条件重绘/覆盖 MANUSCRIPT_STATE.json 中的 locked_approved_figures ({fn} -> {lk!r})！"
                            )

    if isinstance(tree, ast.Module):
        _walk_stmts(tree.body, False)


def audit_python_script(
    path: pathlib.Path,
    allow_schematic: bool = False,
    locked_figs: Optional[List[str]] = None,
    allow_wetlab: bool = False,
) -> Tuple[List[str], List[str], Optional[ast.AST]]:
    errors: List[str] = []
    warnings: List[str] = []
    src = path.read_text(encoding="utf-8", errors="replace")

    has_global_frameon_false = bool(re.search(r"""['"]legend\.frameon['"]\s*:\s*False""", src))

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        errors.append(f"[{path.name}] Python 语法错误: {e}")
        return errors, warnings, None

    audit_submission_and_locked_ast_safety(tree, src, path, locked_figs or [], errors)

    fancy_bbox_count = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in RIGHT_COMB_HELPER_NAMES:
            errors.append(
                f"[{path.name}:L{node.lineno}] 违禁定义『右侧梳子超长横跨引线模板函数』({node.name}): "
                f"严禁将半边 X 轴拉空并把左/中象限散点横穿画布拉一排平行长引线到右侧竖列 (Rule 4)！"
                f"请改用象限内就近微距贴标（稀疏点 <=10 个直接 4-6pt 贴点直标，密集点按所在象限局部短距 repel，左半轴点绝不跨 x=0 右拉）"
            )
            continue

        if not isinstance(node, ast.Call):
            continue

        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if func_name in RIGHT_COMB_HELPER_NAMES:
            errors.append(
                f"[{path.name}:L{node.lineno}] 违禁调用『右侧梳子长引线模板』({func_name}): "
                f"禁止把散点标签统一拉到右侧空白列形成鱼竿/梳子交叉长线且多图重复套模板 (Rule 4)"
            )

        if func_name == "imshow" and node.args and hasattr(ast, "unparse"):
            arg0_src = ast.unparse(node.args[0])
            if RASTER_IMG_VAR_RE.search(arg0_src):
                for kw in node.keywords:
                    if kw.arg == "aspect" and isinstance(kw.value, ast.Constant) and kw.value.value == "auto":
                        errors.append(
                            f"[{path.name}:L{node.lineno}] 违禁对插画/横幅/底图使用 imshow({arg0_src}, aspect='auto') 导致上下压缩或横向拉伸失真: "
                            f"必须使用 aspect='equal' 并按图像真实像素宽高比 (W/H) 设置 extent 与 GridSpec 行高，严禁挤压变形！"
                        )

        if func_name == "scatter" and len(node.args) >= 2 and hasattr(ast, "unparse"):
            x_src = ast.unparse(node.args[0])
            y_src = ast.unparse(node.args[1])
            if re.search(r"published_", x_src, re.I) and re.search(r"(?:published_|neglog10_fdr)", y_src, re.I):
                errors.append(
                    f"[{path.name}:L{node.lineno}] 违禁纯重绘外部已发表附表双轴数值 (scatter X={x_src!r}, Y={y_src!r}): "
                    f"单面板 X 与 Y 轴均直接取自外部 published 字段，缺乏自有分析增量且易被审稿人质疑搬运 (Rule 9) → "
                    f"请改为『本研究供体/动物级重算效应量 (Y) vs 参考单细胞/队列基准 (X)』交叉一致性验证图"
                )

        if func_name in VISIBLE_LABEL_FUNCS:
            target_args = node.args
            if func_name in ("text", "figtext") and len(node.args) >= 3:
                target_args = [node.args[2]]
            elif func_name == "annotate" and len(node.args) >= 1:
                target_args = [node.args[0]]
            for arg in target_args:
                for st in _extract_const_strings(arg):
                    _audit_visible_label_string(st, path, node.lineno, func_name, errors, allow_wetlab=allow_wetlab)
            for kw in node.keywords:
                if kw.arg in ("s", "text", "label", "labels"):
                    for st in _extract_const_strings(kw.value):
                        _audit_visible_label_string(st, path, node.lineno, func_name, errors, allow_wetlab=allow_wetlab)
        else:
            for kw in node.keywords:
                if kw.arg == "label":
                    for st in _extract_const_strings(kw.value):
                        _audit_visible_label_string(st, path, node.lineno, f"{func_name}(label=)", errors, allow_wetlab=allow_wetlab)

        if func_name in ("text", "annotate", "figtext"):
            str_args = []
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    str_args.append(arg.value)
            for kw in node.keywords:
                if kw.arg in ("s", "text") and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    str_args.append(kw.value.value)

            has_bbox = any(kw.arg == "bbox" and kw.value is not None for kw in node.keywords)

            for s in str_args:
                clean_s = s.strip()
                if not clean_s:
                    continue
                lines = [ln.strip() for ln in clean_s.splitlines() if ln.strip()]
                word_count = len(re.findall(r"[A-Za-z0-9_]+", clean_s))
                has_narrative = bool(NARRATIVE_VERBS_RE.search(clean_s))
                is_stat = bool(STAT_TOKEN_RE.search(clean_s))

                if has_narrative and word_count >= 5:
                    errors.append(
                        f"[{path.name}:L{node.lineno}] 违禁图内叙事性注释 ({func_name}): "
                        f"{clean_s!r} → 解释性文字必须移入 Figure Legend 或 Results 正文 (Rule 2)"
                    )
                elif has_bbox and len(lines) >= 2 and word_count >= 7 and not is_stat:
                    errors.append(
                        f"[{path.name}:L{node.lineno}] 违禁图内多行文本框 ({func_name}+bbox): "
                        f"{clean_s!r} → 严禁在数据面板内塞入带框解释性文字块 (Rule 2)"
                    )
                elif len(lines) >= 3 and word_count >= 10 and not is_stat:
                    warnings.append(
                        f"[{path.name}:L{node.lineno}] 疑似过长多行图内文字 ({func_name}, {len(lines)}行/{word_count}词): "
                        f"{clean_s[:60]!r}... → 请确认是否应精简或移至 Figure Legend"
                    )

        if func_name == "FancyBboxPatch" and not allow_schematic:
            fancy_bbox_count += 1

        if func_name == "legend":
            frameon_kw = next((kw for kw in node.keywords if kw.arg == "frameon"), None)
            if frameon_kw is not None:
                if isinstance(frameon_kw.value, ast.Constant) and frameon_kw.value.value is True:
                    warnings.append(
                        f"[{path.name}:L{node.lineno}] legend(frameon=True) → 顶刊清爽制图标准建议 frameon=False 并置于扩轴留白区 (Rule 3)"
                    )
            elif not has_global_frameon_false:
                warnings.append(
                    f"[{path.name}:L{node.lineno}] legend() 未显式指定 frameon=False 且未设置 rcParams['legend.frameon']=False (Rule 3)"
                )

        if func_name == "inset_axes" and node.args:
            first_arg = node.args[0]
            if isinstance(first_arg, (ast.List, ast.Tuple)) and len(first_arg.elts) == 4:
                elts = first_arg.elts
                if all(isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) for e in elts):
                    x0, y0, w0, h0 = [float(e.value) for e in elts]
                    if 0.0 <= y0 < 0.08 and w0 > h0:
                        errors.append(
                            f"[{path.name}:L{node.lineno}] inset_axes([{x0}, {y0}, {w0}, {h0}]) 底部 y={y0} 过低 (<0.08) → "
                            f"色标标题极易与主轴底部刻度重叠，须上移至 y>=0.10 并下扩 ylim (Rule 5)"
                        )
                    elif w0 >= 0.15 and h0 >= 0.15:
                        # Embedded data/zoom sub-plot (not a thin colorbar): enforce dedicated corridor + runtime non-occlusion check
                        if x0 < 0.63 and y0 < 0.66:
                            errors.append(
                                f"[{path.name}:L{node.lineno}] 违禁内嵌数据子图 inset_axes([{x0}, {y0}, {w0}, {h0}]) 居中/偏左放置覆盖主图主体数据 (Rule 5): "
                                f"数据子图 x0={x0} (<0.63) 且 y0={y0} (<0.66) 极易压住主图散点云或截断主轨迹曲线 (如 Fig. 1b/1c/6b 病灶)！"
                                f"必须先右扩父轴 xlim (如 1.7x~1.88x) 或上扩 ylim 留出 100% 零数据走廊，再将子图置于右侧专属走廊 (x0>=0.64) 或顶部专属走廊 (y0>=0.68)"
                            )
                        if "assert_zero_inset_data_occlusion" not in src:
                            errors.append(
                                f"[{path.name}:L{node.lineno}] 含内嵌数据子图 inset_axes([{x0}, {y0}, {w0}, {h0}]) 的脚本缺少运行时像素级零遮挡断言 "
                                f"`_assert_zero_inset_data_occlusion(fig, stem)` (Rule 5): 必须在保存前校验父图散点 (collections) 与曲线 (lines) 落入子图 tightbbox 的数量严格为 0！"
                            )

    if fancy_bbox_count >= 5 and not allow_schematic:
        errors.append(
            f"[{path.name}] 检测到 {fancy_bbox_count} 处 FancyBboxPatch → "
            f"严禁用 matplotlib 圆角方框+文字拼凑伪机制流程图 (Rule 6)"
        )

    if ("bioicons_lib" in src or "cairosvg" in src or "<svg " in src) and (
        "Mechanism" in src or "Working Model" in src
    ) and not allow_schematic:
        errors.append(
            f"[{path.name}] 检测到程序化 SVG 拼接机制图 (bioicons_lib/cairosvg) → "
            f"机制图/假说图必须调用 image-generator 生成纯正 BioRender 2D 生物医学插画 (Rule 6)"
        )

    return errors, warnings, tree


def audit_png_image(path: pathlib.Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return errors, warnings

    with Image.open(path) as im:
        w, h = im.size
        if w < 1500 and h < 1200:
            warnings.append(f"[{path.name}] 分辨率偏低 ({w}x{h} px) → 确认是否达到 >=300 DPI 投稿要求")

        arr = np.asarray(im.convert("RGB"))
        non_white_top = np.mean(np.any(arr[:2, :, :] < 240, axis=-1))
        non_white_bot = np.mean(np.any(arr[-2:, :, :] < 240, axis=-1))
        non_white_left = np.mean(np.any(arr[:, :2, :] < 240, axis=-1))
        non_white_right = np.mean(np.any(arr[:, -2:, :] < 240, axis=-1))

        for side, ratio in [
            ("顶部", non_white_top),
            ("底部", non_white_bot),
            ("左侧", non_white_left),
            ("右侧", non_white_right),
        ]:
            if ratio > 0.05:
                warnings.append(
                    f"[{path.name}] 图像{side}外边缘 2px 内存在 {ratio*100:.1f}% 非白像素 → 请视检确认是否存在文字/图例贴边截断"
                )

    return errors, warnings


def _discover_state(targets: List[str], explicit_state: Optional[str]) -> Optional[Dict]:
    if explicit_state:
        sp = pathlib.Path(explicit_state)
        if sp.exists():
            return json.loads(sp.read_text(encoding="utf-8"))
        return None
    if not targets:
        return None
    base = pathlib.Path(targets[0]).resolve()
    if base.is_file():
        base = base.parent
    for cand in (
        base / "MANUSCRIPT_STATE.json",
        base.parent / "manuscript" / "MANUSCRIPT_STATE.json",
        base.parent.parent / "manuscript" / "MANUSCRIPT_STATE.json",
    ):
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="顶刊清爽制图、五维数据深度与已发表竞品对标十重硬门禁（支持单脚本多图与多脚本套件聚合审计）")
    parser.add_argument("targets", nargs="+", help="绘图脚本 (.py) 或目录路径（支持传入多个脚本 fig1.py fig2.py ...）")
    parser.add_argument("--images", nargs="*", default=[], help="生成的 PNG 图片文件或目录路径")
    parser.add_argument("--state", default=None, help="可选：MANUSCRIPT_STATE.json 路径（读取 locked_approved_figures 保护锁）")
    parser.add_argument("--allow-schematic", action="store_true", help="允许纯流程图/示意图使用 FancyBboxPatch")
    parser.add_argument("--allow-wetlab", action="store_true", help="干湿结合/湿实验稿件模式（放行真实湿实验 IHC/mIF/WB 面板标签）")
    parser.add_argument("--single-figure", action="store_true", help="单图独立脚本模式（跳过多主图套件面板错落与多样性聚合审计）")
    args = parser.parse_args()

    py_files: List[pathlib.Path] = []
    png_files: List[pathlib.Path] = []

    for t in args.targets:
        p = pathlib.Path(t)
        if not p.exists():
            print(f"❌ 找不到目标路径: {p}", file=sys.stderr)
            return 1
        if p.is_dir():
            py_files.extend(sorted(f for f in p.rglob("*.py") if "__pycache__" not in f.parts))
            png_files.extend(sorted(p.rglob("*.png")))
        elif p.suffix.lower() == ".py":
            py_files.append(p)
        elif p.suffix.lower() == ".png":
            png_files.append(p)

    for img_t in args.images:
        p = pathlib.Path(img_t)
        if p.is_dir():
            png_files.extend(sorted(p.rglob("*.png")))
        elif p.suffix.lower() == ".png":
            png_files.append(p)

    state = _discover_state(args.targets, args.state)
    locked_figs = (state or {}).get("locked_approved_figures", [])
    eff_allow_wetlab = bool(
        args.allow_wetlab
        or (state or {}).get("has_wetlab_experiments")
        or (state or {}).get("wet_lab_included")
        or str((state or {}).get("research_track") or "").strip() == "wetlab_mechanism"  # 2026-11-05 湿实验赛道自动放行 IHC/mIF/WB 标签
    )

    all_errors: List[str] = []
    all_warnings: List[str] = []
    suite_units: List[FigureUnitMetrics] = []

    for pyf in py_files:
        errs, warns, tree = audit_python_script(
            pyf,
            allow_schematic=args.allow_schematic,
            locked_figs=locked_figs,
            allow_wetlab=eff_allow_wetlab,
        )
        all_errors.extend(errs)
        all_warnings.extend(warns)
        if tree is not None and not args.single_figure:
            suite_units.extend(collect_figure_units_from_script(tree, pyf))

    if not args.single_figure and len(suite_units) >= 2:
        combined_src = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in py_files)
        s_errs, s_warns = audit_aggregated_suite(suite_units, state=state, combined_src=combined_src)
        all_errors.extend(s_errs)
        all_warnings.extend(s_warns)

    for pngf in png_files:
        errs, warns = audit_png_image(pngf)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    print("═" * 78)
    print(
        f"🎨 顶刊制图十重硬门禁审计报告 | 脚本: {len(py_files)} 个 | 主图单元: {len(suite_units)} 个 | PNG: {len(png_files)} 张"
    )
    if locked_figs:
        print(f"🔒 已锁定用户认可图片 (严禁重绘覆盖): {locked_figs}")
    print("═" * 78)

    if all_warnings:
        print(f"\n⚠️  警告项 ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"  - {w}")

    if all_errors:
        print(f"\n❌ 门禁拦截项 ({len(all_errors)}):")
        for e in all_errors:
            print(f"  - {e}")
        print("\n🔴 Audit result: FAILED (必须修复上述违禁制图项后再交付)")
        return 1

    print("\n✅ Audit result: ALL 10 GATES PASSED (有机非对称构图 / >=6类多元图型 / <=12%(湿实验<=35%)柱图占比 / 0代码名泄露 / 0文本框杂讯)")
    print("👁️ 强制提醒：请确保已通过 Read / ds-vision-skill 100% 逐图视检 PNG 并完成全图转灰度 90 秒可读性测试！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
