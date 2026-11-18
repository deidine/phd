import re
import sys

from fontTools.ttLib import TTFont as FTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, FrameBreak,
    Table, TableStyle, XPreformatted, KeepTogether, NextPageTemplate,
)

FONT_DIR = "/System/Library/Fonts/Supplemental/"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
pdfmetrics.registerFont(TTFont("TimesCustom", FONT_DIR + "Times New Roman.ttf"))
pdfmetrics.registerFont(TTFont("TimesCustom-Bold", FONT_DIR + "Times New Roman Bold.ttf"))
pdfmetrics.registerFont(TTFont("TimesCustom-Italic", FONT_DIR + "Times New Roman Italic.ttf"))
pdfmetrics.registerFont(TTFont("TimesCustom-BoldItalic", FONT_DIR + "Times New Roman Bold Italic.ttf"))
pdfmetrics.registerFontFamily(
    "TimesCustom", normal="TimesCustom", bold="TimesCustom-Bold",
    italic="TimesCustom-Italic", boldItalic="TimesCustom-BoldItalic",
)

pdfmetrics.registerFont(TTFont("CourierCustom", FONT_DIR + "Courier New.ttf"))
pdfmetrics.registerFont(TTFont("CourierCustom-Bold", FONT_DIR + "Courier New Bold.ttf"))
pdfmetrics.registerFontFamily("CourierCustom", normal="CourierCustom", bold="CourierCustom-Bold")

pdfmetrics.registerFont(TTFont("ArialUni", FONT_DIR + "Arial Unicode.ttf"))

TIMES_CMAP = set(FTFont(FONT_DIR + "Times New Roman.ttf").getBestCmap().keys())
COURIER_CMAP = set(FTFont(FONT_DIR + "Courier New.ttf").getBestCmap().keys())

SUBSCRIPT_DIGITS = {
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
}

# ---------------------------------------------------------------------------
# Text helpers: XML-escape, Unicode-subscript -> <sub>, missing-glyph fallback
# ---------------------------------------------------------------------------

def xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sub_and_fallback(escaped_text, cmap):
    out = []
    i, n = 0, len(escaped_text)
    while i < n:
        ch = escaped_text[i]
        if ch in SUBSCRIPT_DIGITS:
            j = i
            digits = ""
            while j < n and escaped_text[j] in SUBSCRIPT_DIGITS:
                digits += SUBSCRIPT_DIGITS[escaped_text[j]]
                j += 1
            out.append(f"<sub>{digits}</sub>")
            i = j
            continue
        cp = ord(ch)
        if cp < 128 or cp in cmap:
            out.append(ch)
        else:
            out.append(f'<font face="ArialUni">{ch}</font>')
        i += 1
    return "".join(out)


INLINE_RE = re.compile(r"\*\*(.+?)\*\*|\*([^*]+?)\*|`([^`]+?)`")


def tokenize_inline(raw):
    segments = []
    pos = 0
    for m in INLINE_RE.finditer(raw):
        if m.start() > pos:
            segments.append(("text", raw[pos:m.start()]))
        if m.group(1) is not None:
            segments.append(("bold", m.group(1)))
        elif m.group(2) is not None:
            segments.append(("italic", m.group(2)))
        else:
            segments.append(("code", m.group(3)))
        pos = m.end()
    if pos < len(raw):
        segments.append(("text", raw[pos:]))
    return segments


def build_markup(raw, cmap_primary=TIMES_CMAP):
    parts = []
    for kind, seg in tokenize_inline(raw):
        esc = xml_escape(seg)
        if kind == "code":
            body = sub_and_fallback(esc, COURIER_CMAP)
            parts.append(f'<font face="CourierCustom" size="8.3">{body}</font>')
        else:
            body = sub_and_fallback(esc, cmap_primary)
            if kind == "bold":
                parts.append(f"<b>{body}</b>")
            elif kind == "italic":
                parts.append(f"<i>{body}</i>")
            else:
                parts.append(body)
    return "".join(parts)


