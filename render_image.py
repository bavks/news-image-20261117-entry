#!/usr/bin/env python3
"""Render entry.png as a vintage newspaper front page.

Entry for the make.fun bounty "Sum up 17 November's world news in one
image" (news-image-20261117). The page is a black-and-white newsprint
broadsheet: serif nameplate ("The Daily Meridian"), a dateline carrying
"Tuesday, 17 November 2026", one lead story and five further stories in
ruled columns, each with a halftone-style illustration drawn in code.

Every word is real and typeset here with PIL fonts (no generative
text, no filler). The six stories and their facts are the ones verified
against reports dated 17 November 2026; see README.md for sources.

The artwork for each story is drawn in grayscale with simple shapes,
then run through an ordered-dither "newsprint" pass (a handful of gray
levels, Bayer dithering) and inked onto the paper colour, so it reads
as halftone newspaper art rather than flat colour blocks.

Output: entry.png next to this script, 1024x1024, under 1 MiB.
main.py copies it to the grader's output directory unchanged.
"""

import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- setup

S = 2                      # supersampling factor (rendered big, shrunk)
W = H = 1024               # final size
PAPER = (244, 239, 227)    # warm newsprint
INK = (27, 24, 19)         # black ink
SOFT = (84, 79, 68)        # softened ink for captions

