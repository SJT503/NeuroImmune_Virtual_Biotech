#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
03c_compile_docx_and_run_gates.py
Compiles submission-grade Word (.docx) files:
  - Manuscript_NeuroImmune_Virtual_Biotech_EN.docx
  - Manuscript_NeuroImmune_Virtual_Biotech_ZH.docx
  - Cover_Letter_EN.docx
Enforces manuscript-submission-docx-format:
  - 3-layer LaTeX & Markdown sanitizer (zero raw $ / \ / ** / ^ / ~ / ` in Word XML)
  - Times New Roman (11-12 pt) + SimSun (EastAsia)
  - Double line spacing (line_spacing = 2.0) and Justified body paragraphs (WD_ALIGN_PARAGRAPH.JUSTIFY)
  - Native publication three-line tables (Table 1, Table 2, Table 3)
  - Embedded 600 DPI flagship figures (Fig 1 - Fig 5) above their respective Figure Legends
  - Verifies 0 errors on manuscript_convention_and_parity_gate.py and Layer-3 Zero-Garble DOCX Gate.
"""

import pathlib
import re
import subprocess
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt

TEMPLATE_DIR = pathlib.Path(r"C:\Users\sheng\.gemini\config\skills\manuscript-submission-docx-format\templates")
sys.path.insert(0, str(TEMPLATE_DIR))
from scientific_text_sanitizer import add_scientific_runs

BASE_DIR = pathlib.Path(r"D:\AI工具\NeuroImmune_Virtual_Biotech\flagship_paper")
MS_DIR = BASE_DIR / "manuscript"
FIG_DIR = BASE_DIR / "figures"

FIG_MAP = {
    1: FIG_DIR / "Fig1_ClinicalTrials_230_Audit.png",
    2: FIG_DIR / "Fig2_Dynamic_Tau_Trajectories.png",
    3: FIG_DIR / "Fig3_SixGate_Ablation_and_Elo_Tournament.png",
    4: FIG_DIR / "Fig4_vGliaNiche_World_Model.png",
    5: FIG_DIR / "Fig5_ChronoStaged_Translation_Blueprint.png",
}

ED_FIG_MAP = {
    1: FIG_DIR / "Extended_Data_Fig1_PRISMA_and_ChronoWindow_Validation.png",
    2: FIG_DIR / "Extended_Data_Fig2_10GEO_CrossSpecies_MultiModal_Atlas.png",
    3: FIG_DIR / "Extended_Data_Fig3_Agentic_Deliberation_and_UpSet_Audit.png",
    4: FIG_DIR / "Extended_Data_Fig4_Human_Separatrix_and_MonteCarlo_Sensitivity.png",
}


SUB_DIGIT_MAP = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP_DIGIT_MAP = str.maketrans("+-0123456789", "⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def pre_sanitize_latex_for_docx(line: str) -> str:
    r"""
    Converts display equations ($$...$$) and inline LaTeX tokens (\tau, \alpha, \rho, \mu, \theta,
    \frac, \sum, \int, subscripts/superscripts) into clean scientific notation using Unicode
    superscript/subscript digits and plain text before passing to add_scientific_runs().
    """
    s = line

    display_replacements = {
        r"$$\tau_g(t) = \frac{\sum_{k=1}^{K} \left(1 - \hat{\mu}_{g,k}(t)\right)}{K - 1} \in [0, 1]$$":
            "τ_g(*t*) = [ ∑(k=1..K) (1 – μ̂_g,k(*t*)) ] / (*K* – 1) ∈ [0, 1]",
        r"$$\frac{dV}{dt} = k_{v,\text{ton}}(V_0 - V) - k_{v,\text{insult}} I_{\text{insult}}(t) V + k_{v,\text{brake}} U_{\text{Brake}}(t)(1 - V)$$":
            "d*V*/d*t* = *k*_v,ton(*V*₀ – *V*) – *k*_v,insult *I*_insult(*t*)*V* + *k*_v,brake *U*_Brake(*t*)(1 – *V*)",
        r"$$\frac{dV}{dt} = k_{v,\text{ton}}(V_0 - V) - k_{v,\text{loss}} I_{\text{insult}}(t) V + k_{v,\text{brk}} U_{\text{Brake}}(t)(1 - V)$$":
            "d*V*/d*t* = *k*_v,ton(*V*₀ – *V*) – *k*_v,loss *I*_insult(*t*)*V* + *k*_v,brk *U*_Brake(*t*)(1 – *V*)",
        r"$$\frac{dM}{dt} = k_{m,\text{storm}} S(t)(1 - M)\frac{1}{1 + (V / K_v)^2} - d_m M$$":
            "d*M*/d*t* = *k*_m,storm *S*(*t*)(1 – *M*) [1 / (1 + (*V*/*K*_v)²)] – *d*_m *M*",
        r"$$\frac{dM}{dt} = k_{m,\text{storm}} S_{\text{insult}}(t)(1 - M)\frac{1}{1 + (V / K_v)^2} - d_m M$$":
            "d*M*/d*t* = *k*_m,storm *S*_insult(*t*)(1 – *M*) [1 / (1 + (*V*/*K*_v)²)] – *d*_m *M*",
        r"$$\frac{dM}{dt} = k_{m,\text{storm}} I_{\text{insult}}(t)(1 - M)\frac{1}{1 + (V / K_v)^2} - d_m M$$":
            "d*M*/d*t* = *k*_m,storm *I*_insult(*t*)(1 – *M*) [1 / (1 + (*V*/*K*_v)²)] – *d*_m *M*",
        r"$$\frac{dA}{dt} = k_{a,m} M(1 - A) + k_{a,\text{loop}} L(1 - A)\big(1 - U_{\text{Folh1}}(t)\big) - d_a A$$":
            "d*A*/d*t* = *k*_a,m *M*(1 – *A*) + *k*_a,loop *L*(1 – *A*)(1 – *U*_Folh1(*t*)) – *d*_a *A*",
        r"$$\frac{dL}{dt} = k_{l,\text{lock}} \frac{E(t)^4}{E_{\text{crit}}^4 + E(t)^4}(1 - L) - k_{l,\text{unlock}} U_{\text{Combo}}(t) L - d_l L, \quad E(t) = \int_0^t \big[M(\tau) + A(\tau)\big]\,d\tau$$":
            "d*L*/d*t* = *k*_l,lock [*E*(*t*)⁴ / (*E*_crit⁴ + *E*(*t*)⁴)](1 – *L*) – *k*_l,unlock *U*_Combo(*t*)*L* – *d*_l *L*, where *E*(*t*) = ∫(0..t) [*M*(τ) + *A*(τ)] dτ",
        r"$$\frac{dL}{dt} = k_{l,\text{lock}} \frac{E_{\text{auc}}(t)^4}{E_{\text{crit}}^4 + E_{\text{auc}}(t)^4}(1 - L) - k_{l,\text{unlock}} U_{\text{Combo}}(t) L - d_l L, \quad E_{\text{auc}}(t) = \int_0^t \big[0.65\,M(\tau) + 0.35\,A(\tau)\big]\,d\tau$$":
            "d*L*/d*t* = *k*_l,lock [*E*_auc(*t*)⁴ / (*E*_crit⁴ + *E*_auc(*t*)⁴)](1 – *L*) – *k*_l,unlock *U*_Combo(*t*)*L* – *d*_l *L*, where *E*_auc(*t*) = ∫(0..t) [0.65 *M*(τ) + 0.35 *A*(τ)] dτ",
        r"$$\frac{dC}{dt} = k_{c,\text{rec}}(1 - C)\big(1 + k_{c,\text{gate}} U_{\text{Scn3a/Rnf112}}(t)\big) - \big(k_{c,m} M + k_{c,a} A + k_{c,l} L\big) C$$":
            "d*C*/d*t* = *k*_c,rec(1 – *C*)(1 + *k*_c,gate *U*_Scn3a/Rnf112(*t*)) – (*k*_c,m *M* + *k*_c,a *A* + *k*_c,l *L*)*C*",
        r"$$\frac{dS}{dt} = k_{s,\text{rec}}(1 - S)\big(1 + k_{s,\text{gate}} U_{\text{Scn3a/Rnf112}}(t)\big) - \big(k_{s,m} M + k_{s,a} A + k_{s,l} L\big) S$$":
            "d*S*/d*t* = *k*_s,rec(1 – *S*)(1 + *k*_s,gate *U*_Scn3a/Rnf112(*t*)) – (*k*_s,m *M* + *k*_s,a *A* + *k*_s,l *L*)*S*",
    }
    for k, v in display_replacements.items():
        if k in s:
            s = s.replace(k, v)

    s = s.replace("$$", "$")

    def clean_math_span(m: re.Match) -> str:
        expr = m.group(1)
        expr = expr.replace(r"\,", " ")
        expr = expr.replace(r"\quad", "  ")
        expr = expr.replace(r"\big[", "[").replace(r"\big]", "]").replace(r"\big(", "(").replace(r"\big)", ")")
        expr = expr.replace(r"\left(", "(").replace(r"\right)", ")")
        expr = expr.replace(r"\{", "(").replace(r"\}", ")")
        expr = re.sub(r"\\text\{([^\}]+)\}", r"\1", expr)
        expr = re.sub(r"\\hat\{\\mu\}", "μ̂", expr)
        expr = re.sub(r"\\hat\{\\theta\}", "θ̂", expr)
        expr = re.sub(r"\\bar\{w\}", "w̄", expr)
        expr = expr.replace(r"\tau", "τ")
        expr = expr.replace(r"\alpha", "α")
        expr = expr.replace(r"\beta", "β")
        expr = expr.replace(r"\gamma", "γ")
        expr = expr.replace(r"\phi", "φ")
        expr = expr.replace(r"\rho", "ρ")
        expr = expr.replace(r"\mu", "μ")
        expr = expr.replace(r"\theta", "θ")
        expr = expr.replace(r"\Delta", "Δ")
        expr = expr.replace(r"\int_0^t", "∫(0..t)")
        expr = expr.replace(r"\leftrightarrow", "↔")
        expr = expr.replace(r"\rightarrow", "→")
        expr = expr.replace(r"\to", "→")
        expr = expr.replace(r"\succ", "≻")
        expr = re.sub(r"\\in\b", "∈", expr)
        expr = expr.replace(r"\le", "≤")
        expr = expr.replace(r"\ge", "≥")
        expr = expr.replace(r"\pm", "±")
        expr = expr.replace(r"\dots", "...")
        expr = expr.replace(r"\cdot", "·")
        expr = re.sub(r"\s*\\times\s*", " × ", expr)
        expr = expr.replace(r"\%", "%")
        expr = re.sub(r"\\sum_([a-zA-Z0-9]+)", r"∑_\1", expr)
        expr = re.sub(r"\\tilde\{([^\}]+)\}", lambda pm: pm.group(1) + "\u0303", expr)
        expr = re.sub(r"\\max_\{([^\}]+)\}", r"max(\1)", expr)

        # Numeric subscripts _{50} or _0 -> Unicode subscript digits ₅₀, ₀
        expr = re.sub(r"_\{([0-9]+)\}", lambda pm: pm.group(1).translate(SUB_DIGIT_MAP), expr)
        expr = re.sub(r"_([0-9]+)\b", lambda pm: pm.group(1).translate(SUB_DIGIT_MAP), expr)
        # Text subscripts _{crit} -> _crit (use dot or plain text to avoid ~...~ conversion)
        expr = re.sub(r"_\{([^\}]+)\}", r"(\1)", expr)
        expr = re.sub(r"_([a-zA-Z0-9]+)", r"(\1)", expr)

        # Numeric superscripts ^{-4} or ^2 -> Unicode superscript digits ⁻⁴, ²
        expr = re.sub(r"\^\{([+\-0-9]+)\}", lambda pm: pm.group(1).translate(SUP_DIGIT_MAP), expr)
        expr = re.sub(r"\^([+\-0-9]+)\b", lambda pm: pm.group(1).translate(SUP_DIGIT_MAP), expr)
        expr = re.sub(r"\^\{([^\}]+)\}", r"(\1)", expr)

        # Replace \frac{A}{B} after inner braces have been flattened
        expr = re.sub(r"\\frac\{([^\}]+)\}\{([^\}]+)\}", r"(\1)/(\2)", expr)
        expr = expr.replace(r"\exp", "exp")
        expr = re.sub(r"\\([a-zA-Z]+)", r"\1", expr)
        return expr

    s = re.sub(r"\$([^\$]+)\$", clean_math_span, s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = s.replace("`", "")
    s = re.sub(r"_([0-9]+)\b", lambda pm: pm.group(1).translate(SUB_DIGIT_MAP), s)
    # Strip leading blockquote marker '> ' if present
    if s.startswith("> "):
        s = s[2:].strip()
        if s.startswith('*"') and s.endswith('"*'):
            s = '"' + s[2:-2] + '"'
    # Prevent Unicode subscripts/superscripts inside **...** or *...* spans from leaving unparsed ~0~ or ^...^ tokens
    def clean_styled_span(bm: re.Match) -> str:
        delim = bm.group(1)
        inner = bm.group(2)
        inner = inner.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹", "01234567890123456789"))
        return f"{delim}{inner}{delim}"
    s = re.sub(r"(\*\*|\*)([^\*]+)\1", clean_styled_span, s)
    return s


def set_east_asia_font(run, font_name="SimSun"):
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), font_name)


