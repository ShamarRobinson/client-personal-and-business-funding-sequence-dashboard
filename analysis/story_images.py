"""Infographic images for the Tableau Story (rendered as PNG so they look the same on Tableau Public).

Style: a data-model aesthetic. Entities are white cards with a colored header strip, field rows in a
monospace face, thin orthogonal connectors and a dot-grid canvas. Each bureau keeps one color
everywhere: Experian blue, Equifax orange, TransUnion green, and bureau names are bold in that color.
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "tableau" / "_images"
S = 2  # 2x for sharp text
INTER = Path("/usr/share/fonts/opentype/inter")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# Theme: dark "metal card" look taken from the cover photo: near-black canvas, charcoal cards,
# teal and orange edge glows for chrome. Bureau colors stay unique and are lifted for a dark background.
BUREAU = {"Experian": "#4C8DF0", "Equifax": "#F07A3A", "TransUnion": "#2EBF86"}
TINT = {"Experian": "#16263F", "Equifax": "#3A2318", "TransUnion": "#12301F"}
INK, INK2, MUTED, LINE, CANVAS, NAVY = "#F2EFE8", "#C3C8D0", "#8C94A1", "#2E3540", "#0E1115", "#FFFFFF"
NEUTRAL = "#2A3240"
CARD, CARD2, TRACK, GRID = "#161A20", "#1C2129", "#262C35", "#1F242C"
BG = "#07090C"
TEAL, ORANGE = "#2FD4C4", "#FF8A2A"
BW = re.compile(r"(Experian|Equifax|TransUnion)")


def f(weight, size):
    name = {"regular": "Inter-Regular.otf", "medium": "Inter-Medium.otf", "semibold": "Inter-SemiBold.otf", "bold": "Inter-Bold.otf"}[weight]
    return ImageFont.truetype(str(INTER / name), int(size * S))


def mono(size, bold=False):
    return ImageFont.truetype(MONO_B if bold else MONO, int(size * S))


def canvas(w, h, grid=True, bg=CANVAS):
    im = Image.new("RGB", (w * S, h * S), bg)
    d = ImageDraw.Draw(im)
    if grid:
        for x in range(0, w * S, 16 * S):
            for y in range(0, h * S, 16 * S):
                d.point((x, y), fill=GRID)
    return im, d


def rich_words(text):
    """Split text into (word, is_bureau) tokens, keeping punctuation attached to words."""
    out = []
    for w in text.split():
        m = BW.search(w)
        out.append((w, bool(m)))
    return out


def draw_rich(d, x, y, width, text, size=10, weight="regular", color=INK2, align="left", line_gap=4, lead=None):
    """Wrap and draw text, with bureau names bold in their color. An optional lead (e.g. 'Sources:') is drawn bold in INK.
    Returns the y after the last line."""
    fr, fb = f(weight, size), f("bold", size)
    words = [(w, "lead") for w in (lead or "").split()] + [(w, "b" if BW.search(w) else None) for w in text.split()]
    lines, cur, cw = [], [], 0
    space = d.textlength(" ", font=fr)
    for w, k in words:
        wl = d.textlength(w, font=fb if k else fr)
        if cur and cw + space + wl > width:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (space if cur else 0) + wl
        cur.append((w, k, wl))
    if cur:
        lines.append((cur, cw))
    lh = fr.getbbox("Ag")[3] + line_gap * S
    for ln, lw in lines:
        xx = x + (width - lw) / 2 if align == "center" else x
        for w, k, wl in ln:
            if k == "b":
                m = BW.search(w)
                pre, word, post = w[:m.start()], m.group(1), w[m.end():]
                if pre:
                    d.text((xx, y), pre, font=fr, fill=color); xx += d.textlength(pre, font=fr)
                d.text((xx, y), word, font=fb, fill=BUREAU[word]); xx += d.textlength(word, font=fb)
                if post:
                    d.text((xx, y), post, font=fr, fill=color); xx += d.textlength(post, font=fr)
            elif k == "lead":
                d.text((xx, y), w, font=fb, fill=INK); xx += wl
            else:
                d.text((xx, y), w, font=fr, fill=color); xx += wl
            xx += space
        y += lh
    return y


def text_height(d, width, text, size=10, weight="regular", line_gap=4):
    im = Image.new("RGB", (10, 10)); dd = ImageDraw.Draw(im)
    return draw_rich(dd, 0, 0, width, text, size, weight, line_gap=line_gap)


def entity(d, box, title, fields=(), head=NEUTRAL, head_ink="#FFFFFF", key="◆", fsize=9, title_size=10, body=None):
    """A data-model entity: header strip plus monospace field rows (name, value) or a rich body text."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=0, fill=CARD, outline=LINE, width=1 * S)
    hh = 26 * S
    d.rounded_rectangle((x0, y0, x1, y0 + hh), radius=0, fill=head)
    d.rectangle((x0, y0 + hh - 6 * S, x1, y0 + hh), fill=head)
    d.text((x0 + 10 * S, y0 + 6 * S), f"{key} {title}", font=f("bold", title_size), fill=head_ink)
    y = y0 + hh + 8 * S
    for name, val in fields:
        d.text((x0 + 10 * S, y), name, font=mono(fsize), fill=MUTED)
        nx = x0 + 10 * S + d.textlength(name + "  ", font=mono(fsize))
        y = draw_rich(d, nx, y, x1 - nx - 10 * S, val, size=fsize + 0.5, weight="medium", color=INK) + 2 * S
    if body:
        draw_rich(d, x0 + 10 * S, y, x1 - x0 - 20 * S, body, size=fsize + 0.5, color=INK2)
    return y


def elbow(d, x0, y0, x1, y1, color="#8A93A3", dash=False, arrow=True):
    """Orthogonal connector: down, across, down, with a small arrowhead."""
    ym = (y0 + y1) / 2
    pts = [(x0, y0), (x0, ym), (x1, ym), (x1, y1)]
    for a, b in zip(pts, pts[1:]):
        if dash:
            n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) / (6 * S)) or 1
            for k in range(0, n, 2):
                p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                q = (a[0] + (b[0] - a[0]) * min(k + 1, n) / n, a[1] + (b[1] - a[1]) * min(k + 1, n) / n)
                d.line((p, q), fill=color, width=int(1.5 * S))
        else:
            d.line((a, b), fill=color, width=int(1.5 * S))
    if arrow:
        d.polygon([(x1, y1), (x1 - 4 * S, y1 - 7 * S), (x1 + 4 * S, y1 - 7 * S)], fill=color)