def wrap_code_line(line, max_width_pts, font="CourierCustom", size=7.9, indent="  "):
    from reportlab.pdfbase.pdfmetrics import stringWidth

    def width(s):
        return stringWidth(s, font, size)

    if width(line) <= max_width_pts:
        return [line]

    leading_ws = len(line) - len(line.lstrip(" "))
    prefix = line[:leading_ws]
    cont_prefix = prefix + indent
    words = line[leading_ws:].split(" ")

    def hard_break(word, start_prefix):
        # word itself (plus start_prefix) is wider than max_width_pts: break by character
        pieces = []
        buf = start_prefix
        for ch in word:
            if width(buf + ch) <= max_width_pts or buf == start_prefix:
                buf += ch
            else:
                pieces.append(buf)
                buf = cont_prefix + ch
        pieces.append(buf)
        return pieces

    out_lines = []
    cur = prefix
    for w in words:
        at_line_start = cur in (prefix, cont_prefix)
        candidate = (cur + w) if at_line_start else (cur + " " + w)
        if width(candidate) <= max_width_pts:
            cur = candidate
            continue
        if cur not in (prefix, cont_prefix):
            out_lines.append(cur)
            cur = cont_prefix
        if width(cont_prefix + w) <= max_width_pts:
            cur = cont_prefix + w
        else:
            pieces = hard_break(w, cont_prefix)
            out_lines.extend(pieces[:-1])
            cur = pieces[-1]
    out_lines.append(cur)
    return out_lines


def code_block_markup(raw_code, max_width_pts=None):
    if max_width_pts:
        wrapped = []
        for line in raw_code.split("\n"):
            wrapped.extend(wrap_code_line(line, max_width_pts))
        raw_code = "\n".join(wrapped)
    return sub_and_fallback(xml_escape(raw_code), COURIER_CMAP)


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
styles = {
    "title": ParagraphStyle(
        "title", fontName="TimesCustom-Bold", fontSize=17, leading=20,
        alignment=TA_CENTER, spaceAfter=10,
    ),
    "author": ParagraphStyle(
        "author", fontName="TimesCustom-Bold", fontSize=11.5, leading=14,
        alignment=TA_CENTER, spaceAfter=1,
    ),
    "affil": ParagraphStyle(
        "affil", fontName="TimesCustom", fontSize=10, leading=12.5,
        alignment=TA_CENTER, spaceAfter=1,
    ),
    "subinfo": ParagraphStyle(
        "subinfo", fontName="TimesCustom-Italic", fontSize=8, leading=10,
        alignment=TA_CENTER, textColor=colors.black, spaceBefore=6, spaceAfter=1,
    ),
    "heading1": ParagraphStyle(
        "heading1", fontName="TimesCustom-Bold", fontSize=11.5, leading=14,
        alignment=TA_LEFT, spaceBefore=11, spaceAfter=5,
    ),
    "heading2": ParagraphStyle(
        "heading2", fontName="TimesCustom-BoldItalic", fontSize=10.3, leading=13,
        alignment=TA_LEFT, spaceBefore=8, spaceAfter=4,
    ),
    "abstractLabel": ParagraphStyle(
        "abstractLabel", fontName="TimesCustom-Bold", fontSize=10.3, leading=13,
        alignment=TA_LEFT, spaceBefore=0, spaceAfter=4,
    ),
    "body": ParagraphStyle(
        "body", fontName="TimesCustom", fontSize=9.3, leading=11.4,
        alignment=TA_JUSTIFY, spaceAfter=5.5,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName="TimesCustom", fontSize=9.3, leading=11.4,
        alignment=TA_JUSTIFY, leftIndent=13, spaceAfter=3, bulletIndent=0,
    ),
    "code": ParagraphStyle(
        "code", fontName="CourierCustom", fontSize=7.9, leading=9.6,
        alignment=TA_LEFT, leftIndent=6, spaceBefore=3, spaceAfter=7,
    ),
    "tablecell": ParagraphStyle(
        "tablecell", fontName="TimesCustom", fontSize=8.0, leading=9.6,
        alignment=TA_LEFT,
    ),
    "tablehead": ParagraphStyle(
        "tablehead", fontName="TimesCustom-Bold", fontSize=8.0, leading=9.6,
        alignment=TA_LEFT, textColor=colors.black,
    ),
    "caption": ParagraphStyle(
        "caption", fontName="TimesCustom-Bold", fontSize=8.3, leading=10,
        alignment=TA_LEFT, spaceBefore=4, spaceAfter=3,
    ),
    "reference": ParagraphStyle(
        "reference", fontName="TimesCustom", fontSize=8.3, leading=10.2,
        alignment=TA_LEFT, leftIndent=12, firstLineIndent=-12, spaceAfter=3,
    ),
}


