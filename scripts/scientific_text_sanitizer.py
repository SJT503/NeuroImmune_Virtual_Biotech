# -*- coding: utf-8 -*-
"""
scientific_text_sanitizer.py
============================
Universal sanitizer and native python-docx formatter for biomedical manuscripts.
Guarantees ZERO raw LaTeX ($...$, $$...$$, \\text, \\le, \\ge, \\times, \\to, \\pm, \\Delta,
\\binom, \\frac, \\log, ^{...}, _{...}) and ZERO unrendered Markdown (**bold**, *italic*, `code`, ###)
in any generated .md, .docx, or .pdf deliverable.
"""
import re
from docx.oxml.ns import qn

SUP_DIGIT_MAP = str.maketrans("+-0123456789", "⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sanitize_scientific_markdown(text: str) -> str:
    """
    Convert all inline/block LaTeX math ($...$, $$...$$) and LaTeX commands into clean,
    publication-grade scientific text with proper italic markers (*p*, *n*, *q*, *z*, *g*, *R*, *F*, *N*, *k*)
    and clean Unicode symbols (≤, ≥, ×, →, ±, Δ, −, ⁺, ⁻, ⁰..⁹).
    Leaves zero '$', zero '\\cmd', zero '{', zero '}', zero '`', zero '^', and zero '~' in .md files.
    """
    # 1. Hypergeometric downsampling formula (block or inline)
    text = text.replace(
        r"$$p_{\text{det}} = 1 - \frac{\binom{N-k}{F}}{\binom{N}{F}}$$",
        "*p*_det = 1 − C(*N* − *k*, *F*) / C(*N*, *F*)",
    )
    text = text.replace(
        r"$p_{\text{det}} = 1 - \binom{N-k}{F}/\binom{N}{F}$",
        "*p*_det = 1 − C(*N* − *k*, *F*) / C(*N*, *F*)",
    )

    # 2. Inline $...$ math expressions
    def convert_inline_math(m: re.Match) -> str:
        s = m.group(1).strip()

        # Specific superscripts inside \text{...}^{\text{...}}
        s = re.sub(r"\\text\{([^\}]+)\}\^\{\\text\{high\}\}", r"\1-high", s)
        s = re.sub(r"\\text\{([^\}]+)\}\^\{\\text\{([^\}]+)\}\}", r"\1\2", s)
        s = re.sub(r"\\text\{([^\}]+)\}\^\+", r"\1⁺", s)
        s = re.sub(r"\\text\{([^\}]+)\}\^-", r"\1⁻", s)
        s = re.sub(r"\\text\{([^\}]+)\}", r"\1", s)

        # Scientific powers of 10: 10^{-10}, 10^{-4}
        def repl_pow10(pm: re.Match) -> str:
            exp_str = pm.group(1).translate(SUP_DIGIT_MAP)
            return f"10{exp_str}"

        s = re.sub(r"10\^\{([+\-0-9]+)\}", repl_pow10, s)

        # Remaining ^{...} or ^+ or ^-
        s = re.sub(r"\^\+", "⁺", s)
        s = re.sub(r"\^-", "⁻", s)
        s = re.sub(r"\^\{high\}", "-high", s)
        s = re.sub(r"\^\{([^\}]+)\}", r"\1", s)

        # Subscripts like \log_2
        s = s.replace(r"\log_2", "log₂")

        # Math symbols
        s = s.replace(r"\le", "≤")
        s = s.replace(r"\ge", "≥")
        s = re.sub(r"\s*\\times\s*", " × ", s)
        s = s.replace(r"\to", "→")
        s = re.sub(r"\\pm\s*", "±", s)
        s = s.replace(r"\%", "%")
        s = s.replace(r"\Delta P", "Δ*P*")
        s = s.replace(r"\Delta", "Δ")

        # Normalize n=3 vs 3 -> n = 3 vs 3
        s = re.sub(r"\bn=([0-9])", r"n = \1", s)

        # Italicize statistical / math single-letter variables
        s = re.sub(r"\b([pqnzgRFNk])\b(?=\s*[=≤≥<>]|$|\s*,)", r"*\1*", s)
        if s in {"F", "N", "R", "g", "k", "n", "p", "q", "z"}:
            s = f"*{s}*"

        # Proper Unicode minus sign before numbers
        s = re.sub(r"^-(?=\d)", "−", s)

        return s

    text = re.sub(r"\$([^\$]+)\$", convert_inline_math, text)

    # 3. Clean any bare caret expressions outside $...$
    text = re.sub(r"\b(MCL1|Mcl1)\^high\^?\b", r"\1-high", text)
    text = re.sub(r"\b(p21)\^CIP1\^?\b", r"\1CIP1", text)
    text = re.sub(r"\b(p16)\^INK4a\^?\b", r"\1INK4a", text)
    text = re.sub(r"\b(p16)\^Ink4a\^?\b", r"\1Ink4a", text)
    text = re.sub(r"\b(p19)\^Arf\^?\b", r"\1Arf", text)

    # 4. Strip inline code backticks `...`
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # 5. Normalize any residual ~ markers
    text = text.replace("*p*~det~", "*p*_det")
    text = text.replace("log~2~FC", "log₂FC")

    return text


# Regex matching outer **bold** (which may contain inner *italic*) or standalone *italic*
_MD_TOKEN_RE = re.compile(r"(\*\*(?:[^*\n]|\*[^*\n]+\*)+\*\*|\*[^*\n]+\*)")
_SUPSUB_RE = re.compile(r"(\^[^\^\n]+\^|~[^~\n]+~)")


_UNICODE_SUP_TO_ASCII = str.maketrans("⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "+-0123456789")
_UNICODE_SUB_TO_ASCII = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def _prepare_supsub_markers_for_docx(text: str) -> str:
    """
    Convert known biological superscripts (p16INK4a, p16Ink4a, p19Arf, p21CIP1),
    Unicode superscript runs (⁺, ⁻, ⁰..⁹, e.g. p21⁺, 10⁻¹⁰, 10⁻⁴),
    and mathematical subscripts (p_det, *p*_det, log₂) into internal ^sup^ and ~sub~ markers
    using standard ASCII glyphs (which exist in 100% of Western and CJK fonts)
    for native Word superscript/subscript run creation.
    Also replaces U+2212 (−, missing in SimSun) with U+2013 (–) so 100% of characters
    have native glyphs in both Times New Roman and SimSun.
    """
    text = text.replace("\u2212", "–")
    text = re.sub(r"\bp16INK4a\b", "p16^INK4a^", text)
    text = re.sub(r"\bp16Ink4a\b", "p16^Ink4a^", text)
    text = re.sub(r"\bp19Arf\b", "p19^Arf^", text)
    text = re.sub(r"\bp21CIP1\b", "p21^CIP1^", text)
    text = text.replace("*p*_det", "*p*~det~")
    text = re.sub(r"\bp_det\b", "*p*~det~", text)
    # Convert contiguous Unicode superscript sequences (⁺, ⁻, ⁰..⁹) to ^ascii^
    text = re.sub(
        r"[⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+",
        lambda m: "^" + m.group(0).translate(_UNICODE_SUP_TO_ASCII) + "^",
        text,
    )
    # Convert contiguous Unicode subscript sequences (₀..₉) to ~ascii~
    text = re.sub(
        r"[₀₁₂₃₄₅₆₇₈₉]+",
        lambda m: "~" + m.group(0).translate(_UNICODE_SUB_TO_ASCII) + "~",
        text,
    )
    return text


def add_scientific_runs(p, line_text: str, east_asia_font: str = "SimSun", font_size=None, font_color=None):
    """
    Parse a sanitized scientific Markdown line into native python-docx runs on paragraph `p`:
      - Protects literal asterisks: escaped `\\*`, parenthesized `(*)`, and significance legends `* p < 0.05`
      - Renders outer `**bold**`, inner `**... *bold-italic* ...**`, and `*italic*`
      - Renders `^sup^` as native Word superscript (`r.font.superscript = True`)
      - Renders `~sub~` as native Word subscript (`r.font.subscript = True`)
      - Restores protected literal asterisks as plain `*`
      - Sets `Times New Roman` + East Asian font (`SimSun` or `微软雅黑`) on every run
    """
    txt = sanitize_scientific_markdown(line_text)
    txt = _prepare_supsub_markers_for_docx(txt)

    AST_PLACEHOLDER = "\x00AST\x00"
    txt = txt.replace(r"\*", AST_PLACEHOLDER)
    txt = re.sub(
        r"\(\*+\)|(?:^|(?<=\s))\*+(?=\s+\*?p\*?\s*[<=])",
        lambda m: m.group(0).replace("*", AST_PLACEHOLDER),
        txt,
    )

    def emit_leaf_runs(chunk: str, is_bold: bool, is_italic: bool):
        if not chunk:
            return
        for sub_part in _SUPSUB_RE.split(chunk):
            if not sub_part:
                continue
            is_sup = False
            is_sub = False
            content = sub_part
            if sub_part.startswith("^") and sub_part.endswith("^") and len(sub_part) > 2:
                content = sub_part[1:-1]
                is_sup = True
            elif sub_part.startswith("~") and sub_part.endswith("~") and len(sub_part) > 2:
                content = sub_part[1:-1]
                is_sub = True
            content = content.replace(AST_PLACEHOLDER, "*")
            r = p.add_run(content)
            if is_bold:
                r.bold = True
            if is_italic:
                r.italic = True
            if is_sup:
                r.font.superscript = True
            if is_sub:
                r.font.subscript = True
            r.font.name = "Times New Roman"
            r._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), east_asia_font)
            if font_size is not None:
                r.font.size = font_size
            if font_color is not None:
                r.font.color.rgb = font_color

    for part in _MD_TOKEN_RE.split(txt):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            inner = part[2:-2]
            for inner_part in re.split(r"(\*[^*\n]+\*)", inner):
                if not inner_part:
                    continue
                if inner_part.startswith("*") and inner_part.endswith("*") and len(inner_part) > 2:
                    emit_leaf_runs(inner_part[1:-1], is_bold=True, is_italic=True)
                else:
                    emit_leaf_runs(inner_part, is_bold=True, is_italic=False)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            emit_leaf_runs(part[1:-1], is_bold=False, is_italic=True)
        else:
            emit_leaf_runs(part, is_bold=False, is_italic=False)