def pill(d, cx, cy, text, color=NEUTRAL, fill=CARD):
    ft = mono(8, True)
    w = d.textlength(text, font=ft) + 12 * S
    d.rounded_rectangle((cx - w / 2, cy - 9 * S, cx + w / 2, cy + 9 * S), radius=9 * S, fill=fill, outline=color, width=1 * S)
    d.text((cx - w / 2 + 6 * S, cy - 6 * S), text, font=ft, fill=color)


def save(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.png"
    im.save(p)
    return p


# ---------------------------------------------------------------- 1. roadmap (introduction)
def roadmap(w, h, steps):
    im, d = canvas(w, h)
    d.text((10 * S, 8 * S), "How the Story Unfolds", font=f("bold", 13), fill=NAVY)
    d.text((10 * S, 28 * S), "Read top to bottom; each step is one or more story points", font=f("regular", 9), fill=MUTED)
    top, n, gap = 50 * S, len(steps), 10 * S
    bh = (h * S - top - 8 * S - gap * (n - 1)) / n
    for i, (pts, title, line, head) in enumerate(steps):
        y0 = top + i * (bh + gap)
        box = (10 * S, y0, w * S - 10 * S, y0 + bh)
        d.rounded_rectangle(box, radius=0, fill=CARD, outline=LINE, width=1 * S)
        d.rounded_rectangle((box[0], y0, box[0] + 6 * S, y0 + bh), radius=3 * S, fill=head)
        d.text((box[0] + 16 * S, y0 + 6 * S), pts, font=mono(8, True), fill=MUTED)
        d.text((box[0] + 16 * S, y0 + 19 * S), title, font=f("semibold", 11), fill=INK)
        draw_rich(d, box[0] + 16 * S, y0 + 36 * S, box[2] - box[0] - 26 * S, line, size=8.5, color=INK2, line_gap=2)
        if i < n - 1:
            x = w * S / 2
            d.line((x, y0 + bh, x, y0 + bh + gap), fill="#8A93A3", width=int(1.5 * S))
    return save(im, "info_roadmap")


# ---------------------------------------------------------------- 2. market chart
def market_chart(w, h, shares, top_counts, total):
    im, d = canvas(w, h, grid=False, bg=CARD)
    d.text((10 * S, 8 * S), "Share of All Recorded Pulls, by Bureau", font=f("bold", 13), fill=NAVY)
    d.text((10 * S, 28 * S), f"{total:,} bureau pulls across 49 states and DC, all lenders combined", font=f("regular", 9), fill=MUTED)
    y = 54 * S
    lab_w = 100 * S
    maxw = w * S - lab_w - 120 * S
    for b, (n, p) in shares.items():
        d.text((10 * S, y + 6 * S), b, font=f("bold", 12), fill=BUREAU[b])
        d.rectangle((lab_w, y, lab_w + maxw, y + 40 * S), fill=TRACK)
        d.rectangle((lab_w, y, lab_w + maxw * p, y + 40 * S), fill=BUREAU[b])
        d.text((lab_w + maxw * p + 8 * S, y + 4 * S), f"{p:.0%}", font=f("bold", 16), fill=INK)
        d.text((lab_w + maxw * p + 8 * S, y + 25 * S), f"{n:,} pulls", font=f("regular", 8.5), fill=MUTED)
        y += 56 * S
    y += 8 * S
    d.line((10 * S, y, w * S - 10 * S, y), fill=LINE, width=1 * S)
    y += 10 * S
    d.text((10 * S, y), "Top Bureau by State (49 states and DC with data)", font=f("bold", 11), fill=NAVY)
    y += 22 * S
    x = 10 * S
    for name, cnt, col in top_counts:
        tw = (w * S - 20 * S - 3 * 8 * S) / 4
        d.rounded_rectangle((x, y, x + tw, y + 56 * S), radius=0, fill=CARD, outline=LINE, width=1 * S)
        d.rectangle((x, y + 4 * S, x + 4 * S, y + 52 * S), fill=col)
        d.text((x + 12 * S, y + 4 * S), str(cnt), font=f("bold", 20), fill=col if col != "#9AA3B2" else INK)
        d.text((x + 12 * S, y + 36 * S), name, font=f("semibold", 9), fill=INK2)
        x += tw + 8 * S
    return save(im, "info_market")


def fact_tiles(w, h, facts):
    im, d = canvas(w, h)
    d.text((10 * S, 8 * S), "Why the Bureau Matters", font=f("bold", 13), fill=NAVY)
    top, n, gap = 34 * S, len(facts), 8 * S
    bh = (h * S - top - 6 * S - gap * (n - 1)) / n
    for i, (big, text, src) in enumerate(facts):
        y0 = top + i * (bh + gap)
        box = (10 * S, y0, w * S - 10 * S, y0 + bh)
        d.rounded_rectangle(box, radius=0, fill=CARD, outline=LINE, width=1 * S)
        d.text((box[0] + 12 * S, y0 + 8 * S), big, font=f("bold", 17), fill=NAVY)
        bw = d.textlength(big, font=f("bold", 17)) + 22 * S
        yy = draw_rich(d, box[0] + bw, y0 + 9 * S, box[2] - box[0] - bw - 12 * S, text, size=9, color=INK2, line_gap=2)
        d.text((box[0] + bw, max(yy, y0 + bh - 18 * S)), src, font=mono(7.5), fill=MUTED)
    return save(im, "info_facts")


# ---------------------------------------------------------------- 3. KPI tiles
def kpi_tiles(w, h, title, sub, tiles, name):
    im, d = canvas(w, h, grid=False, bg=CARD)
    d.text((8 * S, 4 * S), title, font=f("bold", 12), fill=NAVY)
    d.text((8 * S, 22 * S), sub, font=f("regular", 8.5), fill=MUTED)
    top, n, gap = 40 * S, len(tiles), 8 * S
    tw = (w * S - 16 * S - gap * (n - 1)) / n
    for i, (lab, val, ctx, col) in enumerate(tiles):
        x0 = 8 * S + i * (tw + gap)
        box = (x0, top, x0 + tw, h * S - 4 * S)
        d.rounded_rectangle(box, radius=0, fill=CARD, outline=LINE, width=1 * S)
        d.rectangle((x0, top + 6 * S, x0 + 4 * S, h * S - 10 * S), fill=col)
        d.text((x0 + 12 * S, top + 6 * S), lab, font=mono(7.5, True), fill=MUTED)
        d.text((x0 + 12 * S, top + 20 * S), val, font=f("bold", 18), fill=col if col in BUREAU.values() else INK)
        draw_rich(d, x0 + 12 * S, top + 46 * S, tw - 20 * S, ctx, size=8, color=INK2, line_gap=1)
    return save(im, name)


# ---------------------------------------------------------------- 4. decision tree (data-model style)
def decision_tree(w, h, branches, overrides, name="info_tree"):
    im, d = canvas(w, h)
    d.text((10 * S, 8 * S), "Decision Tree: Start From Your Strongest Report", font=f("bold", 13), fill=NAVY)
    d.text((10 * S, 28 * S), "IF a report is strongest, THEN favor the issuers that pull it. Override rules apply first.", font=f("regular", 9), fill=MUTED)
    W = w * S
    root = (W / 2 - 150 * S, 48 * S, W / 2 + 150 * S, 118 * S)
    entity(d, root, "START: strongest_report", [("check", "pull all three reports, compare scores and errors"), ("then", "follow the branch for the strongest report")], head=NEUTRAL)
    colw, gap = (W - 20 * S - 2 * 24 * S) / 3, 24 * S
    by0, by1 = 168 * S, 168 * S + 112 * S
    for i, (b, why, then, ex) in enumerate(branches):
        x0 = 10 * S + i * (colw + gap)
        box = (x0, by0, x0 + colw, by1)
        cx = x0 + colw / 2
        elbow(d, W / 2, root[3], cx, by0)
        pill(d, cx, by0 - 18 * S, f"IF {b.upper()} IS STRONGEST", color=BUREAU[b])
        entity(d, box, f"THEN {then}", [("why", why)] + ex, head=BUREAU[b])
    # override rules: one entity row along the bottom, linked with a dashed line
    oy0 = by1 + 44 * S
    ow = (W - 20 * S - 2 * 16 * S) / 3
    d.line((10 * S, oy0 - 22 * S, W - 10 * S, oy0 - 22 * S), fill=LINE, width=1 * S)
    pill(d, W / 2, oy0 - 22 * S, "OVERRIDES: CHECK THESE FIRST", color="#5B3FA8")
    for i, (cond, act) in enumerate(overrides):
        x0 = 10 * S + i * (ow + 16 * S)
        entity(d, (x0, oy0, x0 + ow, h * S - 8 * S), f"IF {cond}", [("then", act)], head="#5B3FA8")
    return save(im, name)


def whatif_table(w, h, rows, compact=False, name="info_whatif"):
    """An entity table: header, mono column names, one row per case, with a stacked chance bar."""
    im, d = canvas(w, h)
    x0, y0, x1, y1 = 10 * S, 8 * S, w * S - 10 * S, h * S - 8 * S
    d.rounded_rectangle((x0, y0, x1, y1), radius=0, fill=CARD, outline=LINE, width=1 * S)
    hh = 26 * S
    d.rounded_rectangle((x0, y0, x1, y0 + hh), radius=0, fill=NEUTRAL)
    d.rectangle((x0, y0 + hh - 6 * S, x1, y0 + hh), fill=NEUTRAL)
    d.text((x0 + 10 * S, y0 + 6 * S), "◆ WHAT_IF: model's best forecast, four real cases" if compact else "◆ WHAT_IF: model's best forecast for four real cases (typical application)", font=f("bold", 10), fill="#FFFFFF")
    cols = ([("lender_in_state", 0.36), ("forecast", 0.22), ("chance_by_bureau", 0.42), ("", 0.0)] if compact else
            [("lender_in_state", 0.20), ("likely_bureau", 0.17), ("chance_by_bureau", 0.33), ("why_it_matters", 0.30)])
    cx = [x0 + 10 * S]
    for _, fr in cols:
        cx.append(cx[-1] + fr * (x1 - x0 - 20 * S))
    y = y0 + hh + 6 * S
    for (cname, _), x in zip(cols, cx):
        d.text((x, y), cname, font=mono(8, True), fill=MUTED)
    y += 18 * S
    d.line((x0, y, x1, y), fill=LINE, width=1 * S)
    rh = (y1 - y - 4 * S) / len(rows)
    for i, (case, lead, probs, why) in enumerate(rows):
        ry = y + i * rh
        if i % 2:
            d.rectangle((x0 + 1 * S, ry, x1 - 1 * S, ry + rh), fill=CARD2)
        mid = ry + rh / 2
        d.text((cx[0], mid - 8 * S), case, font=f("semibold", 10), fill=INK)
        d.text((cx[1], mid - 8 * S), lead, font=f("bold", 10), fill=BUREAU[lead])
        # stacked bar in bureau colors
        bx, bw = cx[2], (cx[3] if not compact else x1 - 10 * S) - cx[2] - 16 * S
        xx = bx
        for b in ("Experian", "Equifax", "TransUnion"):
            seg = bw * probs[b]
            d.rectangle((xx, mid - 9 * S, xx + seg, mid + 9 * S), fill=BUREAU[b])
            if probs[b] >= 0.12:
                d.text((xx + 4 * S, mid - 6 * S), f"{probs[b]:.0%}", font=f("bold", 8.5), fill="#FFFFFF")
            xx += seg
        if not compact:
            draw_rich(d, cx[3], mid - 12 * S, x1 - cx[3] - 10 * S, why, size=8.5, color=INK2, line_gap=1)
        d.line((x0, ry + rh, x1, ry + rh), fill=TRACK, width=1 * S)
    # legend
    lx = x1 - 10 * S
    if compact:
        return save(im, name)
    for b in ("TransUnion", "Equifax", "Experian"):
        tw = d.textlength(b, font=f("bold", 8.5))
        lx -= tw + 18 * S
        d.rectangle((lx, y0 + hh + 9 * S, lx + 9 * S, y0 + hh + 18 * S), fill=BUREAU[b])
        d.text((lx + 12 * S, y0 + hh + 7 * S), b, font=f("bold", 8.5), fill=BUREAU[b])
    return save(im, name)


# ---------------------------------------------------------------- 5. pipeline (sources card)
def pipeline(w, h, steps):
    im, d = canvas(w, h)
    d.text((10 * S, 6 * S), "How Every Number Is Made", font=f("bold", 12), fill=NAVY)
    top, n, gap = 28 * S, len(steps), 22 * S
    bw = (w * S - 20 * S - gap * (n - 1)) / n
    for i, (t, line) in enumerate(steps):
        x0 = 10 * S + i * (bw + gap)
        box = (x0, top, x0 + bw, h * S - 6 * S)
        entity(d, box, t, body=line, head=NEUTRAL, fsize=8, title_size=9)
        if i < n - 1:
            ym = (top + h * S) / 2
            d.line((x0 + bw + 3 * S, ym, x0 + bw + gap - 4 * S, ym), fill="#8A93A3", width=int(1.5 * S))
            d.polygon([(x0 + bw + gap - 3 * S, ym), (x0 + bw + gap - 10 * S, ym - 4 * S), (x0 + bw + gap - 10 * S, ym + 4 * S)], fill="#8A93A3")
    return save(im, "info_pipe")


# ---------------------------------------------------------------- 6. bureau groups (recommendations)
def bureau_groups(w, h, groups):
    im, d = canvas(w, h)
    d.text((10 * S, 8 * S), "Spread Applications Across Bureau Groups", font=f("bold", 12), fill=NAVY)
    d.text((10 * S, 26 * S), "One lender from each group per round keeps any single report from stacking up", font=f("regular", 8.5), fill=MUTED)
    top, n, gap = 46 * S, len(groups), 10 * S
    bw = (w * S - 20 * S - gap * (n - 1)) / n
    for i, (b, lenders) in enumerate(groups):
        x0 = 10 * S + i * (bw + gap)
        head = BUREAU.get(b, NEUTRAL)
        entity(d, (x0, top, x0 + bw, h * S - 8 * S), b, [(f"{k+1:02d}", l) for k, l in enumerate(lenders)], head=head, fsize=8, title_size=9)
    return save(im, "info_groups")


# ---------------------------------------------------------------- 7. stakeholders and scope
def stakeholders(w, h, primary, secondary):
    im, d = canvas(w, h, grid=False, bg=CARD)
    d.text((8 * S, 4 * S), "Who This Serves", font=f("bold", 12), fill=NAVY)
    top, gap = 26 * S, 10 * S
    n = len(primary)
    cw = (w * S - 16 * S - gap * (n - 1)) / n
    rh = (h * S - top - 8 * S - gap) * 0.58
    for i, (t, line) in enumerate(primary):
        x0 = 8 * S + i * (cw + gap)
        box = (x0, top, x0 + cw, top + rh)
        d.rounded_rectangle(box, radius=0, fill=CARD, outline=LINE, width=1 * S)
        d.rectangle((x0, top, x0 + cw, top + 4 * S), fill=NAVY)
        d.text((x0 + 12 * S, top + 12 * S), "PRIMARY", font=mono(7.5, True), fill=MUTED)
        d.text((x0 + 12 * S, top + 26 * S), t, font=f("semibold", 11), fill=INK)
        draw_rich(d, x0 + 12 * S, top + 46 * S, cw - 24 * S, line, size=9, color=INK2, line_gap=2)
    y2 = top + rh + gap
    for i, (t, line) in enumerate(secondary):
        x0 = 8 * S + i * (cw + gap)
        box = (x0, y2, x0 + cw, h * S - 8 * S)
        d.rounded_rectangle(box, radius=0, fill=CARD2, outline=LINE, width=1 * S)
        d.text((x0 + 12 * S, y2 + 8 * S), t, font=f("semibold", 10), fill=INK)
        draw_rich(d, x0 + 12 * S, y2 + 26 * S, cw - 24 * S, line, size=8.5, color=INK2, line_gap=2)
    return save(im, "info_stakeholders")


def scope(w, h, ins, outs):
    im, d = canvas(w, h, grid=False, bg=CARD)
    gap = 14 * S
    cw = (w * S - 16 * S - gap) / 2
    for k, (label, items, col, mark) in enumerate([("IN SCOPE: what this story answers", ins, "#2E6CA8", "✓"),
                                                   ("OUT OF SCOPE: what it does not try to answer", outs, "#8A93A3", "✕")]):
        x0 = 8 * S + k * (cw + gap)
        d.text((x0, 4 * S), label, font=f("bold", 11), fill=col if k == 0 else INK2)
        d.line((x0, 24 * S, x0 + cw, 24 * S), fill=col, width=2 * S)
        rh = (h * S - 32 * S) / len(items)
        for r, (t, line) in enumerate(items):
            y = 30 * S + r * rh
            d.text((x0, y + 2 * S), mark, font=f("bold", 11), fill=col)
            d.text((x0 + 18 * S, y), t, font=f("semibold", 10), fill=INK)
            draw_rich(d, x0 + 18 * S, y + 17 * S, cw - 20 * S, line, size=8.5, color=INK2, line_gap=1)
            if r < len(items) - 1:
                d.line((x0 + 18 * S, y + rh - 4 * S, x0 + cw, y + rh - 4 * S), fill=TRACK, width=1 * S)
    return save(im, "info_scope")


# ---------------------------------------------------------------- 8. data and method
def flow(w, h, title, steps, name, result_head=None):
    im, d = canvas(w, h)
    d.text((10 * S, 6 * S), title, font=f("bold", 12), fill=NAVY)
    top, n, gap = 28 * S, len(steps), 22 * S
    bw = (w * S - 20 * S - gap * (n - 1)) / n
    for i, (t, fields) in enumerate(steps):
        x0 = 10 * S + i * (bw + gap)
        head = result_head if (result_head and i == n - 1) else NEUTRAL
        entity(d, (x0, top, x0 + bw, h * S - 6 * S), t, fields, head=head, fsize=8, title_size=9)
        if i < n - 1:
            ym = top + 13 * S
            d.line((x0 + bw + 3 * S, ym, x0 + bw + gap - 4 * S, ym), fill="#8A93A3", width=int(1.5 * S))
            d.polygon([(x0 + bw + gap - 3 * S, ym), (x0 + bw + gap - 10 * S, ym - 4 * S), (x0 + bw + gap - 10 * S, ym + 4 * S)], fill="#8A93A3")
    return save(im, name)


# ---------------------------------------------------------------- 9. share equation
def equation(w, h, examples):
    im, d = canvas(w, h, grid=False, bg=CARD)
    # the rule, written as an equation
    y = 8 * S
    parts = [("Pulls on one bureau in a state", INK), (" ÷ ", MUTED), ("All bureau pulls in that state", INK), (" = ", MUTED), ("Bureau share", "#2E6CA8")]
    tw = sum(d.textlength(t, font=f("bold", 15)) for t, _ in parts)
    x = (w * S - tw) / 2
    for t, c in parts:
        d.text((x, y), t, font=f("bold", 15), fill=c); x += d.textlength(t, font=f("bold", 15))
    d.text((w * S / 2 - d.textlength("The same rule colors every state on the next three maps", font=f("regular", 9)) / 2, y + 26 * S),
           "The same rule colors every state on the next three maps", font=f("regular", 9), fill=MUTED)
    y += 54 * S
    d.line((8 * S, y, w * S - 8 * S, y), fill=LINE, width=1 * S)
    rh = (h * S - y - 6 * S) / len(examples)
    for i, (state, b, n, tot, counts, note) in enumerate(examples):
        ry = y + i * rh + 8 * S
        d.text((8 * S, ry), state, font=f("bold", 12), fill=INK)
        eq = f"{n} ÷ {tot} = {n / tot:.0%}"
        d.text((8 * S, ry + 20 * S), b, font=f("bold", 10), fill=BUREAU[b])
        d.text((8 * S + d.textlength(b + "  ", font=f("bold", 10)), ry + 20 * S), eq, font=mono(10, True), fill=INK)
        d.text((8 * S, ry + 38 * S), note, font=f("regular", 8.5), fill=MUTED)
        # stacked bar of all three shares
        bx, bw = 300 * S, w * S - 320 * S
        xx = bx
        for bb in ("Experian", "Equifax", "TransUnion"):
            p = counts[bb] / tot
            seg = bw * p
            d.rectangle((xx, ry + 6 * S, xx + seg, ry + 34 * S), fill=BUREAU[bb] if bb == b else TINT[bb])
            if p >= 0.1:
                d.text((xx + 6 * S, ry + 12 * S), f"{bb[:2].upper() if bb != 'TransUnion' else 'TU'} {p:.0%}", font=f("bold", 9), fill="#FFFFFF" if bb == b else BUREAU[bb])
            xx += seg
        if i < len(examples) - 1:
            d.line((8 * S, y + (i + 1) * rh, w * S - 8 * S, y + (i + 1) * rh), fill=TRACK, width=1 * S)
    return save(im, "info_equation")


# ---------------------------------------------------------------- 10. funding ladder
def ladder(w, h, tiers, name="info_ladder"):
    im, d = canvas(w, h, grid=False, bg=CARD)
    n = len(tiers)
    ramp = ["#16302F", "#1A4542", "#1D5B56", "#21716A", "#25877E", "#2A9E93", "#2FB4A7"]
    gap = 8 * S
    cw = (w * S - 16 * S - gap * (n - 1)) / n
    base = h * S - 70 * S          # bottom of the risers; the "do this" text sits below
    step = (base - 70 * S) / n
    for i, (rng, head, do) in enumerate(tiers):
        x0 = 8 * S + i * (cw + gap)
        top = base - step * (i + 1)
        d.rectangle((x0, top, x0 + cw, base), fill=ramp[i])
        d.rectangle((x0, top, x0 + cw, top + 3 * S), fill=ORANGE if i == n - 1 else TEAL)
        d.text((x0, top - 40 * S), rng, font=mono(11, True), fill=NAVY)
        d.text((x0, top - 22 * S), head, font=f("semibold", 10), fill=INK)
        d.text((x0 + 6 * S, base - 22 * S), f"STEP {i + 1}", font=mono(8, True), fill="#FFFFFF")
        draw_rich(d, x0, base + 8 * S, cw, do, size=8.5, color=INK2, line_gap=1)
    d.line((8 * S, base, w * S - 8 * S, base), fill=LINE, width=1 * S)
    d.text((10 * S, 8 * S), "The Funding Ladder", font=f("bold", 13), fill=INK)
    d.text((10 * S, 28 * S), "One score step at a time", font=f("regular", 9), fill=MUTED)
    return save(im, name)


# ---------------------------------------------------------------- 11. scorecard
def scorecard(w, h, bans, issuers):
    im, d = canvas(w, h, grid=False, bg=CARD)
    n, gap = len(bans), 8 * S
    tw = (w * S - 16 * S - gap * (n - 1)) / n
    th = 78 * S
    for i, (val, lab, col) in enumerate(bans):
        x0 = 8 * S + i * (tw + gap)
        d.rounded_rectangle((x0, 4 * S, x0 + tw, 4 * S + th), radius=0, fill=CARD, outline=LINE, width=1 * S)
        d.text((x0 + 12 * S, 12 * S), val, font=f("bold", 24), fill=col)
        draw_rich(d, x0 + 12 * S, 46 * S, tw - 22 * S, lab, size=8.5, color=INK2, line_gap=1)
    y = 4 * S + th + 18 * S
    d.text((8 * S, y), "Each Issuer's Bureau Habit", font=f("bold", 12), fill=NAVY)
    d.text((8 * S, y + 18 * S), "Share of each issuer's recorded pulls. A long segment means a predictable issuer.", font=f("regular", 8.5), fill=MUTED)
    # legend
    lx = w * S - 8 * S
    for b in ("TransUnion", "Equifax", "Experian"):
        t = d.textlength(b, font=f("bold", 9)); lx -= t + 20 * S
        d.rectangle((lx, y + 3 * S, lx + 10 * S, y + 13 * S), fill=BUREAU[b]); d.text((lx + 13 * S, y), b, font=f("bold", 9), fill=BUREAU[b])
    y += 46 * S
    lab_w, bx = 130 * S, 146 * S
    bw = w * S - bx - 16 * S
    rh = (h * S - y - 8 * S) / len(issuers)
    for i, (name, sh) in enumerate(issuers):
        ry = y + i * rh
        bh = min(22 * S, rh - 6 * S)
        d.text((8 * S, ry + (bh - 14 * S) / 2), name, font=f("semibold" if name != "All lenders" else "bold", 10), fill=INK)
        xx = bx
        for b in ("Experian", "Equifax", "TransUnion"):
            seg = bw * sh[b]
            d.rectangle((xx, ry, xx + seg - 1 * S, ry + bh), fill=BUREAU[b])
            if sh[b] >= 0.07:
                d.text((xx + 5 * S, ry + (bh - 12 * S) / 2), f"{sh[b]:.0%}", font=f("bold", 8.5), fill="#FFFFFF")
            xx += seg
        if name == "All lenders":
            d.line((8 * S, ry + bh + 3 * S, w * S - 8 * S, ry + bh + 3 * S), fill=LINE, width=1 * S)
    # 50% guide
    gx = bx + bw * 0.5
    for yy in range(int(y - 4 * S), int(h * S - 6 * S), 8 * S):
        d.line((gx, yy, gx, yy + 4 * S), fill="#FFFFFF", width=int(1.5 * S))
    d.text((gx - d.textlength("half of pulls", font=mono(7.5)) / 2, y - 13 * S), "half of pulls", font=mono(7.5), fill=MUTED)
    return save(im, "info_scorecard")


# ================================================================ dashboard shell (sidebar, header band, cards, coach marks)
SB_BG, SB_INK, SB_MUTED = "#0B1F4D", "#FFFFFF", "#9FB2D9"
CANVAS2 = BG


def edge_glow(d, x0, y, x1, width=2):
    """A teal-to-orange edge line, like the lit edges of the cards in the cover photo."""
    c0, c1 = (47, 212, 196), (255, 138, 42)
    n = int(x1 - x0)
    for k in range(n):
        t = k / max(n - 1, 1)
        d.line((x0 + k, y, x0 + k, y + width * S - 1), fill=tuple(int(c0[j] + (c1[j] - c0[j]) * t) for j in range(3)))


def panel(w, h, bg=BG, fill=CARD, radius=0, glow=True):
    im = Image.new("RGB", (w * S, h * S), bg)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 2 * S, h * S - 2 * S), radius=radius * S, fill=fill, outline=LINE, width=1 * S)
    if glow:
        edge_glow(d, 14 * S, 0, w * S - 16 * S, 2)
    return im, d


