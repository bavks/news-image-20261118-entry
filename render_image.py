#!/usr/bin/env python3
"""Render entry.png: a colour newspaper front page for Wednesday,
18 November 2026, typeset as "The Daily Meridian".

Every illustration is drawn with PIL shapes in flat newsprint colours
and every word is typeset with real serif fonts -- no generative text
anywhere, so nothing can come out garbled.  Run it and it writes
entry.png next to this file.
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W = H = 1024

# --- palette: warm paper, coloured inks -------------------------------
PAPER = (247, 240, 221)
PAPER_SHADE = (238, 228, 199)
INK = (38, 33, 26)
MASTHEAD_RED = (140, 40, 28)
MASTHEAD_DEEP = (108, 28, 20)
CREAM = (250, 243, 224)
GOLD = (198, 150, 46)
NAVY = (31, 55, 92)
TEAL = (24, 102, 108)
RUST = (178, 74, 32)
SKY_DUSK_TOP = (46, 52, 96)
SKY_DUSK_MID = (196, 96, 52)
SEA = (30, 74, 96)
SAND = (214, 178, 106)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
NOTO = "/usr/share/fonts/truetype/noto"


def font(kind, size):
    paths = {
        "display": f"{NOTO}/NotoSerifDisplay-Black.ttf",
        "display_it": f"{NOTO}/NotoSerifDisplay-BoldItalic.ttf",
        "bold": f"{DEJAVU}/DejaVuSerif-Bold.ttf",
        "serif": f"{DEJAVU}/DejaVuSerif.ttf",
        "italic": f"{NOTO}/NotoSerif-Italic.ttf",
    }
    return ImageFont.truetype(paths[kind], size)


def text_w(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[2] - box[0]


def wrap(draw, s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, kind, s, max_w, start):
    """Largest size, at or below start, whose text fits max_w."""
    size = start
    while size > 10 and text_w(draw, s, font(kind, size)) > max_w:
        size -= 2
    return font(kind, size)


def centred(draw, cx, y, s, fnt, fill):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)
    return y + fnt.size + 6


def block(draw, x, y, s, fnt, fill, max_w, leading=1.18, centre=False):
    for line in wrap(draw, s, fnt, max_w):
        if centre:
            centred(draw, x + max_w / 2, y, line, fnt, fill)
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * leading)
    return y


def rule(draw, x0, x1, y, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def grain(img, seed=18, specks=2600):
    """A whisper of newsprint noise over the whole page."""
    rnd = random.Random(seed)
    px = img.load()
    for _ in range(specks):
        x, y = rnd.randrange(W), rnd.randrange(H)
        r, g, b = px[x, y][:3]
        delta = rnd.choice((-14, -9, 9, 14))
        px[x, y] = (max(0, min(255, r + delta)),
                    max(0, min(255, g + delta)),
                    max(0, min(255, b + delta)))
    return img


# --- little drawing helpers --------------------------------------------

def drone(draw, cx, cy, s, fill):
    """A quadcopter silhouette: X body, four rotor discs."""
    draw.line([(cx - s, cy - s * 0.6), (cx + s, cy + s * 0.6)], fill=fill, width=3)
    draw.line([(cx - s, cy + s * 0.6), (cx + s, cy - s * 0.6)], fill=fill, width=3)
    for dx, dy in ((-s, -s * 0.6), (s, -s * 0.6), (-s, s * 0.6), (s, s * 0.6)):
        draw.ellipse([cx + dx - s * 0.42, cy + dy - s * 0.16,
                      cx + dx + s * 0.42, cy + dy + s * 0.16], outline=fill, width=2)
    draw.ellipse([cx - s * 0.3, cy - s * 0.3, cx + s * 0.3, cy + s * 0.3], fill=fill)


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def burst(draw, cx, cy, r, fill):
    for i in range(8):
        ang = i * math.pi / 4
        draw.line([(cx, cy), (cx + r * math.cos(ang), cy + r * math.sin(ang))],
                  fill=fill, width=3)
    draw.ellipse([cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22], fill=fill)


# --- the six story illustrations ----------------------------------------

def art_gulf(draw, box):
    """Lead art: dusk over the Strait of Hormuz -- island, missile arcs,
    drones, the sea."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    for i in range(h):  # dusk gradient sky
        t = i / h
        top, mid = SKY_DUSK_TOP, SKY_DUSK_MID
        col = tuple(int(top[c] + (mid[c] - top[c]) * t) for c in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=col)
    sea_y = y0 + int(h * 0.72)
    draw.rectangle([x0, sea_y, x1, y1], fill=SEA)
    for i in range(26):  # wave ticks
        rnd = random.Random(i * 7)
        wx = x0 + rnd.randrange(10, x1 - x0 - 60)
        wy = sea_y + 8 + rnd.randrange(0, max(2, y1 - sea_y - 14))
        draw.line([(wx, wy), (wx + 26, wy)], fill=(120, 178, 196), width=2)
    # Qeshm-like island silhouette, centre-left
    isl = [(x0 + 120, sea_y), (x0 + 210, sea_y - 34), (x0 + 330, sea_y - 44),
           (x0 + 430, sea_y - 18), (x0 + 470, sea_y)]
    draw.polygon(isl, fill=(24, 24, 30))
    draw.rectangle([x0 + 268, sea_y - 74, x0 + 282, sea_y - 40], fill=(24, 24, 30))  # launcher
    # missile arcs from the island toward the right horizon
    for k, (ax, ay, bx, by) in enumerate([(290, -52, 700, -6), (300, -56, 790, -20)]):
        pts = []
        for s_i in range(31):
            t = s_i / 30
            px_ = x0 + ax + (bx - ax) * t
            py_ = y0 + (sea_y - y0) + ay * (1 - t) - math.sin(t * math.pi) * 74 + by * t
            pts.append((px_, py_))
        draw.line(pts, fill=(250, 214, 120), width=3)
        burst(draw, pts[-1][0], pts[-1][1], 13, (250, 190, 90))
    drone(draw, x0 + 640, y0 + 44, 17, (18, 18, 24))
    drone(draw, x0 + 730, y0 + 70, 13, (18, 18, 24))
    drone(draw, x0 + 96, y0 + 40, 12, (18, 18, 24))


