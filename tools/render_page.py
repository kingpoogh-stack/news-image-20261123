"""Build-time renderer for the v3 front page of THE WORLD TODAY.

Composes a realistic broadsheet newspaper front page for Monday,
23 November 2026 and writes it to assets/final-page.png. The page is
drawn at twice its final size with Pillow and downscaled, which gives
the type and the press-style illustration panels a smoother, printed
finish. Pillow is used only here, on the build machine; the shipped
entry point (main.py) is pure standard library.

Layout, top to bottom:
  folio line and masthead, markets ticker, "Inside today" strip,
  the COP31 lead (headline, deck, plenary-hall panel with caption and
  credit, body columns with a pull-quote rail), a three-column row
  (markets rout, Dymer strike, Shenzhen declaration), a second
  three-column row (Hormuz tankers, US House + Riemann claim, Sport),
  a markets-at-a-glance and weather band, and a World in Brief strip.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2  # supersampling factor
W, H = 1024, 1024

PAPER = (243, 238, 226)
PAPER_DARK = (233, 226, 208)
INK = (26, 24, 20)
SOFT = (74, 69, 60)
FAINT = (120, 113, 99)
RED = (150, 30, 24)
NAVY = (30, 50, 74)
RULE = (43, 40, 35)

FONT_DIR = Path("/usr/share/fonts/truetype")
SERIF = str(FONT_DIR / "liberation" / "LiberationSerif-Regular.ttf")
SERIF_B = str(FONT_DIR / "liberation" / "LiberationSerif-Bold.ttf")
SERIF_I = str(FONT_DIR / "liberation" / "LiberationSerif-Italic.ttf")
SERIF_BI = str(FONT_DIR / "liberation" / "LiberationSerif-BoldItalic.ttf")
SANS = str(FONT_DIR / "liberation" / "LiberationSans-Regular.ttf")
SANS_B = str(FONT_DIR / "liberation" / "LiberationSans-Bold.ttf")
SANS_I = str(FONT_DIR / "liberation" / "LiberationSans-Italic.ttf")
DISPLAY = str(FONT_DIR / "noto" / "NotoSerifDisplay-Black.ttf")

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        try:
            _cache[key] = ImageFont.truetype(path, size * S)
        except OSError:
            _cache[key] = ImageFont.truetype(SERIF_B, size * S)
    return _cache[key]


img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img, "RGBA")


def X(v):
    return v * S


def rect(x, y, w, h, fill=None, outline=None, width=1):
    d.rectangle([X(x), X(y), X(x + w), X(y + h)],
                fill=fill, outline=outline, width=max(1, int(width * S)))


def line(x1, y1, x2, y2, fill=RULE, width=1):
    d.line([X(x1), X(y1), X(x2), X(y2)], fill=fill, width=max(1, int(width * S)))


def text(x, y, s, font, fill=INK, anchor="la"):
    d.text((X(x), X(y)), s, font=font, fill=fill, anchor=anchor)


def tw(s, font):
    return d.textlength(s, font=font) / S


def wrap(s, font, width):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(trial, font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def flow(x, y, s, font, width, lh, fill=INK, max_lines=None, align="left"):
    """Set a paragraph; return the y just below its last line."""
    lines = wrap(s, font, width)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        if align == "center":
            text(x + width / 2, y, ln, font, fill, anchor="ma")
        else:
            text(x, y, ln, font, fill)
        y += lh
    return y


def grain(x, y, w, h, seed, n=260, alpha=16):
    """A whisper of print grain over an illustration panel."""
    rng = random.Random(seed)
    for _ in range(n):
        px, py = x + rng.random() * w, y + rng.random() * h
        shade = rng.choice([(0, 0, 0), (255, 255, 255)])
        d.point((X(px), X(py)), fill=shade + (alpha,))


def panel(x, y, w, h):
    rect(x, y, w, h, fill=(210, 203, 186), outline=RULE, width=1)


def caption(x, y, w, s, credit):
    text(x, y, s, F(SANS_I, 9.5), SOFT)
    text(x + w, y, credit, F(SANS_I, 9.5), SOFT, anchor="ra")


def kicker(x, y, s, fill=RED):
    text(x, y, s, F(SANS_B, 10.5), fill)


# ---------------------------------------------------------------- panels

def plenary_panel(x, y, w, h):
    """COP31 plenary hall in Antalya after the walkout."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h - 26, fill=(38, 58, 82))            # hall wall
    rect(x + 1, y + h - 27, w - 2, 26, fill=(104, 88, 66))          # stage floor
    rect(x + 14, y + 10, 46, 24, fill=(146, 44, 36))                # side screens
    rect(x + w - 60, y + 10, 46, 24, fill=(52, 96, 62))
    rect(x + 14, y + 10, 46, 24, outline=(220, 214, 198), width=1)
    rect(x + w - 60, y + 10, 46, 24, outline=(220, 214, 198), width=1)
    for sx in (x + 14, x + w - 60):  # faint agenda lines on the screens
        for li in range(3):
            line(sx + 7, y + 17 + li * 5, sx + 39, y + 17 + li * 5,
                 fill=(226, 220, 204, 130), width=1)
    text(x + w / 2, y + 9, "COP31  ·  ANTALYA", F(SANS_B, 15),
         (232, 226, 208), anchor="ma")
    ty = y + h - 34                                                 # delegates' table
    rect(x + 26, ty, w - 52, 7, fill=(74, 56, 40))
    rect(x + 26, ty + 7, w - 52, 3, fill=(52, 40, 28))
    seats = 11
    for i in range(seats):  # some seats filled, several pointedly empty
        cx = x + 76 + i * (w - 152) / (seats - 1)
        if i in (2, 5, 8):
            rect(cx - 6, ty - 12, 12, 12, outline=(214, 206, 188), width=1)
            continue
        d.ellipse([X(cx - 4.5), X(ty - 21), X(cx + 4.5), X(ty - 12)],
                  fill=(16, 15, 14))
        d.pieslice([X(cx - 8), X(ty - 13), X(cx + 8), X(ty + 3)],
                   180, 360, fill=(16, 15, 14))
        line(cx, ty - 26, cx, ty - 21, fill=(214, 206, 188), width=1)
    grain(x, y, w, h, seed=31)
    rect(x, y, w, h, outline=RULE, width=1)