def sidebar(w, h, items, current, name):
    """Side panel: title, story navigation (current card highlighted), bureau color key, as-of note."""
    im = Image.new("RGB", (w * S, h * S), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 2 * S, h * S - 2 * S), radius=0, fill="#0F1217", outline=LINE, width=1 * S)
    # lit right edge
    for y in range(14 * S, h * S - 14 * S):
        t = y / (h * S)
        d.line((w * S - 4 * S, y, w * S - 3 * S, y), fill=tuple(int(a + (b - a) * t) for a, b in zip((47, 212, 196), (255, 138, 42))))
    x0 = w * S / 2 - 30 * S
    for i, b in enumerate(("Experian", "Equifax", "TransUnion")):
        hh = (34, 24, 18)[i] * S
        d.rounded_rectangle((x0 + i * 22 * S, 58 * S - hh, x0 + i * 22 * S + 14 * S, 58 * S), radius=3 * S, fill=BUREAU[b])
    for k, line in enumerate(("FP&A Credit Stacking &", "Funding Sequencing", "Strategy")):
        t = f("bold", 12); tw = d.textlength(line, font=t)
        d.text(((w * S - tw) / 2, (66 + k * 16) * S), line, font=t, fill=INK)
    t = f("semibold", 9); line = "Which Bureau Will They Pull?"; tw = d.textlength(line, font=t)
    d.text(((w * S - tw) / 2, 118 * S), line, font=t, fill=TEAL)
    y = 138 * S
    d.line((14 * S, y, w * S - 16 * S, y), fill=LINE, width=1 * S)
    d.text((18 * S, y + 12 * S), "STORY", font=mono(8, True), fill=TEAL)
    y += 30 * S
    for i, it in enumerate(items, 1):
        cur = i == current
        if cur:
            d.rounded_rectangle((10 * S, y - 5 * S, w * S - 14 * S, y + 21 * S), radius=0, fill=TEAL)
        d.text((20 * S, y), f"{i}", font=f("bold", 10), fill=BG if cur else MUTED)
        d.text((36 * S, y), it, font=f("bold" if cur else "medium", 10), fill=BG if cur else INK2)
        y += 30 * S
    y += 6 * S
    d.line((14 * S, y, w * S - 16 * S, y), fill=LINE, width=1 * S)
    d.text((18 * S, y + 12 * S), "BUREAU COLORS", font=mono(8, True), fill=TEAL)
    y += 34 * S
    for b in ("Experian", "Equifax", "TransUnion"):
        d.rounded_rectangle((20 * S, y, 34 * S, y + 14 * S), radius=3 * S, fill=BUREAU[b])
        d.text((42 * S, y - 1 * S), b, font=f("bold", 10), fill=BUREAU[b])
        y += 24 * S
    by = h * S - 96 * S
    d.line((14 * S, by, w * S - 16 * S, by), fill=LINE, width=1 * S)
    for k, (txt, ft, col) in enumerate((("As of October 7, 2026", f("medium", 9), INK), ("Lender minimums reviewed quarterly", f("regular", 8), MUTED),
                                        ("Designed by", f("regular", 8), MUTED), ("Shamar Robinson", f("bold", 10), INK))):
        tw = d.textlength(txt, font=ft)
        d.text(((w * S - tw) / 2, by + (12 + k * 18) * S), txt, font=ft, fill=col)
    return save(im, name)