def art_flags(draw, box):
    """Three flags on poles against a pale sky: China, the United States,
    Russia -- the Shenzhen gathering."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(206, 226, 238))
    draw.rectangle([x0, y1 - 16, x1, y1], fill=(96, 128, 92))
    fw, fh = 74, 48
    tops = [y0 + 14, y0 + 8, y0 + 14]
    for i, fx in enumerate([x0 + 22, x0 + 112, x0 + 202]):
        draw.line([(fx, tops[i]), (fx, y1 - 14)], fill=(70, 60, 50), width=3)
        fy = tops[i]
        if i == 0:  # China: red field, gold stars
            draw.rectangle([fx + 3, fy, fx + 3 + fw, fy + fh], fill=(206, 42, 34))
            star(draw, fx + 20, fy + 15, 9, (250, 208, 60))
            for dx, dy in ((34, 7), (37, 17), (34, 27)):
                star(draw, fx + dx, fy + dy, 4, (250, 208, 60))
        elif i == 1:  # United States: stripes and a blue canton
            for s_i in range(7):
                col = (196, 44, 44) if s_i % 2 == 0 else (246, 244, 238)
                draw.rectangle([fx + 3, fy + s_i * fh // 7, fx + 3 + fw,
                                fy + (s_i + 1) * fh // 7], fill=col)
            draw.rectangle([fx + 3, fy, fx + 3 + fw * 0.44, fy + fh * 0.54], fill=NAVY)
            for r_i in range(3):
                for c_i in range(4):
                    draw.ellipse([fx + 8 + c_i * 8, fy + 4 + r_i * 8,
                                  fx + 11 + c_i * 8, fy + 7 + r_i * 8], fill=(250, 250, 250))
        else:  # Russia: white, blue, red
            for s_i, col in enumerate([(246, 246, 246), (36, 84, 168), (206, 42, 34)]):
                draw.rectangle([fx + 3, fy + s_i * fh // 3, fx + 3 + fw,
                                fy + (s_i + 1) * fh // 3], fill=col)


def art_alaska(draw, box):
    """Alaska: deep blue field, snowy peaks, one big gold star."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(24, 44, 92))
    peaks = [(x0, y1), (x0 + 60, y0 + 34), (x0 + 118, y1),
             (x0 + 150, y1), (x0 + 205, y0 + 44), (x0 + 262, y1)]
    draw.polygon(peaks, fill=(232, 238, 244))
    draw.polygon([(x0 + 48, y0 + 48), (x0 + 60, y0 + 34), (x0 + 74, y0 + 48)],
                 fill=(255, 255, 255))
    draw.polygon([(x0 + 192, y0 + 58), (x0 + 205, y0 + 44), (x0 + 218, y0 + 58)],
                 fill=(255, 255, 255))
    star(draw, x0 + 236, y0 + 26, 13, GOLD)
    star(draw, x0 + 30, y0 + 18, 6, GOLD)
    star(draw, x0 + 130, y0 + 14, 5, GOLD)