def P(text, style_key="body"):
    return Paragraph(build_markup(text), styles[style_key])


# ---------------------------------------------------------------------------
# Markdown block parser (tailored to this paper's structure)
# ---------------------------------------------------------------------------

def parse_table(lines):
    rows = [ln.strip() for ln in lines if ln.strip()]
    rows = [r for r in rows if not re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$", r)]
    cells = []
    for r in rows:
        r = r.strip()
        if r.startswith("|"):
            r = r[1:]
        if r.endswith("|"):
            r = r[:-1]
        cells.append([c.strip() for c in r.split("|")])
    return cells


def table_flowable(cell_rows, col_width_total):
    from reportlab.pdfbase.pdfmetrics import stringWidth

    ncols = len(cell_rows[0])
    nrows = len(cell_rows)
    cell_pad = 6.5  # left+right padding points

    weights = []
    min_widths = []
    for c in range(ncols):
        col_cells = [cell_rows[r][c] for r in range(nrows)]
        total_len = max(sum(len(c2) for c2 in col_cells), 4)
        weights.append(total_len)

        longest_word = max(
            (len(w) for cell in col_cells for w in re.split(r"[\s/]+", cell) if w),
            default=1,
        )
        longest_word = min(longest_word, 13)  # cap: let Paragraph hard-wrap rare long identifiers
        min_widths.append(stringWidth("M" * longest_word, "TimesCustom-Bold", 8.0) + cell_pad)

    total_min = sum(min_widths)
    if total_min >= col_width_total:
        scale = col_width_total / total_min
        col_widths = [w * scale for w in min_widths]
    else:
        remaining = col_width_total - total_min
        total_w = sum(weights)
        col_widths = [min_widths[c] + remaining * weights[c] / total_w for c in range(ncols)]

    data = []
    for i, row in enumerate(cell_rows):
        style_key = "tablehead" if i == 0 else "tablecell"
        data.append([Paragraph(build_markup(cell), styles[style_key]) for cell in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 1.0, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def build_story(md_path, col_width):
    text = open(md_path, encoding="utf-8").read()
    lines = text.split("\n")

    abstract_idx = next(i for i, ln in enumerate(lines) if ln.strip().lower().startswith("## abstract"))
    front_lines = lines[:abstract_idx]
    body_lines = lines[abstract_idx:]

    # ---- front matter ----
    front = [ln for ln in front_lines if ln.strip() and ln.strip() != "---"]
    title_parts = []
    i = 0
    while i < len(front) and front[i].lstrip().startswith("# "):
        title_parts.append(front[i].lstrip()[2:].strip())
        i += 1
    title_text = " ".join(title_parts)

    front_story = [P(title_text, "title")]
    while i < len(front):
        ln = front[i].strip()
        if ln.startswith("**Target venue") or ln.startswith("**Submission deadline") or ln.startswith("**Page limit"):
            front_story.append(P(ln, "subinfo"))
        elif re.match(r"^\*\*(.+)\*\*$", ln):
            front_story.append(P(re.match(r"^\*\*(.+)\*\*$", ln).group(1), "author"))
        else:
            front_story.append(P(ln, "affil"))
        i += 1

    # ---- body ----
    story = []
    i = 0
    n = len(body_lines)
    while i < n:
        raw = body_lines[i]
        ln = raw.strip()

        if not ln or ln == "---":
            i += 1
            continue

        if ln.startswith("### "):
            story.append(P(ln[4:].strip(), "heading2"))
            i += 1
            continue

        if ln.startswith("## "):
            heading_text = ln[3:].strip()
            if heading_text.lower() == "abstract":
                story.append(P("ABSTRACT", "abstractLabel"))
            elif heading_text.lower() == "references":
                story.append(P("REFERENCES", "heading1"))
            else:
                story.append(P(heading_text, "heading1"))
            i += 1
            continue

        if ln.startswith("```"):
            i += 1
            code_lines = []
            while i < n and not body_lines[i].strip().startswith("```"):
                code_lines.append(body_lines[i])
                i += 1
            i += 1  # skip closing fence
            code_text = "\n".join(code_lines)
            code_max_width = col_width - styles["code"].leftIndent - 6
            story.append(XPreformatted(code_block_markup(code_text, code_max_width), styles["code"]))
            continue

        if ln.startswith("|"):
            table_lines = []
            while i < n and body_lines[i].strip().startswith("|"):
                table_lines.append(body_lines[i])
                i += 1
            cells = parse_table(table_lines)
            story.append(Spacer(1, 3))
            story.append(table_flowable(cells, col_width))
            story.append(Spacer(1, 5))
            continue

        if ln.startswith("- "):
            item_text = ln[2:].strip()
            story.append(Paragraph("&#8226;&nbsp;&nbsp;" + build_markup(item_text), styles["bullet"]))
            i += 1
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", ln)
        if m:
            story.append(Paragraph(f"{m.group(1)}.&nbsp;&nbsp;{build_markup(m.group(2))}", styles["bullet"]))
            i += 1
            continue

        if ln.startswith("[") and re.match(r"^\[\d+\]", ln):
            story.append(P(ln, "reference"))
            i += 1
            continue

        story.append(P(ln, "body"))
        i += 1

    return front_story, story


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("TimesCustom", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawCentredString(LETTER[0] / 2.0, 0.45 * inch, str(doc.page))
    canvas.restoreState()


def main():
    src = sys.argv[1]
    dst = sys.argv[2]

    page_w, page_h = LETTER
    margin = 0.72 * inch
    gutter = 0.28 * inch
    top_margin = 0.72 * inch
    bottom_margin = 0.6 * inch

    content_w = page_w - 2 * margin
    col_w = (content_w - gutter) / 2.0

    title_h = 2.55 * inch
    body_h = page_h - top_margin - bottom_margin - title_h
    col_h_full = page_h - top_margin - bottom_margin

    title_frame = Frame(margin, page_h - top_margin - title_h, content_w, title_h,
                         id="title", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    col1_p1 = Frame(margin, bottom_margin, col_w, body_h, id="c1p1",
                     leftPadding=0, rightPadding=4, topPadding=0, bottomPadding=0)
    col2_p1 = Frame(margin + col_w + gutter, bottom_margin, col_w, body_h, id="c2p1",
                     leftPadding=4, rightPadding=0, topPadding=0, bottomPadding=0)

    col1_full = Frame(margin, bottom_margin, col_w, col_h_full, id="c1",
                       leftPadding=0, rightPadding=4, topPadding=0, bottomPadding=0)
    col2_full = Frame(margin + col_w + gutter, bottom_margin, col_w, col_h_full, id="c2",
                       leftPadding=4, rightPadding=0, topPadding=0, bottomPadding=0)

    doc = BaseDocTemplate(dst, pagesize=LETTER)
    doc.addPageTemplates([
        PageTemplate(id="First", frames=[title_frame, col1_p1, col2_p1], onPage=on_page),
        PageTemplate(id="Later", frames=[col1_full, col2_full], onPage=on_page),
    ])

    front_story, body_story = build_story(src, col_w)

    story = []
    story.append(NextPageTemplate("First"))
    story.extend(front_story)
    story.append(FrameBreak())
    story.append(NextPageTemplate("Later"))
    story.extend(body_story)

    doc.build(story)
    print("wrote", dst)


if __name__ == "__main__":
    main()