def fill_photo(photo, w, h, focus=(0.5, 0.5)):
    """Crop a photo to fill w x h (pixels), keeping the focus point in view."""
    ph = Image.open(photo).convert("RGB")
    sc = max(w / ph.width, h / ph.height)
    ph = ph.resize((int(ph.width * sc) + 1, int(ph.height * sc) + 1))
    x = int(min(max(ph.width * focus[0] - w / 2, 0), ph.width - w)); y = int(min(max(ph.height * focus[1] - h / 2, 0), ph.height - h))
    return ph.crop((x, y, x + w, y + h))


def fade_left(ph, frac=0.5, dark=1.0):
    """Mask that fades the left part of a photo into the dark canvas."""
    from PIL import ImageEnhance
    ph = ImageEnhance.Brightness(ph).enhance(0.62 * dark + 0.38)
    mask = Image.new("L", ph.size, 255); md = ImageDraw.Draw(mask)
    fw = int(ph.width * frac)
    for x in range(fw):
        md.line((x, 0, x, ph.height), fill=int(255 * (x / fw) ** 1.3))
    return ph, mask


def tab_boxes(w, h, tabs, right_gap=0):
    """Pixel boxes (x0, y0, x1, y1, in 1x units) of the pill tabs header_band draws, so they can be made clickable."""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    ft = f("bold", 10)
    pads = [d.textlength(t.upper(), font=ft) + 30 * S for t in tabs]
    px1 = w * S - 14 * S - right_gap * S; px0 = px1 - (sum(pads) + 10 * S)
    out, x = [], px0 + 5 * S
    for p in pads:
        out.append((x / S, 22, (x + p) / S, h - 24)); x += p
    return out