def art_measles(draw, box):
    """A red virus sphere and a cracked elimination seal."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(244, 228, 205))
    cx, cy, r = x0 + 78, (y0 + y1) // 2, 30
    for i in range(12):
        ang = i * math.pi / 6
        ex, ey = cx + (r + 13) * math.cos(ang), cy + (r + 13) * math.sin(ang)
        draw.line([(cx, cy), (ex, ey)], fill=(188, 52, 44), width=4)
        draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(188, 52, 44))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(206, 64, 52))
    for dx, dy in ((-12, -8), (10, -14), (2, 10), (-4, -2)):
        draw.ellipse([cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5],
                     fill=(232, 120, 100))
    sx, sy, sr = x0 + 218, (y0 + y1) // 2, 40  # the seal, broken
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], outline=(120, 118, 110), width=6)
    draw.ellipse([sx - sr + 12, sy - sr + 12, sx + sr - 12, sy + sr - 12],
                 outline=(120, 118, 110), width=3)
    crack = [(sx - 6, sy - sr + 4), (sx + 8, sy - 18), (sx - 4, sy + 2),
             (sx + 10, sy + 22), (sx + 2, sy + sr - 4)]
    draw.line(crack, fill=(90, 40, 30), width=5)


def art_ebola(draw, box):
    """Africa in amber on teal, with a white medical cross badge."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=TEAL)
    cx, cy, s = x0 + 78, (y0 + y1) // 2, 1.0
    africa = [(0, -38), (26, -46), (52, -40), (66, -22), (84, -14), (88, 4),
              (74, 16), (76, 34), (62, 52), (44, 60), (30, 46), (18, 54),
              (8, 40), (-6, 30), (-16, 10), (-34, 4), (-46, -10), (-40, -26),
              (-22, -34)]
    pts = [(cx + int(px * s), cy + int(py * s)) for px, py in africa]
    draw.polygon(pts, fill=(226, 164, 60))
    draw.polygon([(cx + 52, cy + 40), (cx + 66, cy + 38), (cx + 62, cy + 52),
                  (cx + 50, cy + 50)], fill=(226, 164, 60))  # Madagascar hint
    bx, by, br = x0 + 116, y1 - 30, 17
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(250, 250, 248))
    draw.rectangle([bx - 4, by - 11, bx + 4, by + 11], fill=(196, 44, 40))
    draw.rectangle([bx - 11, by - 4, bx + 11, by + 4], fill=(196, 44, 40))