def format_paragraph_runs(p, font_size_pt=12, bold_override=None):
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(font_size_pt)
        if bold_override is not None:
            r.bold = bold_override
        set_east_asia_font(r, "SimSun")


def set_three_line_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f"""
        <w:tblBorders {nsdecls('w')}>
            <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>
            <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
        """
    )
    tblPr.append(borders)


def build_docx_from_md(md_path: pathlib.Path, docx_path: pathlib.Path, embed_figures: bool = True):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")

    lines = md_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line == "---":
            i += 1
            continue

        # Markdown table block
        if line.startswith("|") and line.endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tline = lines[i].strip()
                if not re.match(r"^\|[\s:\-\|]+\|$", tline):
                    raw_cells = re.split(r"\s+\|\s+", tline.strip().strip("|").strip())
                    cells = [pre_sanitize_latex_for_docx(c.strip()) for c in raw_cells]
                    table_lines.append(cells)
                i += 1
            if table_lines:
                ncols = max(len(r) for r in table_lines)
                tbl = doc.add_table(rows=len(table_lines), cols=ncols)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                set_three_line_table_borders(tbl)
                for r_idx, row_cells in enumerate(table_lines):
                    for c_idx in range(ncols):
                        val = row_cells[c_idx] if c_idx < len(row_cells) else ""
                        cell = tbl.cell(r_idx, c_idx)
                        p = cell.paragraphs[0]
                        p.paragraph_format.line_spacing = 1.15
                        p.paragraph_format.space_before = Pt(2)
                        p.paragraph_format.space_after = Pt(2)
                        add_scientific_runs(p, val)
                        format_paragraph_runs(p, font_size_pt=9, bold_override=(r_idx == 0))
            continue

        # Title (# )
        if line.startswith("# "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 2.0
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(4)
            add_scientific_runs(p, pre_sanitize_latex_for_docx(line[2:].strip()))
            format_paragraph_runs(p, font_size_pt=16, bold_override=True)
            i += 1
            continue

        # H2 (## )
        if line.startswith("## "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 2.0
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            add_scientific_runs(p, pre_sanitize_latex_for_docx(line[3:].strip()))
            format_paragraph_runs(p, font_size_pt=14, bold_override=True)
            i += 1
            continue

        # H3 (### )
        if line.startswith("### "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 2.0
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            add_scientific_runs(p, pre_sanitize_latex_for_docx(line[4:].strip()))
            format_paragraph_runs(p, font_size_pt=12, bold_override=True)
            i += 1
            continue

        # H4 (#### Figure N / #### Table M placement slug in Markdown, or H4 subheadings in Rebuttal)
        if line.startswith("#### "):
            if line.startswith("#### Figure") or line.startswith("#### Table"):
                i += 1
                continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 2.0
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            add_scientific_runs(p, pre_sanitize_latex_for_docx(line[5:].strip()))
            format_paragraph_runs(p, font_size_pt=12, bold_override=True)
            i += 1
            continue

        # Check if this paragraph is the start of a Figure Legend (**Fig. N | ... or **Extended Data Fig. N | ...)
        m_fig_leg = re.match(r"^\*\*Fig\.\s*(\d+)\s*\|", line)
        m_ed_leg = re.match(r"^\*\*(?:Extended Data Fig\.|Supplementary Fig\.\s*S?)\s*(\d+)\s*\|", line)
        if embed_figures and (m_fig_leg or m_ed_leg):
            if m_fig_leg:
                fig_idx = int(m_fig_leg.group(1))
                fig_png = FIG_MAP.get(fig_idx)
            else:
                fig_idx = int(m_ed_leg.group(1))
                fig_png = ED_FIG_MAP.get(fig_idx)
            if fig_png and fig_png.exists():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(10)
                p_img.paragraph_format.space_after = Pt(4)
                p_img.add_run().add_picture(str(fig_png), width=Inches(6.4))

        # Regular or numbered/bulleted paragraph
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 2.0
        p.paragraph_format.space_after = Pt(6)
        add_scientific_runs(p, pre_sanitize_latex_for_docx(line))
        format_paragraph_runs(p, font_size_pt=12)
        i += 1

    doc.save(str(docx_path))
    print(f"[OK] Saved Word document: {docx_path.name} ({docx_path.stat().st_size / 1024:.1f} KB)")


def verify_docx_zero_garble(docx_path: pathlib.Path):
    doc = Document(str(docx_path))
    all_texts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                all_texts.append(cell.text)
    joined = "\n".join(all_texts)
    bad_patterns = [r"\*\*", r"##", r"\^\S+\^", r"~\S+~", r"`", r"\$", r"\\text", r"\\tau", r"\\frac"]
    hits = []
    for pat in bad_patterns:
        m = re.findall(pat, joined)
        if m:
            hits.append((pat, m[:5]))
    assert not hits, f"Garble found in {docx_path.name}: {hits}"
    print(f"[PASS] Layer 3 Zero-Garble DOCX Gate ({docx_path.name}): 0 raw Markdown/LaTeX/caret/tilde tokens")


def main():
    en_md = MS_DIR / "Manuscript_NeuroImmune_Virtual_Biotech_EN.md"
    zh_md = MS_DIR / "Manuscript_NeuroImmune_Virtual_Biotech_ZH.md"
    cl_md = MS_DIR / "Cover_Letter_EN.md"
    reb_md = MS_DIR / "Point_by_Point_Rebuttal_Letter_EN.md"

    en_docx = MS_DIR / "Manuscript_NeuroImmune_Virtual_Biotech_EN.docx"
    zh_docx = MS_DIR / "Manuscript_NeuroImmune_Virtual_Biotech_ZH.docx"
    cl_docx = MS_DIR / "Cover_Letter_EN.docx"
    reb_docx = MS_DIR / "Point_by_Point_Rebuttal_Letter_EN.docx"

    build_docx_from_md(en_md, en_docx, embed_figures=True)
    build_docx_from_md(zh_md, zh_docx, embed_figures=True)
    build_docx_from_md(cl_md, cl_docx, embed_figures=False)
    if reb_md.exists():
        build_docx_from_md(reb_md, reb_docx, embed_figures=False)

    verify_docx_zero_garble(en_docx)
    verify_docx_zero_garble(zh_docx)
    verify_docx_zero_garble(cl_docx)
    if reb_docx.exists():
        verify_docx_zero_garble(reb_docx)

    conv_gate = r"C:\Users\sheng\.claude\scripts\manuscript_convention_and_parity_gate.py"
    for a, b in [(en_md, zh_md), (en_docx, zh_docx)]:
        res = subprocess.run(
            [sys.executable, conv_gate, str(a), "--zh", str(b)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        print(f"[Gate: {a.name} + {b.name}] -> {res.stdout.strip()}")
        if res.returncode != 0:
            print(res.stderr)
            sys.exit(res.returncode)


if __name__ == "__main__":
    main()