def header_band(w, h, title, sub, tabs, current, name, right_gap=0, photo=None, focus=(0.5, 0.5)):
    """Title band with pill tabs (current section lit teal); a teal-to-orange glow along the bottom edge.
    An optional photo fills the right part of the band and fades into it."""
    im = Image.new("RGB", (w * S, h * S), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 2 * S, h * S - 2 * S), radius=0, fill="#0F1217", outline=LINE, width=1 * S)
    if photo:
        pw = int(w * S * 0.55)
        ph, mask = fade_left(fill_photo(photo, pw, h * S - 4 * S, focus), 0.6, 0.5)
        layer = Image.new("RGB", im.size, "#0F1217"); layer.paste(ph, (w * S - pw - 2 * S, 2 * S), mask)
        rm = Image.new("L", im.size, 0); ImageDraw.Draw(rm).rounded_rectangle((1 * S, 1 * S, w * S - 3 * S, h * S - 3 * S), radius=0, fill=255)
        im.paste(layer, (0, 0), rm)
        d = ImageDraw.Draw(im)
    edge_glow(d, 16 * S, h * S - 4 * S, w * S - 18 * S, 2)
    d.text((22 * S, 12 * S), title, font=f("bold", 20), fill=INK)
    draw_rich(d, 22 * S, 44 * S, w * S * 0.56, sub, size=10, color=INK2, line_gap=2)
    ft = f("bold", 10)
    pads = [d.textlength(t.upper(), font=ft) + 30 * S for t in tabs]
    pw = sum(pads) + 10 * S
    px1 = w * S - 14 * S - right_gap * S; px0 = px1 - pw
    d.rounded_rectangle((px0, 18 * S, px1, h * S - 20 * S), radius=0, fill=CARD2 if not photo else "#0F1217", outline=LINE, width=1 * S)
    x = px0 + 5 * S
    for t, p in zip(tabs, pads):
        if t == current:
            d.rounded_rectangle((x, 22 * S, x + p, h * S - 24 * S), radius=0, fill=TEAL)
        tw = d.textlength(t.upper(), font=ft)
        d.text((x + (p - tw) / 2, (18 * S + h * S - 20 * S) / 2 - 7 * S), t.upper(), font=ft, fill=BG if t == current else INK2)
        x += p
    return save(im, name)