def chart_panel(x, y, w, h):
    """A dealing-room screen as the AI sell-off goes global."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h - 2, fill=(18, 26, 40))
    for gx in range(1, 6):
        line(x + gx * w / 6, y + 4, x + gx * w / 6, y + h - 4,
             fill=(52, 66, 88), width=1)
    for gy in range(1, 4):
        line(x + 4, y + gy * h / 4, x + w - 4, y + gy * h / 4,
             fill=(52, 66, 88), width=1)
    pts = [(0.04, 0.30), (0.20, 0.22), (0.36, 0.38), (0.52, 0.33),
           (0.68, 0.52), (0.84, 0.60), (0.97, 0.80)]
    xy = [(X(x + px * w), X(y + py * h)) for px, py in pts]
    d.line(xy, fill=(224, 84, 60), width=2 * S)
    for px, py in xy:
        d.ellipse([px - 2.5 * S, py - 2.5 * S, px + 2.5 * S, py + 2.5 * S],
                  fill=(240, 150, 60))
    text(x + 8, y + h - 19, "NIKKEI 225  −5.06%", F(SANS_B, 12),
         (240, 190, 70))
    grain(x, y, w, h, seed=7, n=140, alpha=10)
    rect(x, y, w, h, outline=RULE, width=1)


def rescue_panel(x, y, w, h):
    """Rescue floodlights at the damaged block in Dymer, at dusk."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h - 2, fill=(72, 78, 92))
    rect(x + 1, y + h - 10, w - 2, 9, fill=(44, 44, 48))            # rubble ground
    bx, by, bw, bh = x + w * 0.52, y + 6, w * 0.40, h - 16          # the block
    rect(bx, by, bw, bh, fill=(60, 60, 66))
    d.polygon([(X(x + w * 0.40), X(y + h - 10)), (X(x + w * 0.47), X(y + h - 20)),
               (X(x + w * 0.55), X(y + h - 10))], fill=(38, 38, 42))  # rubble pile
    for r in range(3):
        for c in range(4):
            lit = (r * 4 + c) in (1, 5, 6, 10)
            rect(bx + 6 + c * (bw - 10) / 4, by + 4 + r * (bh - 6) / 3,
                 7, 5, fill=(238, 196, 110) if lit else (30, 30, 36))
    rect(bx + bw * 0.55, by, bw * 0.45, bh * 0.4, fill=(72, 78, 92))  # torn corner
    for tx in (x + w * 0.16, x + w * 0.34):                          # tripod lights
        ly = y + h - 12
        d.polygon([(X(tx), X(ly - 24)), (X(tx - 14), X(ly + 2)),
                   (X(tx + 14), X(ly + 2))], fill=(250, 226, 150, 70))
        line(tx - 6, ly, tx, ly - 20, fill=(20, 20, 22), width=2)
        line(tx + 6, ly, tx, ly - 20, fill=(20, 20, 22), width=2)
        d.ellipse([X(tx - 4), X(ly - 28), X(tx + 4), X(ly - 20)],
                  fill=(250, 230, 160))
    grain(x, y, w, h, seed=12, n=160, alpha=12)
    rect(x, y, w, h, outline=RULE, width=1)


