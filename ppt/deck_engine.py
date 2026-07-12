# -*- coding: utf-8 -*-
"""
Reusable slide-deck engine for the low-cost-vitals-triage paper review.
Pure layout/rendering helpers; the actual paper content lives in build_deck.py.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.oxml.ns import qn

# ---------------------------------------------------------------- palette
INK     = RGBColor(0x16, 0x24, 0x33)   # near-black navy (titles)
BODY    = RGBColor(0x33, 0x41, 0x4F)   # body text
MUTED   = RGBColor(0x6B, 0x78, 0x85)   # secondary text
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
BG      = RGBColor(0xFF, 0xFF, 0xFF)
PANEL   = RGBColor(0xF1, 0xF5, 0xF8)   # light panel fill
PANEL2  = RGBColor(0xE7, 0xEF, 0xF3)
PRIMARY = RGBColor(0x10, 0x53, 0x6B)   # deep teal-navy
PRIMD   = RGBColor(0x0A, 0x35, 0x47)   # darker
ACCENT  = RGBColor(0x1F, 0x9E, 0xB3)   # teal
MODEL   = RGBColor(0xE1, 0x7A, 0x2E)   # amber -> trained ML module
MODELBG = RGBColor(0xFB, 0xEC, 0xDC)
GREEN   = RGBColor(0x2F, 0x9E, 0x6A)
AMBER   = RGBColor(0xD9, 0x9A, 0x2B)
RED     = RGBColor(0xC8, 0x45, 0x54)
LINE    = RGBColor(0xD6, 0xDE, 0xE5)

LATIN = "Segoe UI"
EA    = "Microsoft JhengHei"   # Traditional-Chinese friendly (falls back gracefully)

SW, SH = Inches(13.333), Inches(7.5)


def new_deck():
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH
    return prs


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _set_ea(run, name):
    """Force the East-Asian typeface so CJK glyphs use a sensible font."""
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set("typeface", name)


def _font(run, size, color=BODY, bold=False, italic=False, latin=LATIN, ea=EA):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.name = latin
    f.color.rgb = color
    try:
        f.language_id = MSO_LANGUAGE_ID.TRADITIONAL_CHINESE
    except Exception:
        pass
    _set_ea(run, ea)


def rect(slide, l, t, w, h, fill=None, line=None, line_w=1.0, shape=MSO_SHAPE.RECTANGLE,
         shadow=False, radius=None):
    sp = slide.shapes.add_shape(shape, l, t, w, h)
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(line_w)
    sp.shadow.inherit = False
    if shadow:
        _soft_shadow(sp)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sp.adjustments[0] = radius
        except Exception:
            pass
    return sp


def _soft_shadow(sp):
    spPr = sp._element.spPr
    effLst = spPr.makeelement(qn('a:effectLst'), {})
    outer = spPr.makeelement(qn('a:outerShdw'),
                             {'blurRad': '90000', 'dist': '40000', 'dir': '5400000', 'rotWithShape': '0'})
    clr = spPr.makeelement(qn('a:srgbClr'), {'val': '9AA7B2'})
    alpha = spPr.makeelement(qn('a:alpha'), {'val': '38000'})
    clr.append(alpha); outer.append(clr); effLst.append(outer); spPr.append(effLst)


def para(tf, text, size, color=BODY, bold=False, italic=False, align=PP_ALIGN.LEFT,
         space_after=4, space_before=0, bullet=False, level=0, line_spacing=1.06,
         latin=LATIN, ea=EA, first=False):
    p = tf.paragraphs[0] if first and tf.paragraphs[0].text == "" and not tf.paragraphs[0].runs else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    p.level = level
    try:
        p.line_spacing = line_spacing
    except Exception:
        pass
    # segments: list of (text,bold,color) OR plain string
    if isinstance(text, list):
        for seg in text:
            r = p.add_run(); r.text = seg[0]
            _font(r, size, seg[2] if len(seg) > 2 else color, seg[1] if len(seg) > 1 else bold,
                  latin=latin, ea=ea)
    else:
        r = p.add_run(); r.text = text
        _font(r, size, color, bold, italic, latin, ea)
    _bullet_xml(p, bullet, color)
    return p


def _bullet_xml(p, on, color):
    pPr = p._pPr
    if pPr is None:
        pPr = p._p.get_or_add_pPr()
    # clear existing bullet defs
    for tag in ('a:buChar', 'a:buNone', 'a:buAutoNum'):
        e = pPr.find(qn(tag))
        if e is not None:
            pPr.remove(e)
    if on:
        pPr.set('indent', '-137160'); pPr.set('marL', '182880')
        buFont = pPr.makeelement(qn('a:buFont'), {'typeface': 'Arial'})
        buChar = pPr.makeelement(qn('a:buChar'), {'char': '•'})
        pPr.append(buFont); pPr.append(buChar)
    else:
        pPr.append(pPr.makeelement(qn('a:buNone'), {}))


def textbox(slide, l, t, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    return tf


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ---------------------------------------------------------------- composite

def title_bar(slide, kicker, title, num=None):
    """Standard content-slide header: thin accent tab + kicker + title."""
    rect(slide, Inches(0.55), Inches(0.5), Inches(0.09), Inches(0.62), fill=ACCENT)
    tf = textbox(slide, Inches(0.78), Inches(0.42), Inches(11.0), Inches(0.9))
    para(tf, kicker.upper(), 11, ACCENT, bold=True, space_after=2, first=True)
    para(tf, title, 23, INK, bold=True, space_after=0)
    if num is not None:
        tf2 = textbox(slide, Inches(12.2), Inches(6.98), Inches(0.9), Inches(0.3), anchor=MSO_ANCHOR.MIDDLE)
        para(tf2, str(num), 10, MUTED, align=PP_ALIGN.RIGHT, first=True)


def est_text_w_in(text, pt):
    """Rough on-slide text width in inches, accounting for CJK double-width."""
    w = 0.0
    u = pt / 72.0
    for c in text:
        o = ord(c)
        if o > 0x2E80:          # CJK / fullwidth punctuation
            w += u * 1.03
        elif c in "iIlj.,'!|:;":
            w += u * 0.30
        elif c in "mMW@":
            w += u * 0.90
        else:
            w += u * 0.55
    return w


def chip(slide, l, t, text, fill=PANEL2, fg=PRIMARY, w=None, h=Inches(0.32)):
    if w is None:
        w = Inches(est_text_w_in(text, 10.5) + 0.26)
    sp = rect(slide, l, t, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = sp.text_frame; tf.word_wrap = False
    tf.margin_left = Inches(0.06); tf.margin_right = Inches(0.06)
    tf.margin_top = 0; tf.margin_bottom = 0
    para(tf, text, 10.5, fg, bold=True, align=PP_ALIGN.CENTER, first=True)
    return sp, w


def footer(slide, text="低成本設備 × 生命徵象 × 主訴 → 初步檢傷 / 急症判斷"):
    tf = textbox(slide, Inches(0.55), Inches(7.02), Inches(9.5), Inches(0.3))
    para(tf, text, 8.5, MUTED, first=True)


def badge(slide, l, t, label, value, kind="ok", w=Inches(2.55), h=Inches(0.72)):
    """A labeled yes/no style badge. kind: 'ok'(green), 'no'(red), 'warn'(amber), 'info'(teal)."""
    cmap = {"ok": GREEN, "no": RED, "warn": AMBER, "info": ACCENT}
    c = cmap.get(kind, ACCENT)
    sp = rect(slide, l, t, w, h, fill=WHITE, line=c, line_w=1.6,
              shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.14)
    bar = rect(slide, l, t, Inches(0.10), h, fill=c)
    tf = textbox(slide, l + Inches(0.22), t + Inches(0.07), w - Inches(0.3), h - Inches(0.12),
                 anchor=MSO_ANCHOR.MIDDLE)
    para(tf, label, 9.5, MUTED, bold=True, space_after=1, first=True, line_spacing=0.98)
    para(tf, value, 12, c, bold=True, space_after=0, line_spacing=1.0)
    return sp


def callout(slide, l, t, w, h, title, body, accent=ACCENT, fill=None):
    fill = fill if fill is not None else RGBColor(0xED, 0xF6, 0xF8)
    sp = rect(slide, l, t, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    rect(slide, l, t, Inches(0.10), h, fill=accent)
    tf = textbox(slide, l + Inches(0.26), t + Inches(0.14), w - Inches(0.42), h - Inches(0.24))
    if title:
        para(tf, title, 11.5, accent, bold=True, space_after=4, first=True)
        para(tf, body, 11.5, BODY, line_spacing=1.16)
    else:
        para(tf, body, 11.5, BODY, line_spacing=1.16, first=True)
    return sp


def panel_titled(slide, l, t, w, h, title, accent=PRIMARY, fill=PANEL):
    sp = rect(slide, l, t, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
    tf = textbox(slide, l + Inches(0.22), t + Inches(0.14), w - Inches(0.4), Inches(0.4))
    para(tf, title, 12.5, accent, bold=True, first=True)
    return sp, l + Inches(0.22), t + Inches(0.58), w - Inches(0.44)


def section_divider(prs, kicker, title, subtitle, num_label):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=PRIMD)
    rect(s, 0, 0, Inches(0.22), SH, fill=ACCENT)
    # big number
    tf0 = textbox(s, Inches(0.85), Inches(1.5), Inches(4), Inches(2.2))
    para(tf0, num_label, 92, RGBColor(0x22, 0x5A, 0x72), bold=True, first=True)
    tf = textbox(s, Inches(0.9), Inches(3.5), Inches(11.4), Inches(2.4))
    para(tf, kicker, 13, ACCENT, bold=True, space_after=6, first=True)
    para(tf, title, 30, WHITE, bold=True, space_after=10, line_spacing=1.05)
    para(tf, subtitle, 15, RGBColor(0xC9, 0xDD, 0xE6), line_spacing=1.2)
    return s


def flow_snake(slide, left, top, width, labels, model_labels, details=None,
               box_h=Inches(1.02), gap=Inches(0.30), max_cols=5):
    """Draw a snaking left->right / right->left flow of rounded boxes with arrows.
    Trained-model steps are highlighted in amber."""
    details = details or {}
    model_set = set(model_labels or [])
    n = len(labels)
    cols = min(max_cols, n)
    import math
    rows = math.ceil(n / cols)
    total_gap = gap * (cols - 1)
    box_w = int((width - total_gap) / cols)
    positions = []  # (x,y,row,col_visual)
    for i in range(n):
        row = i // cols
        col_in_row = i % cols
        # snake: even rows L->R, odd rows R->L
        visual_col = col_in_row if row % 2 == 0 else (cols - 1 - col_in_row)
        # last row may be short; keep its own count for centering
        x = left + visual_col * (box_w + gap)
        y = top + row * (box_h + Inches(0.62))
        positions.append((x, y, row, visual_col))

    # draw boxes
    for i, lab in enumerate(labels):
        x, y, row, vc = positions[i]
        is_model = lab in model_set
        fill = MODELBG if is_model else PANEL
        edge = MODEL if is_model else ACCENT
        sp = rect(slide, x, y, box_w, box_h, fill=fill, line=edge, line_w=1.4,
                  shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
        tf = sp.text_frame; tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.08); tf.margin_right = Inches(0.08)
        tf.margin_top = Inches(0.03); tf.margin_bottom = Inches(0.03)
        para(tf, f"{i+1}. {lab}", 11, INK, bold=True, align=PP_ALIGN.CENTER,
             space_after=1, first=True, line_spacing=1.0)
        d = details.get(lab)
        if d:
            para(tf, d, 8.3, MUTED, align=PP_ALIGN.CENTER, space_after=0, line_spacing=0.98)
        if is_model:
            # tiny "AI" tag
            tag = rect(slide, x + box_w - Inches(0.42), y - Inches(0.10), Inches(0.44), Inches(0.22),
                       fill=MODEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
            ttf = tag.text_frame; ttf.margin_left=0; ttf.margin_right=0; ttf.margin_top=0; ttf.margin_bottom=0
            para(ttf, "模型", 8, WHITE, bold=True, align=PP_ALIGN.CENTER, first=True)

    # draw arrows between consecutive boxes
    for i in range(n - 1):
        x0, y0, r0, vc0 = positions[i]
        x1, y1, r1, vc1 = positions[i + 1]
        if r0 == r1:
            # horizontal arrow in the gap
            if vc1 > vc0:  # rightward
                ax = x0 + box_w; aw = gap
                _arrow(slide, ax, y0 + box_h/2 - Inches(0.09), aw, Inches(0.18), MSO_SHAPE.RIGHT_ARROW)
            else:  # leftward
                ax = x1 + box_w; aw = gap
                _arrow(slide, ax, y0 + box_h/2 - Inches(0.09), aw, Inches(0.18), MSO_SHAPE.LEFT_ARROW)
        else:
            # wrap: down arrow under box i (same visual col as i)
            ax = x0 + box_w/2 - Inches(0.09)
            ay = y0 + box_h
            _arrow(slide, ax, ay, Inches(0.18), Inches(0.62), MSO_SHAPE.DOWN_ARROW)


def _arrow(slide, l, t, w, h, shape):
    sp = rect(slide, l, t, w, h, fill=ACCENT, shape=shape)
    return sp


def simple_table(slide, left, top, col_w, headers, rows, header_fill=PRIMARY,
                 row_h=Inches(0.42), header_h=Inches(0.44), fs=9.5, hfs=10):
    """Lightweight banded table drawn from shapes (full control over styling)."""
    x = left
    xs = [left]
    for w in col_w:
        xs.append(xs[-1] + w)
    total_w = xs[-1] - left
    # header
    for j, htext in enumerate(headers):
        cell = rect(slide, xs[j], top, col_w[j], header_h, fill=header_fill,
                    line=WHITE, line_w=1.0)
        tf = cell.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        tf.margin_left = Inches(0.06); tf.margin_right = Inches(0.05)
        tf.margin_top = 0; tf.margin_bottom = 0
        para(tf, htext, hfs, WHITE, bold=True, align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER, first=True, line_spacing=0.98)
    # body
    y = top + header_h
    for ri, row in enumerate(rows):
        fill = WHITE if ri % 2 == 0 else PANEL
        rh = row_h if not isinstance(row, tuple) else row[1]
        cells = row if not isinstance(row, tuple) else row[0]
        for j, ctext in enumerate(cells):
            cell = rect(slide, xs[j], y, col_w[j], rh, fill=fill, line=LINE, line_w=0.75)
            tf = cell.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.word_wrap = True
            tf.margin_left = Inches(0.06); tf.margin_right = Inches(0.05)
            tf.margin_top = Inches(0.02); tf.margin_bottom = Inches(0.02)
            first = True
            segs = ctext if isinstance(ctext, list) else [ctext]
            for k, s in enumerate(segs):
                para(tf, s, fs, BODY, align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.LEFT,
                     first=first, space_after=0, line_spacing=0.98,
                     bold=(j == 0 and k == 0))
                first = False
        y += rh
    return y