def text_card(w, h, blocks, name, title=None, accent=TEAL, size=10.5):
    """Charcoal rounded card. blocks: list of (heading, [(label, text), ...] or str)."""
    im, d = panel(w, h)
    y = 16 * S
    if title:
        d.text((18 * S, y), title, font=f("bold", 13), fill=INK); y += 26 * S
    for head, body in blocks:
        d.rounded_rectangle((18 * S, y + 3 * S, 22 * S, y + 17 * S), radius=2 * S, fill=accent)
        d.text((30 * S, y), head, font=f("bold", 12), fill=INK)
        y += 24 * S
        if isinstance(body, str):
            y = draw_rich(d, 30 * S, y, w * S - 52 * S, body, size=size, color=INK2, line_gap=3) + 8 * S
        else:
            for lab, txt in body:
                y = draw_rich(d, 30 * S, y, w * S - 52 * S, txt, size=size, color=INK2, line_gap=3, lead=f"{lab}:" if lab else None)
                y += 5 * S
            y += 6 * S
        y += 4 * S
    if y > h * S:
        print("WARNING overflow", name, y // S, ">", h)
    return save(im, name)


def coach(n, text, name, w=230, h=28, color=ORANGE):
    """Coach mark: a numbered orange badge with a short instruction, for guided walkthroughs."""
    im = Image.new("RGB", (w * S, h * S), CARD)
    d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=f("semibold", 10)) + 44 * S
    d.rounded_rectangle((0, 0, min(tw, w * S - 1), h * S - 1), radius=0, fill="#F2EFE8")
    d.ellipse((3 * S, 3 * S, h * S - 3 * S, h * S - 3 * S), fill=color)
    t = f("bold", 12); nw = d.textlength(str(n), font=t)
    d.text(((h * S - nw) / 2, 6 * S), str(n), font=t, fill="#07090C")
    d.text((h * S + 6 * S, 7 * S), text, font=f("semibold", 10), fill="#07090C")
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.png"; im.save(p); return p