def flags_panel(x, y, w, h):
    """The three flags at the Shenzhen trilateral summit."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h - 2, fill=(206, 198, 180))
    fw, fh, gap = (w - 32) / 3, h - 26, 8
    fx = x + 8
    for i in range(7):                                               # United States
        rect(fx, y + 6 + i * fh / 7, fw, fh / 7 + 1,
             fill=(168, 44, 48) if i % 2 == 0 else (238, 234, 224))
    rect(fx, y + 6, fw * 0.44, fh * 0.54, fill=(44, 54, 110))
    text(fx + fw / 2, y + h - 15, "USA", F(SANS_B, 9.5), INK, anchor="ma")
    fx += fw + gap
    for i, col in enumerate([(238, 234, 224), (52, 74, 140), (178, 40, 44)]):
        rect(fx, y + 6 + i * fh / 3, fw, fh / 3 + 1, fill=col)        # Russia
    text(fx + fw / 2, y + h - 15, "RUSSIA", F(SANS_B, 9.5), INK, anchor="ma")
    fx += fw + gap
    rect(fx, y + 6, fw, fh, fill=(186, 40, 40))                      # China
    for sx, sy, sr in ((9, 9, 3.5), (19, 6, 1.8), (22, 11, 1.8),
                       (19, 16, 1.8), (15, 19, 1.8)):
        d.ellipse([X(fx + sx - sr), X(y + 6 + sy - sr),
                   X(fx + sx + sr), X(y + 6 + sy + sr)], fill=(244, 200, 60))
    text(fx + fw / 2, y + h - 15, "CHINA", F(SANS_B, 9.5), INK, anchor="ma")
    grain(x, y, w, h, seed=3, n=120, alpha=10)
    rect(x, y, w, h, outline=RULE, width=1)


def tanker_panel(x, y, w, h):
    """A supertanker ablaze near the Strait of Hormuz."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h * 0.52, fill=(148, 138, 122))        # smoke sky
    rect(x + 1, y + h * 0.52, w - 2, h * 0.48 - 1, fill=(52, 74, 92))  # sea
    for i in range(5):                                               # smoke drift
        d.ellipse([X(x + w * 0.52 + i * 12), X(y + 2 + i * 2),
                   X(x + w * 0.52 + i * 12 + 24), X(y + 13 + i * 2)],
                  fill=(96, 90, 84, 150))
    hy = y + h * 0.60                                                # hull
    d.polygon([(X(x + 10), X(hy)), (X(x + w - 26), X(hy)),
               (X(x + w - 8), X(hy + 8)), (X(x + w - 34), X(hy + 13)),
               (X(x + 26), X(hy + 13))], fill=(30, 28, 30))
    rect(x + 10, hy - 4, w - 36, 4, fill=(150, 52, 40))              # red deck line
    rect(x + 22, hy - 13, 24, 9, fill=(226, 220, 206))               # superstructure
    rect(x + 27, hy - 18, 5, 5, fill=(60, 58, 56))
    for fxp, fh_ in ((0.52, 13), (0.58, 20), (0.64, 11)):            # flames amidships
        cx = x + w * fxp
        d.polygon([(X(cx - 5), X(hy - 3)), (X(cx), X(hy - 3 - fh_)),
                   (X(cx + 5), X(hy - 3))], fill=(232, 118, 34))
        d.polygon([(X(cx - 2.5), X(hy - 3)), (X(cx), X(hy - 3 - fh_ * 0.55)),
                   (X(cx + 2.5), X(hy - 3))], fill=(246, 190, 70))
        d.ellipse([X(cx - 7), X(hy - 12 - fh_), X(cx + 9), X(hy - 2 - fh_)],
                  fill=(80, 74, 68, 170))                            # smoke above flames
    grain(x, y, w, h, seed=19, n=150, alpha=12)
    rect(x, y, w, h, outline=RULE, width=1)