F_DIR = "/usr/share/fonts/truetype/dejavu"
N_DIR = "/usr/share/fonts/truetype/noto"
DISPLAY_BLACK = os.path.join(N_DIR, "NotoSerifDisplay-Black.ttf")
SERIF_BOLD = os.path.join(F_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(F_DIR, "DejaVuSerif.ttf")
SERIF_IT = os.path.join(N_DIR, "NotoSerif-Italic.ttf")


def X(v):
    """Scale a final-size coordinate to render size."""
    return int(round(v * S))


def font(path, size):
    return ImageFont.truetype(path, X(size))


# ---------------------------------------------------------------- text

def wrap(draw, text, fnt, maxw):
    """Greedy word wrap; maxw in render px."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, path, maxw, start, minimum):
    """Largest font size (<= start) whose single line fits maxw."""
    size = start
    while size > minimum:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= maxw:
            return fnt, size
        size -= 1
    return font(path, minimum), minimum


def wrap_fit(draw, text, path, maxw, max_lines, start, minimum):
    """Largest size whose wrap fits within max_lines lines."""
    size = start
    while size > minimum:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, maxw)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(path, minimum)
    return fnt, wrap(draw, text, fnt, maxw)


def centered(draw, cx, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text((X(cx) - w / 2, X(y)), text, font=fnt, fill=fill)
    return w


def block(draw, x, y, lines, fnt, lh, fill=INK, align="left", cx=None):
    """Draw wrapped lines; returns y after the block."""
    for line in lines:
        if align == "center":
            centered(draw, cx, y, line, fnt, fill)
        else:
            draw.text((X(x), X(y)), line, font=fnt, fill=fill)
        y += lh
    return y


# ------------------------------------------------------- newsprint art

BAYER = np.array(
    [[0, 32, 8, 40, 2, 34, 10, 42],
     [48, 16, 56, 24, 50, 18, 58, 26],
     [12, 44, 4, 36, 14, 46, 6, 38],
     [60, 28, 52, 20, 62, 30, 54, 22],
     [3, 35, 11, 43, 1, 33, 9, 41],
     [51, 19, 59, 27, 49, 17, 57, 25],
     [15, 47, 7, 39, 13, 45, 5, 37],
     [63, 31, 55, 23, 61, 29, 53, 21]], dtype=np.float32) / 64.0


def newsprint(gray, levels=6):
    """Ordered-dither a grayscale image to a few gray levels."""
    a = np.asarray(gray).astype(np.float32) / 255.0
    h, w = a.shape
    b = np.tile(BAYER, (h // 8 + 1, w // 8 + 1))[:h, :w]
    q = np.floor(a * (levels - 1) + b) / (levels - 1)
    return Image.fromarray((np.clip(q, 0, 1) * 255).astype(np.uint8), "L")


def ink_on_paper(gray):
    """Map grayscale (0=ink, 255=paper) onto the paper/ink colours."""
    t = np.asarray(gray).astype(np.float32) / 255.0
    ink = np.array(INK, dtype=np.float32)
    paper = np.array(PAPER, dtype=np.float32)
    out = ink[None, None, :] * (1 - t[..., None]) + paper[None, None, :] * t[..., None]
    return Image.fromarray(out.astype(np.uint8), "RGB")


def art_canvas(w, h, base=238):
    img = Image.new("L", (X(w), X(h)), base)
    return img, ImageDraw.Draw(img)


def vgrad(img, top, bottom):
    """Vertical gradient fill on an 'L' image."""
    w, h = img.size
    col = np.linspace(top, bottom, h, dtype=np.float32)[:, None]
    arr = np.repeat(col, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "L")


def finish_art(img, page, x, y):
    """Dither, ink and paste an artwork, with a photo-box border."""
    img = newsprint(img, levels=6)
    rgb = ink_on_paper(img)
    page.paste(rgb, (X(x), X(y)))
    d = ImageDraw.Draw(page)
    w, h = img.size
    d.rectangle([X(x), X(y), X(x) + w - 1, X(y) + h - 1],
                outline=INK, width=X(1.6))


# ------------------------------------------------------------ artworks
# Each returns an 'L' image of the given final-pixel size.

def art_bridge(w, h):
    """Kerch Bridge: arch span, one road span dropped into the strait."""
    img = Image.new("L", (X(w), X(h)), 0)
    img = vgrad(img, 242, 208)
    d = ImageDraw.Draw(img)
    deck = h * 0.40
    water = h * 0.64
    # sea
    d.rectangle([0, X(water), X(w), X(h)], fill=118)
    rng = random.Random(7)
    for _ in range(46):  # wave strokes
        x0 = rng.uniform(0, w - 26)
        y0 = rng.uniform(water + 5, h - 6)
        ln = rng.uniform(9, 24)
        d.line([X(x0), X(y0), X(x0 + ln), X(y0)], fill=196, width=X(1.4))
    # piers
    for px in (0.10, 0.30, 0.50, 0.86):
        d.rectangle([X(w * px), X(deck), X(w * px + 7), X(h * 0.97)], fill=58)
    # arch (left section) with hangers
    ax0, ax1 = w * 0.06, w * 0.47
    d.arc([X(ax0), X(deck - h * 0.30), X(ax1), X(deck + h * 0.10)],
          start=180, end=360, fill=42, width=X(4))
    for t in np.linspace(0.12, 0.88, 6):
        ang = math.pi * (1 - t)
        ax = (ax0 + ax1) / 2 + (ax1 - ax0) / 2 * math.cos(ang)
        ay = deck - h * 0.10 - h * 0.20 * math.sin(ang)
        d.line([X(ax), X(ay), X(ax), X(deck)], fill=70, width=X(1.3))
    # intact deck, left and right of the break
    d.rectangle([0, X(deck), X(w * 0.55), X(deck + 5)], fill=40)
    d.rectangle([X(w * 0.80), X(deck), X(w), X(deck + 5)], fill=40)
    # dropped span: a slab slanting from the break down into the water
    bx, by = w * 0.55, deck
    ex, ey = w * 0.79, water + h * 0.10
    d.polygon([(X(bx), X(by)), (X(ex), X(ey)), (X(ex), X(ey + 7)),
               (X(bx), X(by + 6))], fill=38)
    # splash where it meets the water
    for dx, dy, ln in ((-12, -8, 12), (-4, -13, 15), (5, -12, 14), (13, -7, 11)):
        d.line([X(ex + dx), X(water + 4), X(ex + dx + dx * 0.4),
                X(water + 4 + dy)], fill=225, width=X(1.6))
    d.ellipse([X(ex - 20), X(water - 2), X(ex + 22), X(water + 6)],
              outline=225, width=X(1.5))
    # smoke over the break: an overlapping chain of puffs from the break
    for cx, cy, r, g in ((0.572, 0.325, 9, 146), (0.598, 0.255, 12, 162),
                         (0.632, 0.185, 15, 179), (0.675, 0.12, 18, 196)):
        d.ellipse([X(w * cx - r), X(h * cy - r * 0.62),
                   X(w * cx + r), X(h * cy + r * 0.62)], fill=g)
    return img


def art_drones(w, h):
    """Bahrain: radar dome under a dark sky, drones intercepted."""
    img = Image.new("L", (X(w), X(h)), 0)
    img = vgrad(img, 66, 104)
    d = ImageDraw.Draw(img)
    gy = h * 0.86
    d.rectangle([0, X(gy), X(w), X(h)], fill=30)          # ground
    # radar dome on its base, left of centre
    cx, r = w * 0.27, h * 0.44
    d.rectangle([X(cx - r), X(gy - 4), X(cx + r), X(gy)], fill=22)
    d.pieslice([X(cx - r), X(gy - 2 * r), X(cx + r), X(gy)],
               start=180, end=360, fill=208)
    d.line([X(cx), X(gy - 2 * r), X(cx), X(gy - 2 * r - 7)], fill=208,
           width=X(1.6))
    # drones (quadcopter glyphs) in pale silhouette
    def drone(cx, cy, s, tone=216):
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            ex, ey = cx + dx * s, cy + dy * s * 0.62
            d.line([X(cx), X(cy), X(ex), X(ey)], fill=tone, width=X(1.4))
            d.ellipse([X(ex - s * 0.52), X(ey - s * 0.20),
                       X(ex + s * 0.52), X(ey + s * 0.20)], outline=tone,
                      width=X(1.3))
        d.ellipse([X(cx - s * 0.30), X(cy - s * 0.22),
                   X(cx + s * 0.30), X(cy + s * 0.22)], fill=tone)
    drone(w * 0.60, h * 0.36, 9)
    drone(w * 0.76, h * 0.55, 7.5)
    drone(w * 0.90, h * 0.28, 8.5)
    # interception burst beside the highest drone
    bx, by = w * 0.845, h * 0.30
    for ang in range(0, 360, 45):
        dx = math.cos(math.radians(ang)) * 8
        dy = math.sin(math.radians(ang)) * 8
        d.line([X(bx + dx * 0.35), X(by + dy * 0.35), X(bx + dx),
                X(by + dy)], fill=246, width=X(1.6))
    return img


def art_jets(w, h):
    """Japan: two fighters climbing past the dawn sun."""
    img = Image.new("L", (X(w), X(h)), 0)
    img = vgrad(img, 240, 214)
    d = ImageDraw.Draw(img)
    sea = h * 0.78
    d.rectangle([0, X(sea), X(w), X(h)], fill=128)
    rng = random.Random(11)
    for _ in range(18):
        x0 = rng.uniform(0, w - 20)
        y0 = rng.uniform(sea + 3, h - 4)
        d.line([X(x0), X(y0), X(x0 + rng.uniform(8, 18)), X(y0)],
               fill=200, width=X(1.2))
    # dawn sun: a pale disc with a dark rim
    sx, sy, sr = w * 0.16, h * 0.40, h * 0.26
    d.ellipse([X(sx - sr), X(sy - sr), X(sx + sr), X(sy + sr)], fill=206,
              outline=96, width=X(2))

    def jet(cx, cy, s, ang_deg=-20, tone=36):
        # top-view delta-wing fighter, nose to the right, rotated to
        # climb; two contrails stream from the tail
        base = [(1.0, 0.50), (0.42, 0.60), (0.14, 0.97), (0.26, 0.52),
                (0.10, 0.50), (0.26, 0.48), (0.14, 0.03), (0.42, 0.40)]
        ang = math.radians(ang_deg)
        ca, sa = math.cos(ang), math.sin(ang)
        pts = []
        for px, py in base:
            vx, vy = (px - 0.5) * s, (py - 0.5) * s * 0.92
            pts.append((X(cx + vx * ca - vy * sa),
                        X(cy + vx * sa + vy * ca)))
        d.polygon(pts, fill=tone)
        tx_ = cx - math.cos(ang) * s * 0.52
        ty_ = cy - math.sin(ang) * s * 0.52
        for off in (-3.2, 3.2):
            ox = -math.sin(ang) * off
            oy = math.cos(ang) * off
            d.line([X(tx_ + ox), X(ty_ + oy),
                    X(tx_ + ox - math.cos(ang) * s * 0.55),
                    X(ty_ + oy - math.sin(ang) * s * 0.55)],
                   fill=248, width=X(1.3))
    jet(w * 0.55, h * 0.40, 56)
    jet(w * 0.79, h * 0.58, 43)
    return img


def art_sport(w, h):
    """SAFF final: ball and trophy on the pitch."""
    img = Image.new("L", (X(w), X(h)), 0)
    img = vgrad(img, 236, 218)
    d = ImageDraw.Draw(img)
    gy = h * 0.80
    d.rectangle([0, X(gy), X(w), X(h)], fill=104)          # pitch
    d.line([0, X(gy), X(w), X(gy)], fill=52, width=X(2))
    # ball
    bx, by, br = w * 0.34, h * 0.46, h * 0.30
    d.ellipse([X(bx - br), X(by - br), X(bx + br), X(by + br)], fill=248,
              outline=40, width=X(2))
    d.polygon([(X(bx + br * 0.40 * math.cos(math.radians(a - 90))),
                X(by + br * 0.40 * math.sin(math.radians(a - 90))))
               for a in (0, 72, 144, 216, 288)], fill=44)
    for a in (18, 90, 162, 234, 306):
        px = bx + br * 0.97 * math.cos(math.radians(a))
        py = by + br * 0.97 * math.sin(math.radians(a))
        d.ellipse([X(px - 4.6), X(py - 4.6), X(px + 4.6), X(py + 4.6)],
                  fill=44)
    d.ellipse([X(bx - br), X(by - br), X(bx + br), X(by + br)],
              outline=40, width=X(2))
    # trophy
    tx, ty = w * 0.70, h * 0.16
    tw, th = w * 0.17, h * 0.44
    d.polygon([(X(tx), X(ty)), (X(tx + tw), X(ty)), (X(tx + tw * 0.82),
               X(ty + th)), (X(tx + tw * 0.18), X(ty + th))], fill=52)
    d.arc([X(tx - tw * 0.34), X(ty + th * 0.06), X(tx + tw * 0.30),
           X(ty + th * 0.62)], start=90, end=270, fill=52, width=X(3))
    d.arc([X(tx + tw * 0.70), X(ty + th * 0.06), X(tx + tw * 1.34),
           X(ty + th * 0.62)], start=270, end=90, fill=52, width=X(3))
    d.rectangle([X(tx + tw * 0.40), X(ty + th), X(tx + tw * 0.60),
                 X(ty + th + 8)], fill=52)
    d.rectangle([X(tx + tw * 0.22), X(ty + th + 8), X(tx + tw * 0.78),
                 X(ty + th + 13)], fill=52)
    # confetti ticks
    rng = random.Random(3)
    for _ in range(16):
        x0 = rng.uniform(4, w - 8)
        y0 = rng.uniform(3, h * 0.55)
        g = rng.choice((70, 120, 165))
        d.rectangle([X(x0), X(y0), X(x0 + 4), X(y0 + 2.4)], fill=g)
    return img


def art_climate(w, h):
    """COP31: the globe and a leaf."""
    img, d = art_canvas(w, h, base=240)
    cx, cy, r = w * 0.44, h * 0.52, h * 0.40
    d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], fill=232,
              outline=48, width=X(2.4))
    # continents: rough clusters of overlapping blobs
    clusters = [(-0.42, -0.40), (-0.08, -0.52), (0.34, -0.26),
                (-0.24, 0.10), (0.26, 0.30), (0.55, 0.55), (-0.52, 0.44)]
    rng = random.Random(9)
    for dx, dy in clusters:
        for _ in range(3):
            ox = dx + rng.uniform(-0.09, 0.09)
            oy = dy + rng.uniform(-0.08, 0.08)
            bw = rng.uniform(0.13, 0.24)
            bh = rng.uniform(0.11, 0.20)
            d.ellipse([X(cx + (ox - bw / 2) * r * 1.55),
                       X(cy + (oy - bh / 2) * r * 1.55),
                       X(cx + (ox + bw / 2) * r * 1.55),
                       X(cy + (oy + bh / 2) * r * 1.55)], fill=118)
    # leaf, lower right: a pointed oval built from a sine profile,
    # its tip at top-right, stem at bottom-left
    lx, ly = w * 0.64, h * 0.56
    lw, lh = w * 0.32, h * 0.38
    ux, uy = lw, -lh                      # leaf axis vector
    ulen = math.hypot(ux, uy)
    ux, uy = ux / ulen, uy / ulen
    px_, py_ = -uy, ux                    # perpendicular
    side_a, side_b = [], []
    for i in range(13):
        t = i / 12.0
        along = t * ulen
        half = math.sin(math.pi * t) * lw * 0.30
        bx_ = lx + ux * along
        by_ = ly + lh + uy * along
        side_a.append((X(bx_ + px_ * half), X(by_ + py_ * half)))
        side_b.append((X(bx_ - px_ * half), X(by_ - py_ * half)))
    d.polygon(side_a + side_b[::-1], fill=74)
    d.line([X(lx), X(ly + lh), X(lx + lw * 0.94), X(ly + lh * 0.06)],
           fill=214, width=X(1.5))
    return img


def art_gaza(w, h):
    """Gaza camps: tents in the rain, floodwater rising."""
    img, d = art_canvas(w, h, base=228)
    # cloud band
    for cx, cy, r in ((0.16, 0.10, 0.15), (0.38, 0.07, 0.19),
                      (0.62, 0.10, 0.17), (0.84, 0.08, 0.15)):
        d.ellipse([X(w * (cx - r)), X(h * (cy - r * 0.5)),
                   X(w * (cx + r)), X(h * (cy + r * 0.5))], fill=128)
    d.rectangle([0, 0, X(w), X(h * 0.10)], fill=128)
    # rain
    rng = random.Random(5)
    for _ in range(54):
        x0 = rng.uniform(2, w - 4)
        y0 = rng.uniform(h * 0.16, h * 0.58)
        d.line([X(x0), X(y0), X(x0 - 3), X(y0 + 8)], fill=150,
               width=X(1.2))
    # tents along the bottom
    base = h * 0.78
    for tx, tw, th, tone in ((0.05, 0.30, 0.30, 168), (0.38, 0.34, 0.36, 188),
                             (0.72, 0.27, 0.27, 158)):
        x0 = w * tx
        d.polygon([(X(x0), X(base)), (X(x0 + w * tw / 2), X(base - h * th)),
                   (X(x0 + w * tw), X(base))], fill=tone, outline=54)
        d.polygon([(X(x0 + w * tw * 0.40), X(base)),
                   (X(x0 + w * tw / 2), X(base - h * th * 0.42)),
                   (X(x0 + w * tw * 0.60), X(base))], fill=66)
    # floodwater with ripples
    d.rectangle([0, X(base), X(w), X(h)], fill=138)
    for rx, ry, rw in ((0.16, 0.87, 0.10), (0.52, 0.91, 0.13),
                       (0.82, 0.86, 0.09)):
        d.ellipse([X(w * (rx - rw)), X(h * (ry - 0.028)),
                   X(w * (rx + rw)), X(h * (ry + 0.028))], outline=214,
                  width=X(1.3))
    return img


# ---------------------------------------------------------------- page

def rule(d, x0, x1, y, weight=1.4, fill=INK):
    d.rectangle([X(x0), X(y), X(x1), X(y + weight)], fill=fill)


def build():
    page = Image.new("RGB", (X(W), X(H)), PAPER)
    d = ImageDraw.Draw(page)
    rng = random.Random(42)

    ML, MR = 40, 984            # content margins (final px)
    CW = MR - ML

    # page frame: double rule
    d.rectangle([X(13), X(13), X(1011), X(1011)], outline=INK, width=X(2.2))
    d.rectangle([X(19), X(19), X(1005), X(1005)], outline=INK, width=X(0.9))

    # ---- masthead strip
    f_strip = font(SERIF_BOLD, 19)
    d.text((X(ML), X(30)), "Vol. CXVII — No. 321", font=f_strip, fill=INK)
    right = "Price: One Day's News"
    d.text((X(MR) - d.textlength(right, font=f_strip), X(30)), right,
           font=f_strip, fill=INK)
    rule(d, ML, MR, 58, 4.6)
    rule(d, ML, MR, 66, 1.3)

    # ---- nameplate
    f_name, _ = fit(d, "The Daily Meridian", DISPLAY_BLACK, X(CW), 118, 40)
    centered(d, (ML + MR) / 2, 74, "The Daily Meridian", f_name)
    rule(d, ML, MR, 179, 5.2)
    rule(d, ML, MR, 188, 1.3)

    # ---- dateline
    f_date = font(SERIF_BOLD, 43)
    date = "Tuesday, 17 November 2026"
    tw = centered(d, (ML + MR) / 2, 198, date, f_date)
    midy = 198 + 24
    rule(d, ML, (ML + MR) / 2 - tw / (2 * S) - 18, midy, 1.3)
    rule(d, (ML + MR) / 2 + tw / (2 * S) + 18, MR, midy, 1.3)
    rule(d, ML, MR, 252, 1.3)

    # ---- lead story: Kerch Bridge
    f_lead, lead_lines = wrap_fit(d, "UKRAINE DROPS KERCH BRIDGE SPAN",
                                  SERIF_BOLD, X(CW), 2, 60, 30)
    y = block(d, ML, 266, lead_lines, f_lead, 64, align="center",
              cx=(ML + MR) / 2)
    f_deck = font(SERIF_IT, 25)
    centered(d, (ML + MR) / 2, y + 2,
             "Drones and missiles fell the road arch overnight; "
             "the rail span was damaged.", f_deck)
    finish_art(art_bridge(CW, 148), page, ML, 428)
    rule(d, ML, MR, 592, 1.6)

    # ---- row A: three columns
    col_w, gut = 301, 20.5
    xs = [ML, ML + col_w + gut, ML + 2 * (col_w + gut)]
    rowA = [
        ("BAHRAIN STOPS IRANIAN DRONES",
         "IRGC drones aimed at a US radar base; all downed, no damage.",
         art_drones),
        ("JAPAN SCRAMBLES JETS AT DAWN",
         "Suspected Russian aircraft off Fukuoka; Tokyo protests.",
         art_jets),
        ("INDIA BEAT PAKISTAN TO SAFF TITLE",
         "A 2-1 win in Dhaka seals a record-extending 10th title.",
         art_sport),
    ]
    topA = 606
    for i, (head, sub, artfn) in enumerate(rowA):
        finish_art(artfn(col_w, 62), page, xs[i], topA)
        f_h, h_lines = wrap_fit(d, head, SERIF_BOLD, X(col_w), 2, 30, 20)
        yy = block(d, xs[i], topA + 70, h_lines, f_h, 33)
        f_s, s_lines = wrap_fit(d, sub, SERIF, X(col_w), 2, 20, 16)
        block(d, xs[i], yy + 3, s_lines, f_s, 24)
    for gx in (ML + col_w + gut / 2, ML + 2 * col_w + 1.5 * gut):
        d.line([X(gx), X(topA), X(gx), X(792)], fill=INK, width=X(1.1))
    rule(d, ML, MR, 800, 1.6)

    # ---- row B: two wide columns, art left, text right
    colB_w, gutB = 462, 20
    xsB = [ML, ML + colB_w + gutB]
    rowB = [
        ("COP31 DRAFT: PHASE OUT FOSSIL FUELS",
         "Ministers take over in Antalya; $120bn a year for "
         "adaptation by 2035.", art_climate),
        ("WINTER RAINS FLOOD GAZA CAMPS",
         "UN agencies: 1.7 million displaced, 1.4 million face "
         "acute hunger.", art_gaza),
    ]
    topB = 814
    artB_w, artB_h = 132, 118
    for i, (head, sub, artfn) in enumerate(rowB):
        finish_art(artfn(artB_w, artB_h), page, xsB[i], topB)
        tx = xsB[i] + artB_w + 14
        tw2 = colB_w - artB_w - 14
        f_h, h_lines = wrap_fit(d, head, SERIF_BOLD, X(tw2), 3, 28, 18)
        yy = block(d, tx, topB, h_lines, f_h, 30)
        f_s, s_lines = wrap_fit(d, sub, SERIF, X(tw2), 2, 20, 15)
        block(d, tx, yy + 4, s_lines, f_s, 23)
    gx = ML + colB_w + gutB / 2
    d.line([X(gx), X(topB), X(gx), X(944)], fill=INK, width=X(1.1))

    # ---- footer
    rule(d, ML, MR, 964, 1.6)
    f_foot = font(SERIF_IT, 19)
    centered(d, (ML + MR) / 2, 974,
             "All the news of one day, in one page.", f_foot, fill=SOFT)

    # ---- newsprint grain over the whole page
    page = page.resize((W, H), Image.LANCZOS)
    arr = np.asarray(page).astype(np.float32)
    noise = np.random.default_rng(42).normal(0, 4.5, arr.shape[:2])[..., None]
    blotch = np.asarray(
        Image.effect_noise((64, 64), 26).resize((W, H), Image.BILINEAR)
    ).astype(np.float32)
    blotch = (blotch - 128.0) * 0.055
    arr = np.clip(arr + noise + blotch[..., None], 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img = build()
    img.save(out, optimize=True)
    size = os.path.getsize(out)
    if size > 1_048_576:  # fall back to a palette PNG to fit the gate
        img.quantize(colors=96, dither=Image.FLOYDSTEINBERG).save(
            out, optimize=True)
        size = os.path.getsize(out)
    print(f"entry.png: {img.size[0]}x{img.size[1]}, {size} bytes")


if __name__ == "__main__":
    main()