def callouts(w, h, title, items, name):
    """Annotation cards: a colored marker, a bold finding and one line of context."""
    im, d = panel(w, h)
    d.text((18 * S, 16 * S), title, font=f("bold", 13), fill=INK)
    n = len(items); top = 46 * S
    rh = (h * S - top - 10 * S) / n
    for i, (mark_col, head, line) in enumerate(items):
        y = top + i * rh
        d.ellipse((18 * S, y + 4 * S, 30 * S, y + 16 * S), fill=mark_col)
        d.line((24 * S, y + 18 * S, 24 * S, y + rh - 8 * S), fill=LINE, width=1 * S)
        yy = draw_rich(d, 40 * S, y, w * S - 60 * S, head, size=11, weight="semibold", color=INK, line_gap=2)
        yy = draw_rich(d, 40 * S, yy + 2 * S, w * S - 60 * S, line, size=9.5, color=INK2, line_gap=2)
        if yy > y + rh + 4 * S: print("WARNING callout overflow", name, i)
    return save(im, name)


def hbars(w, h, title, rows, name, note=""):
    """Card with labeled horizontal bars: rows = (label, value, color)."""
    im, d = panel(w, h)
    d.text((18 * S, 16 * S), title, font=f("bold", 13), fill=INK)
    top = 46 * S; lab = 170 * S; mx = max(v for _, v, _ in rows)
    rh = (h * S - top - (30 * S if note else 12 * S)) / len(rows)
    for i, (l, v, c) in enumerate(rows):
        y = top + i * rh
        d.text((18 * S, y + rh / 2 - 8 * S), l, font=f("medium", 10), fill=INK2)
        d.rounded_rectangle((lab, y + rh * 0.2, w * S - 60 * S, y + rh * 0.8), radius=3 * S, fill=TRACK)
        bw = (w * S - lab - 60 * S) * v / mx
        d.rounded_rectangle((lab, y + rh * 0.2, lab + max(bw, 3 * S), y + rh * 0.8), radius=3 * S, fill=c)
        d.text((w * S - 52 * S, y + rh / 2 - 8 * S), f"{v}", font=f("bold", 11), fill=INK)
    if note:
        draw_rich(d, 18 * S, h * S - 26 * S, w * S - 36 * S, note, size=9, color=MUTED)
    return save(im, name)