# ---------------------------------------------------------------- page

M = 28                 # page margin
CW = W - 2 * M         # content width (968)
COLW = 309             # three-column width
GUT = 20.5             # gutter
COL2 = M + COLW + GUT  # 357.5
COL3 = M + 2 * (COLW + GUT)  # 687


def vrule(x, y1, y2):
    line(x, y1, x, y2, fill=FAINT, width=1)


def brief_flow(x, y, head, body):
    """One World in Brief item: bold country head, then a two-line brief
    whose first line runs beside the head and second line runs full width."""
    hf, bf = F(SANS_B, 9), F(SERIF, 9.5)
    text(x, y, head, hf, RED)
    hw = tw(head, hf) + 6
    words, first, rest = body.split(), "", ""
    for wd in words:
        trial = wd if not first else first + " " + wd
        if tw(trial, bf) <= COLW - hw or not first:
            first = trial
        else:
            rest = " ".join(words[len(first.split()):])
            break
    else:
        rest = ""
    text(x + hw, y, first, bf, INK)
    if rest:
        second = wrap(rest, bf, COLW)
        text(x, y + 10.5, second[0], bf, INK)


# --- folio + masthead ---------------------------------------------------
line(M, 16, W - M, 16, width=2.5)
text(M, 22, "Vol. XLI  ·  No. 327", F(SANS, 10.5), SOFT)
text(W / 2, 21, "MONDAY, 23 NOVEMBER 2026", F(SANS_B, 12.5), RED, anchor="ma")
text(W - M, 22, "World Edition  ·  Price $2.00  ·  theworldtoday.news",
     F(SANS, 10.5), SOFT, anchor="ra")
text(W / 2, 38, "THE WORLD TODAY", F(DISPLAY, 45), INK, anchor="ma")
line(M, 94, W - M, 94, width=2.5)
line(M, 99, W - M, 99, width=1)

# --- markets ticker -------------------------------------------------------
rect(M, 105, CW, 22, fill=INK)
text(W / 2, 109.5,
     "NIKKEI 225  −5.06%    ·    KOSPI  −4%    ·    S&P 500  −3.7%    ·    "
     "NASDAQ  −5.3%    ·    BRENT  $92.29    ·    GOLD  +2.7%    ·    VIX  35.89",
     F(SANS_B, 11.5), (240, 234, 218), anchor="ma")