def art_voyager(draw, box):
    """Deep space: a small gold probe, a dashed signal home to a blue dot."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(16, 22, 52))
    rnd = random.Random(7)
    for _ in range(46):
        sx = x0 + rnd.randrange(4, x1 - x0 - 4)
        sy = y0 + rnd.randrange(4, y1 - y0 - 4)
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(235, 238, 250))
    ex, ey = x0 + 30, y1 - 26  # Earth
    draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=(86, 148, 220))
    draw.ellipse([ex - 4, ey - 6, ex + 3, ey - 1], fill=(110, 190, 130))
    px_, py_ = x0 + 106, y0 + 32  # the probe, kept inside the box
    for t_i in range(8):  # dashed signal arc, Earth to probe
        t = t_i / 8
        sx = ex + (px_ - ex) * t
        sy = ey + (py_ - ey) * t - math.sin(t * math.pi) * 14
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(250, 214, 120))
    draw.ellipse([px_ - 17, py_ - 11, px_ + 17, py_ + 11], outline=(240, 236, 226), width=3)
    draw.ellipse([px_ - 4, py_ - 4, px_ + 4, py_ + 4], fill=GOLD)
    draw.line([(px_, py_), (px_ + 30, py_ + 20)], fill=(220, 216, 205), width=3)
    draw.rectangle([px_ + 27, py_ + 17, px_ + 36, py_ + 25], fill=(200, 196, 185))
    draw.line([(px_, py_), (px_ - 22, py_ - 18)], fill=(220, 216, 205), width=3)


# --- page assembly -------------------------------------------------------

def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    MX0, MX1 = 44, 980  # content margins

    # frame
    draw.rectangle([14, 14, W - 15, H - 15], outline=INK, width=3)
    draw.rectangle([22, 22, W - 23, H - 23], outline=INK, width=1)

    # top strip
    strip_f = font("bold", 20)
    draw.text((MX0, 36), "Vol. CXVII — No. 322", font=strip_f, fill=INK)
    right = "Price: One Day's News"
    draw.text((MX1 - text_w(draw, right, strip_f), 36), right, font=strip_f, fill=INK)
    rule(draw, MX0, MX1, 68, 3)
    rule(draw, MX0, MX1, 74, 1)

    # masthead: deep red band, cream nameplate, auto-fitted to the page
    draw.rectangle([MX0, 82, MX1, 186], fill=MASTHEAD_RED)
    draw.rectangle([MX0, 82, MX1, 90], fill=MASTHEAD_DEEP)
    draw.rectangle([MX0, 178, MX1, 186], fill=MASTHEAD_DEEP)
    name_f = fit_font(draw, "display", "The Daily Meridian", MX1 - MX0 - 56, 96)
    centred(draw, W // 2, 134 - name_f.size // 2, "The Daily Meridian", name_f, CREAM)

    # dateline
    rule(draw, MX0, MX1, 200, 1)
    date_f = font("bold", 40)
    centred(draw, W // 2, 207, "Wednesday, 18 November 2026", date_f, MASTHEAD_RED)
    rule(draw, MX0, MX1, 258, 3)
    rule(draw, MX0, MX1, 264, 1)

    # lead story
    lead_f = font("bold", 50)
    y = block(draw, MX0, 274, "IRAN STRIKES U.S. BASES IN KUWAIT AND BAHRAIN",
              lead_f, INK, MX1 - MX0, leading=1.06, centre=True)
    deck_f = font("italic", 22)
    y = block(draw, MX0, y + 2,
              "Gulf states intercept missiles and drones after American jets "
              "hit a Revolutionary Guards missile site on Qeshm Island.",
              deck_f, (74, 62, 48), MX1 - MX0, leading=1.15, centre=True)
    art_gulf(draw, (MX0, y + 8, MX1, y + 138))
    y += 158
    rule(draw, MX0, MX1, y, 2)
    y += 12

    # three ruled columns
    col_w = (MX1 - MX0 - 2 * 28) // 3
    head_f, sub_f = font("bold", 24), font("serif", 17)
    columns = [
        ("XI GREETS TRUMP IN SHENZHEN",
         "Xi meets Putin and greets Trump in Shenzhen ahead of "
         "Thursday's first-ever trilateral summit.",
         art_flags),
        ("PELTOLA FLIPS ALASKA SENATE SEAT",
         "The final midterm call gives Democrats a 56-seat Senate "
         "majority, their largest since 2009.",
         art_alaska),
        ("U.S. LOSES MEASLES-FREE STATUS",
         "A verification panel ends 26 years of elimination status: "
         "5,412 cases, 10 deaths in 2026.",
         art_measles),
    ]
    col_top = y
    col_end = col_top
    for i, (head, sub, art) in enumerate(columns):
        cx0 = MX0 + i * (col_w + 28)
        art(draw, (cx0, col_top, cx0 + col_w, col_top + 72))
        hy = block(draw, cx0, col_top + 78, head, head_f,
                   NAVY if i != 1 else MASTHEAD_RED, col_w, leading=1.1)
        col_end = max(col_end, block(draw, cx0, hy + 2, sub, sub_f, INK,
                                     col_w, leading=1.15))
        if i < 2:
            draw.line([(cx0 + col_w + 14, col_top), (cx0 + col_w + 14, col_top + 196)],
                      fill=INK, width=1)
    y = col_end + 10
    rule(draw, MX0, MX1, y, 2)
    y += 12

    # two wide stories, art left and text right
    wide = [
        ("CONGO EBOLA CASES PASS 11,000",
         "The outbreak has doubled in three months; 5,400 are dead, "
         "and children are hit hardest.",
         art_ebola),
        ("VOYAGER 1 REACHES ONE LIGHT-DAY",
         "Its radio signals now take a full day to cross 16 billion "
         "miles — 49 years after launch.",
         art_voyager),
    ]
    half = (MX1 - MX0 - 28) // 2
    wide_end = y
    for i, (head, sub, art) in enumerate(wide):
        wx0 = MX0 + i * (half + 28)
        art(draw, (wx0, y, wx0 + 150, y + 88))
        tx = wx0 + 164
        hy = block(draw, tx, y - 2, head, font("bold", 23),
                   TEAL if i == 0 else NAVY, (wx0 + half) - tx, leading=1.1)
        wide_end = max(wide_end, block(draw, tx, hy + 2, sub, font("serif", 17),
                                       INK, (wx0 + half) - tx, leading=1.15))
        if i == 0:
            draw.line([(wx0 + half + 14, y), (wx0 + half + 14, y + 88)],
                      fill=INK, width=1)
    y = max(wide_end, y + 92) + 10

    # footer
    rule(draw, MX0, MX1, y, 1)
    centred(draw, W // 2, y + 7, "All the news of one day, in one page.",
            font("italic", 20), (74, 62, 48))
    assert y + 34 < H - 24, f"page overflow: content ends at {y}"

    img = grain(img)
    img.save(OUT, optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