def steps_card(w, h, title, steps, name):
    """Guided walkthrough: numbered orange steps (coach marks) in a card."""
    im, d = panel(w, h)
    d.text((18 * S, 16 * S), title, font=f("bold", 13), fill=INK)
    top = 48 * S; rh = (h * S - top - 8 * S) / len(steps)
    for i, (head, line) in enumerate(steps, 1):
        y = top + (i - 1) * rh
        d.ellipse((18 * S, y, 42 * S, y + 24 * S), fill=ORANGE)
        t = f("bold", 12); nw = d.textlength(str(i), font=t)
        d.text((30 * S - nw / 2, y + 4 * S), str(i), font=t, fill=BG)
        d.text((54 * S, y + 2 * S), head, font=f("semibold", 11), fill=INK)
        draw_rich(d, 54 * S, y + 22 * S, w * S - 76 * S, line, size=9.5, color=INK2, line_gap=2)
    return save(im, name)


def photo_hero(w, h, photo, name, title, sub, bans, subhead=None):
    """Cover band: the card photo darkened on the right, title and BAN chips on the left."""
    from PIL import ImageFilter
    im = Image.new("RGB", (w * S, h * S), BG)
    ph = Image.open(photo).convert("RGB")
    pw = int(w * S * 0.62); ratio = ph.height / ph.width
    ph = ph.resize((pw, int(pw * ratio)))
    top = max(0, (ph.height - h * S) // 2)
    ph = ph.crop((0, top, pw, top + h * S))
    # fade the photo into the canvas on its left edge
    mask = Image.new("L", ph.size, 255)
    md = ImageDraw.Draw(mask)
    fade = int(pw * 0.45)
    for x in range(fade):
        md.line((x, 0, x, ph.height), fill=int(255 * (x / fade) ** 1.4))
    im.paste(ph, (w * S - pw, 0), mask)
    m2 = Image.new("L", im.size, 0); ImageDraw.Draw(m2).rounded_rectangle((0, 0, w * S - 2 * S, h * S - 2 * S), radius=0, fill=255)
    out = Image.new("RGB", im.size, BG); out.paste(im, (0, 0), m2)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((0, 0, w * S - 2 * S, h * S - 2 * S), radius=0, outline=LINE, width=1 * S)
    edge_glow(d, 16 * S, h * S - 4 * S, w * S - 18 * S, 2)
    d.text((24 * S, 18 * S), "CLIENT PERSONAL AND BUSINESS FUNDING SEQUENCE", font=mono(8.5, True), fill=TEAL)
    yy = 36 * S
    for line in title:
        d.text((24 * S, yy), line, font=f("bold", 26), fill=INK); yy += 33 * S
    if subhead:
        d.text((24 * S, yy + 2 * S), subhead, font=f("semibold", 15), fill=TEAL); yy += 26 * S
    yy = draw_rich(d, 24 * S, yy + 4 * S, w * S * 0.42, sub, size=10.5, color=INK2, line_gap=3)
    x = 24 * S; y = h * S - 74 * S
    for val, lab, col in bans:
        tw = max(d.textlength(val, font=f("bold", 18)), d.textlength(lab, font=f("medium", 8.5))) + 24 * S
        d.rounded_rectangle((x, y, x + tw, y + 54 * S), radius=0, fill=(15, 18, 23), outline=LINE, width=1 * S)
        d.text((x + 12 * S, y + 6 * S), val, font=f("bold", 18), fill=col)
        d.text((x + 12 * S, y + 33 * S), lab, font=f("medium", 8.5), fill=INK2)
        x += tw + 8 * S
    return save(out, name)


def photo_card(w, h, photo, name, kicker, title, lines=(), focus=(0.5, 0.5)):
    """A photo card: the photo fills the card, a dark gradient rises from the bottom, text sits on top."""
    W_, H_ = w * S, h * S
    ph = fill_photo(photo, W_, H_, focus)
    from PIL import ImageEnhance
    ph = ImageEnhance.Brightness(ph).enhance(0.8)
    shade = Image.new("RGB", ph.size, "#07090C"); mask = Image.new("L", ph.size, 0); md = ImageDraw.Draw(mask)
    for y in range(H_):
        t = y / H_
        md.line((0, y, W_, y), fill=int(235 * max(0, (t - 0.25) / 0.75) ** 1.1))
    ph.paste(shade, (0, 0), mask)
    out = Image.new("RGB", ph.size, BG); rm = Image.new("L", ph.size, 0)
    ImageDraw.Draw(rm).rounded_rectangle((0, 0, W_ - 2 * S, H_ - 2 * S), radius=0, fill=255)
    out.paste(ph, (0, 0), rm)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((0, 0, W_ - 2 * S, H_ - 2 * S), radius=0, outline=LINE, width=1 * S)
    edge_glow(d, 14 * S, 0, W_ - 16 * S, 2)
    # measure text block height, then draw it bottom-aligned
    tmp = ImageDraw.Draw(Image.new("RGB", (W_, H_)))
    hh = 18 * S + 22 * S
    for lab, txt in lines:
        hh = draw_rich(tmp, 0, hh, W_ - 36 * S, txt, size=9.5, color=INK2, line_gap=2, lead=f"{lab}:" if lab else None) + 4 * S
    y = H_ - hh - 14 * S
    d.text((18 * S, y), kicker, font=mono(8, True), fill=TEAL)
    d.text((18 * S, y + 16 * S), title, font=f("bold", 15), fill="#FFFFFF")
    yy = y + 18 * S + 22 * S
    for lab, txt in lines:
        yy = draw_rich(d, 18 * S, yy, W_ - 36 * S, txt, size=9.5, color="#E3E6EB", line_gap=2, lead=f"{lab}:" if lab else None) + 4 * S
    return save(out, name)