# --- inside today -----------------------------------------------------------
text(M, 133, "INSIDE TODAY:", F(SANS_B, 10), RED)
text(M + 92, 133,
     "Climate collapse — full report p.2–3   ·   Markets rout p.14   ·   "
     "Ukraine p.6   ·   Shenzhen summit p.8   ·   Riemann claim p.11   ·   Sport p.24",
     F(SANS, 10), SOFT)
line(M, 148, W - M, 148, width=1)

# --- lead story -------------------------------------------------------------
kicker(M, 156, "COP31  ·  ANTALYA, TÜRKIYE  ·  CLIMATE")
text(W - M, 156, "FIRST FAILURE OF UN TALKS SINCE 2009", F(SANS_B, 10.5),
     SOFT, anchor="ra")
text(W / 2, 170, "CLIMATE TALKS COLLAPSE", F(SERIF_B, 41), INK, anchor="ma")
text(W / 2, 214, "IN ANTALYA", F(SERIF_B, 41), INK, anchor="ma")
flow(M + 60, 260,
     "UN summit ends after two days of overtime with no agreement, as about "
     "130 parties reject a draft text that never once mentions fossil fuels",
     F(SERIF_I, 14), CW - 120, 18, SOFT, align="center")

plenary_panel(M, 302, CW, 78)
caption(M, 384, CW,
        "Empty chairs in the plenary hall in Antalya after delegations walked out on Sunday night.",
        "Illustration: Staff  ·  Reporting: Antalya")

text(M, 402, "By the Climate Desk", F(SERIF_BI, 11.5), INK)
LEAD_A = ("ANTALYA — The COP31 climate summit collapsed on Sunday night "
          "after two days of overtime, the first failure of the UN climate "
          "talks since 2009. The European Union and about 130 parties "
          "rejected a draft text that omitted any mention of fossil fuels, "
          "after oil-producing states lobbied to keep the words out.")
LEAD_B = ("Talks also broke down over climate finance for poorer nations. "
          "Delegates said the draft offered no path at all on phasing out "
          "oil, gas and coal, and no new date was set to meet again. "
          "Negotiators left Antalya with no agreement and no timetable.")
flow(M, 420, LEAD_A, F(SERIF, 11.5), COLW, 14.5)
vrule(COL2 - GUT / 2, 420, 502)
flow(COL2, 420, LEAD_B, F(SERIF, 11.5), COLW, 14.5)
vrule(COL3 - GUT / 2, 420, 502)
rect(COL3, 420, COLW, 84, fill=PAPER_DARK, outline=RULE, width=1)
text(COL3 + 13, 427, "“", F(SERIF_B, 28), RED)
flow(COL3 + 33, 432,
     "We came to Antalya to phase out fossil fuels. The words were taken "
     "out — and then the talks fell apart.",
     F(SERIF_BI, 12.5), COLW - 47, 15.5)
text(COL3 + 33, 484, "— A European negotiator, Sunday night",
     F(SANS_I, 9.5), SOFT)
line(M, 512, W - M, 512, width=1.5)

# --- row A: markets / ukraine / shenzhen ------------------------------------
RA = 520
kicker(M, RA, "MARKETS")
chart_panel(M, RA + 14, COLW, 44)
caption(M, RA + 61, COLW, "Screens in Tokyo as the AI rout went global.", "Staff")
y = flow(M, RA + 78, "AI SELL-OFF GOES GLOBAL", F(SERIF_B, 18), COLW, 21)
flow(M, y + 2,
     "Japan's Nikkei 225 fell 5.06% and South Korea's KOSPI slid about 4% "
     "as the rout in artificial-intelligence shares spread across Asia. "
     "Seoul pledged a stabilisation fund, Hong Kong hit a 19-month low, "
     "and US futures steadied early on Monday.",
     F(SERIF, 11), COLW, 13.5)

