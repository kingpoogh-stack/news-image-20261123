"""Build-time renderer for the 23 November 2026 broadsheet front page (v2).

Composes a dense, realistic 1024x1024 newspaper front page with Pillow
and writes assets/final-page.png. Fully deterministic: fixed layout,
no wall-clock, no randomness, no network.
Run:  python3 tools/render_page.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (243, 238, 223)
PAPER_D = (231, 222, 198)
INK = (20, 19, 17)
GREY = (88, 84, 76)
RULE = (28, 27, 25)
RED = (139, 35, 32)
NAVY = (36, 52, 71)
WHITE = (246, 243, 233)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_BI = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, font, max_w, leading, fill=INK):
    for line in wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def centered(draw, y, text, font, fill=INK):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)
    return y + font.size + 4


def columns(draw, x, y, text, font, total_w, ncols, leading, gap=14, fill=INK):
    col_w = (total_w - gap * (ncols - 1)) // ncols
    lines = wrap(draw, text, font, col_w)
    per = (len(lines) + ncols - 1) // ncols
    bottom = y
    for c in range(ncols):
        cy = y
        for line in lines[c * per:(c + 1) * per]:
            draw.text((x + c * (col_w + gap), cy), line, font=font, fill=fill)
            cy += leading
        bottom = max(bottom, cy)
    return bottom


# ---------- procedural press-illustration panels ----------

def panel_conference(d, box):
    # Designed for a short, wide box (~84px tall): banner on top, then a
    # single row of delegates seated at a long table, two chairs empty.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(188, 180, 158))
    d.rectangle([x0, y0, x1, y0 + 27], fill=NAVY)
    tf = F(SANS_B, 17)
    t = "COP31  ·  ANTALYA"
    tw = d.textlength(t, font=tf)
    d.text((x0 + (x1 - x0 - tw) / 2, y0 + 5), t, font=tf, fill=WHITE)
    # small flag chips at both ends of the banner
    cols = [(168, 52, 46), (52, 122, 76), (206, 164, 52), (52, 84, 148)]
    for i, c in enumerate(cols):
        fx = x0 + 14 + i * 26 if i < 2 else x1 - 66 + (i - 2) * 26
        d.rectangle([fx, y0 + 7, fx + 20, y0 + 20], fill=c)
    ty = y1 - 26
    d.rectangle([x0 + 30, ty, x1 - 30, ty + 8], fill=(96, 74, 50))
    d.rectangle([x0 + 44, ty + 8, x1 - 44, y1 - 4], fill=(116, 92, 62))
    for i in range(11):
        cx = x0 + 70 + i * ((x1 - x0 - 140) // 10)
        if i in (4, 7):  # empty chairs: talks abandoned
            d.rectangle([cx - 10, ty - 15, cx + 10, ty], outline=(60, 56, 50), width=2)
            continue
        d.ellipse([cx - 7, ty - 21, cx + 7, ty - 7], fill=(34, 33, 36))
        d.rectangle([cx - 10, ty - 7, cx + 10, ty + 1], fill=(34, 33, 36))
        d.rectangle([cx - 5, ty - 4, cx + 5, ty], fill=(222, 218, 204))
    px = (x0 + x1) // 2 + 30
    d.line([px, ty + 4, px + 20, ty + 1], fill=(25, 25, 25), width=3)
    d.ellipse([px + 18, ty - 2, px + 27, ty + 5], fill=(25, 25, 25))


def panel_chart(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(34, 39, 50))
    for gx in range(x0 + 16, x1, 30):
        d.line([gx, y0 + 6, gx, y1 - 6], fill=(66, 72, 86), width=1)
    for gy in range(y0 + 12, y1, 20):
        d.line([x0 + 6, gy, x1 - 6, gy], fill=(66, 72, 86), width=1)
    fx = x1 - x0
    pts = [(x0 + 10, y0 + 14), (x0 + fx // 6, y0 + 21), (x0 + fx // 3, y0 + 12),
           (x0 + fx // 2, y0 + 34), (x0 + 2 * fx // 3, y0 + 28),
           (x0 + 5 * fx // 6, y0 + 50), (x1 - 12, y0 + 43)]
    d.line(pts, fill=(228, 74, 56), width=4)
    for p in pts:
        d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(242, 200, 88))
    lab = F(SANS_B, 14)
    d.text((x0 + 10, y1 - 21), "NIKKEI  -5.06%", font=lab, fill=(242, 200, 88))


def panel_dymer(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(158, 150, 138))
    d.rectangle([x0, y0, x1, y0 + 10], fill=(102, 104, 112))
    d.rectangle([x0 + 12, y0 + 13, x0 + 160, y1 - 5], fill=(122, 112, 98))
    for r in range(3):
        for c in range(4):
            wx, wy = x0 + 23 + c * 33, y0 + 20 + r * 15
            col = (38, 36, 34) if (r * 4 + c) % 3 == 0 else (214, 198, 148)
            d.rectangle([wx, wy, wx + 18, wy + 9], fill=col)
    d.polygon([(x0 + 116, y0 + 13), (x0 + 160, y0 + 13), (x0 + 160, y0 + 42),
               (x0 + 133, y0 + 35)], fill=(64, 58, 52))
    d.polygon([(x0 + 84, y1 - 5), (x0 + 124, y1 - 19), (x0 + 168, y1 - 5)],
              fill=(84, 76, 66))
    for lx in (x0 + 200, x0 + 250):
        d.ellipse([lx - 6, y0 + 15, lx + 6, y0 + 27], fill=(255, 214, 90))
        d.line([lx, y0 + 27, lx - 7, y1 - 5], fill=(38, 38, 38), width=3)
        d.line([lx, y0 + 27, lx + 7, y1 - 5], fill=(38, 38, 38), width=3)


def panel_tanker(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(146, 168, 180))
    sea_y = y0 + (y1 - y0) * 3 // 5
    d.rectangle([x0, sea_y, x1, y1], fill=(58, 92, 114))
    for wy in range(sea_y + 7, y1 - 3, 10):
        d.line([x0 + 7, wy, x1 - 7, wy], fill=(84, 118, 140), width=2)
    hx, hy = x0 + 18, sea_y + 1
    hull_w = (x1 - x0) - 36
    d.polygon([(hx, hy), (hx + hull_w, hy), (hx + hull_w - 16, hy + 11),
               (hx + 14, hy + 11)], fill=(48, 48, 52))
    d.rectangle([hx + 5, hy - 5, hx + hull_w - 5, hy], fill=(160, 58, 46))
    d.rectangle([hx + hull_w - 52, hy - 17, hx + hull_w - 28, hy - 5],
                fill=(224, 220, 208))
    d.rectangle([hx + 36, hy - 10, hx + 54, hy - 5], fill=(88, 88, 92))
    # flames and smoke, kept strictly inside the panel
    d.ellipse([hx + hull_w - 24, hy - 13, hx + hull_w - 4, hy + 1],
              fill=(236, 128, 48))
    d.ellipse([hx + hull_w - 17, hy - 19, hx + hull_w + 1, hy - 5],
              fill=(240, 168, 70))
    d.ellipse([hx + hull_w - 20, hy - 24, hx + hull_w + 2, hy - 10],
              fill=(100, 96, 92))


def panel_flags(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(206, 198, 176))
    labels = [("USA", (58, 78, 140)), ("RUSSIA", (196, 196, 190)),
              ("CHINA", (178, 44, 40))]
    third = (x1 - x0) // 3
    lf = F(SANS_B, 12)
    for i, (name, c) in enumerate(labels):
        fx = x0 + 14 + i * third
        d.line([fx, y0 + 8, fx, y1 - 22], fill=(45, 42, 38), width=2)
        d.rectangle([fx + 2, y0 + 10, fx + third - 24, y0 + 32], fill=c)
        if name == "USA":
            d.rectangle([fx + 2, y0 + 10, fx + third - 24, y0 + 32],
                        fill=(238, 234, 226))
            for s in range(3):
                d.rectangle([fx + 2, y0 + 13 + s * 7, fx + third - 24,
                             y0 + 16 + s * 7], fill=(178, 44, 40))
            d.rectangle([fx + 2, y0 + 10, fx + third // 2 - 4, y0 + 21],
                        fill=(58, 78, 140))
        if name == "RUSSIA":
            d.rectangle([fx + 2, y0 + 17, fx + third - 24, y0 + 25],
                        fill=(52, 84, 148))
            d.rectangle([fx + 2, y0 + 25, fx + third - 24, y0 + 32],
                        fill=(178, 44, 40))
        if name == "CHINA":
            d.rectangle([fx + 5, y0 + 13, fx + 12, y0 + 20], fill=(240, 200, 60))
        tw = d.textlength(name, font=lf)
        d.text((fx + (third - 18 - tw) / 2, y1 - 19), name, font=lf, fill=INK)
    d.rectangle([x0 + 18, y1 - 28, x1 - 18, y1 - 21], fill=(96, 74, 50))


# ---------- page composition ----------

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28
    CW = W - 2 * M

    # Masthead
    centered(d, 4, "THE  WORLD  TODAY", F(SERIF_B, 48))
    y = 62
    d.line([M, y, W - M, y], fill=RULE, width=2)
    y += 4
    f_meta = F(SANS, 11)
    left = "Vol. XLI  ·  No. 327"
    mid = "MONDAY, 23 NOVEMBER 2026"
    right = "World Edition  ·  Price $2.00"
    d.text((M, y + 1), left, font=f_meta, fill=INK)
    mf = F(SANS_B, 15)
    mw = d.textlength(mid, font=mf)
    d.text(((W - mw) / 2, y), mid, font=mf, fill=RED)
    rw = d.textlength(right, font=f_meta)
    d.text((W - M - rw, y + 1), right, font=f_meta, fill=INK)
    y += 20
    d.line([M, y, W - M, y], fill=RULE, width=3)
    d.line([M, y + 4, W - M, y + 4], fill=RULE, width=1)
    y += 10

    # Markets ticker strip
    d.rectangle([M, y, W - M, y + 22], fill=(26, 26, 28))
    ticker = ("NIKKEI 225  -5.06%   ·   KOSPI  -4%   ·   S&P 500  -3.7%   ·   NASDAQ  -5.3%   ·   "
              "BRENT  $92.29   ·   GOLD  +2.7%   ·   VIX  35.89")
    tf = F(SANS_B, 13)
    tw = d.textlength(ticker, font=tf)
    d.text(((W - tw) / 2, y + 5), ticker, font=tf, fill=WHITE)
    y += 29

    # Inside-today strip
    d.rectangle([M, y, W - M, y + 19], fill=PAPER_D)
    inside = ("INSIDE TODAY:   Climate collapse — full report p.2–3   ·   Markets rout p.14   ·   "
              "Ukraine p.6   ·   Shenzhen summit p.8   ·   Sport p.24")
    inf = F(SANS, 12)
    iw = d.textlength(inside, font=inf)
    d.text(((W - iw) / 2, y + 4), inside, font=inf, fill=INK)
    y += 26

    # ---- Lead story ----
    d.text((M, y), "COP31  ·  ANTALYA, TÜRKIYE  ·  CLIMATE", font=F(SANS_B, 13), fill=RED)
    late = "FIRST FAILURE OF UN TALKS SINCE 2009"
    lw = d.textlength(late, font=F(SANS_B, 12))
    d.text((W - M - lw, y + 1), late, font=F(SANS_B, 12), fill=GREY)
    y += 18
    y = centered(d, y, "CLIMATE TALKS COLLAPSE", F(SERIF_B, 46))
    y = centered(d, y - 4, "IN ANTALYA", F(SERIF_B, 46))
    stand = ("UN summit ends after two days of overtime with no agreement, as about 130 parties "
             "reject a draft text that never once mentions fossil fuels")
    y = para(d, M + 70, y + 1, stand, F(SERIF_I, 15), CW - 140, 19)
    y += 6
    panel_conference(d, (M, y, W - M, y + 84))
    d.rectangle([M, y, W - M, y + 84], outline=RULE, width=2)
    y += 89
    cap = ("Empty chairs in the plenary hall in Antalya after delegates walked out on Sunday night.")
    y = para(d, M, y, cap, F(SERIF_I, 11), CW - 200, 14, fill=GREY)
    cred = "Illustration: Staff  ·  Reporting: Antalya"
    cw_ = d.textlength(cred, font=F(SANS, 10))
    d.text((W - M - cw_, y - 14), cred, font=F(SANS, 10), fill=GREY)
    y += 2
    d.text((M, y), "By the Climate Desk", font=F(SERIF_BI, 12), fill=INK)
    y += 16
    lead = ("ANTALYA — The COP31 climate summit collapsed on Sunday night after two days of "
            "overtime, the first failure of the UN climate talks since 2009. The European "
            "Union and about 130 parties rejected a draft text that omitted any mention of "
            "fossil fuels, after oil-producing states lobbied to keep the words out. Talks "
            "also broke down over climate finance. Delegates said the draft offered no "
            "path at all on phasing out oil, gas and coal. Negotiators left with no "
            "agreement and no date to meet again.")
    y = columns(d, M, y, lead, F(SERIF, 12), CW, 3, 14)
    y += 7
    d.line([M, y, W - M, y], fill=RULE, width=3)
    y += 9

    # ---- Story grid helpers ----
    col_w = (CW - 24) // 3
    xs = [M, M + col_w + 12, M + 2 * (col_w + 12)]
    f_h = F(SERIF_B, 20)
    f_h2 = F(SERIF_B, 18)
    f_b = F(SERIF, 11.5)

    def headline(idx, yy, text, font=f_h, xoff=0, woff=0):
        return para(d, xs[idx] + xoff, yy, text, font, col_w - woff,
                    font.size + 3)

    def body(idx, yy, text, xoff=0, woff=0):
        return para(d, xs[idx] + xoff, yy, text, f_b, col_w - woff, 14)

    def kicker(idx, yy, text, xoff=0):
        d.text((xs[idx] + xoff, yy), text, font=F(SANS_B, 11), fill=RED)
        return yy + 15

    def panel(idx, yy, fn, h, caption):
        fn(d, (xs[idx], yy, xs[idx] + col_w, yy + h))
        d.rectangle([xs[idx], yy, xs[idx] + col_w, yy + h], outline=RULE, width=1)
        yy += h + 3
        yy = para(d, xs[idx], yy, caption, F(SERIF_I, 10), col_w, 12, fill=GREY)
        return yy + 3

    # ---- Row 1: Markets / Ukraine / Shenzhen ----
    row1 = y
    y1 = kicker(0, row1, "MARKETS")
    y1 = panel(0, y1, panel_chart, 54, "Screens in Tokyo as the AI rout went global.")
    y1 = headline(0, y1, "AI SELL-OFF GOES GLOBAL")
    y1 += 1
    y1 = body(0, y1, "Japan's Nikkei 225 fell 5.06% and South Korea's KOSPI slid about 4% "
                     "as the rout in AI shares spread across Asia. Seoul pledged a "
                     "stabilisation fund, Hong Kong hit a 19-month low, and US futures "
                     "steadied early on Monday.")

    y2 = kicker(1, row1, "UKRAINE WAR")
    y2 = panel(1, y2, panel_dymer, 54, "Rescue lights at the damaged block in Dymer.")
    y2 = headline(1, y2, "STRIKE ON FLATS KILLS 10 NEAR KYIV")
    y2 += 1
    y2 = body(1, y2, "A strike on an apartment block in Dymer, north of Kyiv, killed at "
                     "least 10 people. Rescuers pulled a seven-year-old boy alive from "
                     "the rubble, and drones also struck homes in the capital.")

    y3 = kicker(2, row1, "SHENZHEN SUMMIT")
    y3 = panel(2, y3, panel_flags, 54, "Flags of the three powers at Shenzhen.")
    y3 = headline(2, y3, "TRUMP, PUTIN, XI SIGN PEACE DECLARATION")
    y3 += 1
    y3 = body(2, y3, "The three presidents issued a joint \u201cDeclaration toward Peace\u201d "
                     "at their trilateral summit in Shenzhen, pledging further talks. "
                     "Mr Trump called Mr Putin \u201cmy friend\u201d at the signing.")

    row1_bottom = max(y1, y2, y3)
    for vx in (xs[1] - 6, xs[2] - 6):
        d.line([vx, row1, vx, row1_bottom], fill=(170, 162, 142), width=1)
    y = row1_bottom + 7
    d.line([M, y, W - M, y], fill=RULE, width=1)
    y += 8

    # ---- Row 2: Hormuz / US+Science / Sport ----
    row2 = y
    z1 = kicker(0, row2, "MIDDLE EAST")
    z1 = headline(0, z1, "TANKERS BURNING AT HORMUZ", font=f_h2)
    z1 += 1
    z1 = panel(0, z1, panel_tanker, 42, "A tanker ablaze near the strait.")
    z1 = body(0, z1, "Iran said two supertankers hit mines and caught fire near the Strait "
                     "of Hormuz. Mr Trump threatened to sink Iranian vessels running the "
                     "blockade, and strikes were reported on Bahrain.")

    z2 = kicker(1, row2, "UNITED STATES")
    z2 = headline(1, z2, "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992", font=f_h2)
    z2 += 1
    z2 = body(1, z2, "Democrats clinched at least 258 House seats after a recount in North "
                     "Carolina — their largest majority since 1992.")
    z2 += 3
    d.line([xs[1], z2, xs[1] + col_w, z2], fill=RULE, width=1)
    z2 += 4
    z2 = kicker(1, z2, "SCIENCE")
    z2 = headline(1, z2, "RIEMANN HYPOTHESIS: PROOF CLAIMED", font=f_h2)
    z2 += 1
    z2 = body(1, z2, "Levent Alp\u00f6ge, working with Claude, claimed a proof of the "
                     "Riemann Hypothesis, unsolved for over 160 years. Experts are "
                     "checking the work.")

    # Sport box in column 3
    sx, sw = xs[2], col_w
    sport_top = row2
    z3 = kicker(2, row2, "SPORT")
    z3 = headline(2, z3, "VERSTAPPEN WINS IN LAS VEGAS", font=f_h2)
    z3 += 1
    z3 = body(2, z3, "Max Verstappen won the Las Vegas Grand Prix, tightening his grip "
                     "on the Formula One season.")
    z3 += 5
    d.line([sx, z3, sx + sw, z3], fill=RULE, width=1)
    z3 += 6
    z3 = headline(2, z3, "METS' RECORD $450M DEAL FOR SKUBAL", font=f_h2)
    z3 += 1
    z3 = body(2, z3, "The New York Mets agreed a record nine-year, $450 million deal "
                     "for pitcher Tarik Skubal.")

    row2_bottom = max(z1, z2, z3)
    # sport box outline around column 3 of row 2
    d.rectangle([sx - 5, sport_top - 4, sx + sw + 5, row2_bottom + 4],
                outline=RULE, width=1)
    d.rectangle([sx - 5, sport_top - 4, sx + sw + 5, sport_top + 11], fill=(26, 26, 28))
    d.text((sx, sport_top - 3), "SPORT", font=F(SANS_B, 11), fill=WHITE)
    for vx in (xs[1] - 6,):
        d.line([vx, row2, vx, row2_bottom], fill=(170, 162, 142), width=1)
    y = row2_bottom + 11
    d.line([M, y, W - M, y], fill=RULE, width=3)
    y += 8

    # ---- World in Brief: full width, 3 columns x 2 items ----
    d.rectangle([M, y, W - M, y + 20], fill=NAVY)
    d.text((M + 10, y + 4), "WORLD IN BRIEF", font=F(SANS_B, 13), fill=WHITE)
    dat = "MONDAY, 23 NOVEMBER 2026"
    dw = d.textlength(dat, font=F(SANS_B, 11))
    d.text((W - M - 10 - dw, y + 5), dat, font=F(SANS_B, 11), fill=WHITE)
    y += 24
    briefs = [
        ("LIBYA", "Russian corvette Merkury sank at Benghazi naval base after a "
                  "suspected Ukrainian naval-drone attack."),
        ("INDONESIA", "Fire at a candy factory in Banten killed three people; dozens "
                      "of workers still missing."),
        ("JAPAN", "A preliminary magnitude 6.1 earthquake jolted northern Japan."),
        ("SOUTH KOREA", "Exports topped $1 trillion for the first time; education "
                        "minister resigned over AI exam cheating."),
        ("BAHRAIN", "Strikes were reported on Bahrain as Hormuz tensions spread "
                    "across the Gulf."),
        ("HONG KONG", "Shares hit a 19-month low as the AI sell-off deepened in Asia."),
    ]
    bcol_w = (CW - 20) // 3
    bottoms = []
    for ci in range(3):
        bx = M + ci * (bcol_w + 10)
        cy = y
        for tag, text in briefs[ci * 2:(ci + 1) * 2]:
            d.text((bx, cy), tag, font=F(SANS_B, 11), fill=RED)
            cy += 14
            cy = para(d, bx, cy, text, F(SERIF, 11), bcol_w, 11)
            cy += 3
        bottoms.append(cy)
    y = max(bottoms) + 2

    # Footer folio
    fy = H - 32
    d.line([M, fy, W - M, fy], fill=RULE, width=2)
    d.text((M, fy + 7), "Page 1  ·  WORLD", font=F(SANS_B, 12), fill=INK)
    foot = "Monday, 23 November 2026  ·  Continued inside  ·  Markets p.14  ·  Sport p.24"
    fw = d.textlength(foot, font=F(SANS, 12))
    d.text((W - M - fw, fy + 7), foot, font=F(SANS, 12), fill=GREY)

    out = Path(__file__).resolve().parent.parent / "assets" / "final-page.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    print(f"row1_bottom={row1_bottom} row2_bottom={row2_bottom} brief_bottom={y}")


if __name__ == "__main__":
    build()