vrule(COL2 - GUT / 2, RA, RA + 180)
kicker(COL2, RA, "UKRAINE WAR")
rescue_panel(COL2, RA + 14, COLW, 44)
caption(COL2, RA + 61, COLW, "Rescue lights at the damaged block in Dymer.", "Agencies")
y = flow(COL2, RA + 78, "STRIKE ON FLATS KILLS 10 NEAR KYIV", F(SERIF_B, 18), COLW, 21)
flow(COL2, y + 2,
     "A strike on an apartment block in Dymer, north of Kyiv, killed at "
     "least 10 people. Rescuers pulled a seven-year-old boy alive from "
     "the rubble, and drones also struck homes in the capital overnight.",
     F(SERIF, 11), COLW, 13.5)

vrule(COL3 - GUT / 2, RA, RA + 180)
kicker(COL3, RA, "SHENZHEN SUMMIT")
flags_panel(COL3, RA + 14, COLW, 44)
caption(COL3, RA + 61, COLW, "Flags of the three powers at Shenzhen.", "Staff")
y = flow(COL3, RA + 78, "TRUMP, PUTIN, XI SIGN PEACE DECLARATION",
         F(SERIF_B, 18), COLW, 21)
flow(COL3, y + 2,
     "The three presidents issued a joint “Declaration toward Peace” at "
     "their trilateral summit in Shenzhen, pledging further talks. "
     "Mr Trump called Mr Putin “my friend” at the signing ceremony.",
     F(SERIF, 11), COLW, 13.5)
line(M, RA + 188, W - M, RA + 188, width=1.5)

# --- row B: hormuz / united states + science / sport -------------------------
RB = RA + 196  # 730
kicker(M, RB, "MIDDLE EAST")
tanker_panel(M, RB + 14, COLW, 40)
caption(M, RB + 57, COLW, "A tanker ablaze near the strait.", "Agencies")
y = flow(M, RB + 74, "TANKERS BURNING AT HORMUZ", F(SERIF_B, 17.5), COLW, 20)
flow(M, y + 2,
     "Iran said two supertankers hit mines and caught fire near the "
     "Strait of Hormuz. Mr Trump threatened to sink Iranian vessels "
     "running the blockade, and strikes were reported on Bahrain.",
     F(SERIF, 11), COLW, 13.5)

vrule(COL2 - GUT / 2, RB, RB + 172)
kicker(COL2, RB, "UNITED STATES")
y = flow(COL2, RB + 16, "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992",
         F(SERIF_B, 17.5), COLW, 20)
flow(COL2, y + 2,
     "Democrats clinched at least 258 House seats after a recount in "
     "North Carolina — their largest majority since 1992.",
     F(SERIF, 11), COLW, 13.5)
line(COL2, RB + 94, COL2 + COLW, RB + 94, fill=FAINT, width=1)
kicker(COL2, RB + 100, "SCIENCE", fill=NAVY)
y = flow(COL2, RB + 116, "RIEMANN PROOF CLAIMED",
         F(SERIF_B, 15.5), COLW, 19)
flow(COL2, y + 2,
     "Levent Alpöge, working with Claude, claimed a proof of the Riemann "
     "Hypothesis, unsolved for over 160 years. Experts are checking it.",
     F(SERIF, 11), COLW, 13.5)

rect(COL3, RB, COLW, 172, outline=RULE, width=1.2)                    # sport box
rect(COL3, RB, COLW, 20, fill=INK)
text(COL3 + 10, RB + 4, "SPORT", F(SANS_B, 11.5), (240, 234, 218))
text(COL3 + COLW - 10, RB + 5, "LAS VEGAS  ·  NEW YORK", F(SANS, 9),
     (200, 194, 178), anchor="ra")
y = flow(COL3 + 10, RB + 27, "VERSTAPPEN WINS IN LAS VEGAS",
         F(SERIF_B, 15.5), COLW - 20, 18)
y = flow(COL3 + 10, y + 1,
         "Max Verstappen won the Las Vegas Grand Prix, tightening his "
         "grip on the Formula One season.", F(SERIF, 10.5), COLW - 20, 13)
line(COL3 + 10, y + 4, COL3 + COLW - 10, y + 4, fill=FAINT, width=1)
y = flow(COL3 + 10, y + 9, "METS' RECORD $450M DEAL FOR SKUBAL",
         F(SERIF_B, 15.5), COLW - 20, 18)
flow(COL3 + 10, y + 1,
     "The New York Mets agreed a record nine-year, $450 million deal "
     "for pitcher Tarik Skubal.", F(SERIF, 10.5), COLW - 20, 13)
line(M, RB + 180, W - M, RB + 180, width=1.5)

# --- markets at a glance + weather -------------------------------------------
DB = RB + 186  # 916
rect(M, DB, 636, 38, fill=PAPER_DARK, outline=RULE, width=1)
text(M + 10, DB + 3, "MARKETS AT A GLANCE", F(SANS_B, 9), RED)
DATA = [("NIKKEI 225", "−5.06%"), ("KOSPI", "−4.0%"), ("S&P 500", "−3.7%"),
        ("NASDAQ", "−5.3%"), ("BRENT", "$92.29"), ("GOLD", "+2.7%"),
        ("VIX", "35.89"), ("HANG SENG", "19-mo low")]
for i, (name, val) in enumerate(DATA):
    cx = M + 10 + (i % 4) * 158
    cy = DB + 16 + (i // 4) * 12
    text(cx, cy, name, F(SANS_B, 8.5), SOFT)
    text(cx + 60, cy, val, F(SANS_B, 8.5),
         RED if val.startswith("−") else INK)
rect(M + 648, DB, 320, 38, outline=RULE, width=1)
text(M + 658, DB + 3, "WEATHER TODAY", F(SANS_B, 9), NAVY)
text(M + 658, DB + 16, "Antalya 18° cloudy  ·  Kyiv 2° snow  ·  Tokyo 11° rain",
     F(SANS, 8.5), SOFT)
text(M + 658, DB + 28, "New York 6° clear  ·  London 9° showers  ·  Shenzhen 24° humid",
     F(SANS, 8.5), SOFT)

# --- world in brief -------------------------------------------------------------
WB = DB + 40  # 958
rect(M, WB, CW, 17, fill=NAVY)
text(M + 10, WB + 3.5, "WORLD IN BRIEF", F(SANS_B, 10), (240, 234, 218))
text(W / 2, WB + 3.5, "PAGE 1  ·  WORLD", F(SANS, 9.5), (205, 208, 216),
     anchor="ma")
text(W - M - 10, WB + 3.5, "MONDAY, 23 NOVEMBER 2026", F(SANS_B, 10),
     (240, 234, 218), anchor="ra")
BRIEFS = [
    ("LIBYA", "Russian corvette Merkury sank at Benghazi naval base after a "
              "suspected Ukrainian naval-drone attack."),
    ("INDONESIA", "Fire at a candy factory in Banten killed three people; "
                  "dozens of workers were still missing."),
    ("JAPAN", "A preliminary magnitude 6.1 earthquake jolted northern "
              "Japan; no tsunami warning was issued."),
    ("SOUTH KOREA", "Exports topped $1 trillion for the first time; the "
                    "education minister quit over AI exam cheating."),
    ("BAHRAIN", "Strikes were reported on Bahrain as Hormuz tensions "
                "spread across the Gulf."),
    ("HONG KONG", "Shares hit a 19-month low as the AI sell-off deepened "
                  "across Asia."),
]
for i, (head, body) in enumerate(BRIEFS):
    bx = M + (i % 3) * (COLW + GUT)
    by = WB + 22 + (i // 3) * 22
    brief_flow(bx, by, head, body)

text(M, 1010, "Page 1  ·  WORLD  ·  Continued inside", F(SANS_B, 8.5), SOFT)
text(W - M, 1010, "Markets p.14  ·  Sport p.24  ·  theworldtoday.news",
     F(SANS, 8.5), SOFT, anchor="ra")

# ---------------------------------------------------------------- output

out = Path(__file__).resolve().parent.parent / "assets" / "final-page.png"
img.resize((W, H), Image.LANCZOS).save(out, optimize=True)
print("wrote", out)
