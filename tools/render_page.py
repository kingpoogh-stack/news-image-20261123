"""Build-time renderer for the 23 November 2026 broadsheet front page.

Composes a 1024x1024 newspaper front page with Pillow and writes
assets/final-page.png. Fully deterministic: fixed layout numbers,
no wall-clock, no randomness, no network.
Run:  python3 tools/render_page.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (245, 241, 230)
INK = (18, 18, 18)
GREY = (90, 88, 82)
RULE = (30, 30, 30)
LIGHT = (232, 226, 208)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


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


# ---------- procedural press-illustration panels ----------

def panel_conference(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(196, 190, 168))
    d.rectangle([x0, y0, x1, y0 + 26], fill=(58, 64, 78))
    # flags row
    cols = [(150, 60, 55), (60, 90, 150), (60, 130, 80), (210, 170, 60),
            (120, 60, 140), (200, 120, 40), (50, 130, 160), (170, 60, 90)]
    for i, c in enumerate(cols):
        fx = x0 + 22 + i * 52
        d.line([fx, y0 + 30, fx, y0 + 78], fill=(40, 40, 40), width=2)
        d.rectangle([fx + 2, y0 + 32, fx + 34, y0 + 52], fill=c)
    # delegates silhouettes
    for i in range(9):
        cx = x0 + 50 + i * 46
        cy = y1 - 34
        d.ellipse([cx - 9, cy - 26, cx + 9, cy - 8], fill=(35, 35, 38))
        d.rectangle([cx - 13, cy - 8, cx + 13, cy + 22], fill=(35, 35, 38))
    # empty podium centre
    px = (x0 + x1) // 2
    d.rectangle([px - 26, y1 - 62, px + 26, y1 - 10], fill=(105, 82, 55))
    d.rectangle([px - 32, y1 - 68, px + 32, y1 - 58], fill=(80, 62, 42))
    d.line([px, y1 - 68, px + 14, y1 - 88], fill=(30, 30, 30), width=3)


def panel_chart(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(38, 42, 52))
    for gx in range(x0 + 18, x1, 36):
        d.line([gx, y0 + 8, gx, y1 - 8], fill=(70, 76, 90), width=1)
    for gy in range(y0 + 14, y1, 24):
        d.line([x0 + 8, gy, x1 - 8, gy], fill=(70, 76, 90), width=1)
    pts = [(x0 + 12, y0 + 22), (x0 + 55, y0 + 30), (x0 + 95, y0 + 20),
           (x0 + 130, y0 + 48), (x0 + 165, y0 + 42), (x0 + 205, y0 + 78),
           (x0 + 245, y0 + 62), (x0 + 282, y0 + 70)]
    d.line(pts, fill=(225, 70, 55), width=4)
    for p in pts:
        d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(240, 200, 90))
    # skyline (low silhouette so the plunging line stays readable above it)
    for i, bh in enumerate([14, 20, 16, 22, 15, 19, 12]):
        bx = x0 + 14 + i * 42
        d.rectangle([bx, y1 - bh, bx + 28, y1], fill=(22, 24, 30))


def panel_dymer(d, box):
    # Compact panel: every element stays strictly inside the box so the
    # illustration never spills onto the headline below it.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(168, 160, 148))
    d.rectangle([x0, y0, x1, y0 + 14], fill=(110, 112, 118))
    # damaged apartment block (left two-thirds, 3 floors of windows)
    d.rectangle([x0 + 18, y0 + 18, x0 + 178, y1 - 8], fill=(128, 118, 104))
    for r in range(3):
        for c in range(4):
            wx, wy = x0 + 30 + c * 36, y0 + 26 + r * 18
            col = (40, 38, 36) if (r * 4 + c) % 3 == 0 else (215, 200, 150)
            d.rectangle([wx, wy, wx + 20, wy + 10], fill=col)
    # collapsed corner: a dark diagonal scar inside the block only
    d.polygon([(x0 + 132, y0 + 18), (x0 + 178, y0 + 18), (x0 + 178, y0 + 52),
               (x0 + 150, y0 + 44)], fill=(70, 64, 58))
    # rubble heap at the foot of the block
    d.polygon([(x0 + 96, y1 - 8), (x0 + 140, y1 - 24), (x0 + 184, y1 - 8)],
              fill=(88, 80, 70))
    # rescue floodlights on tripods (right side, clear of the block)
    for lx in (x0 + 222, x0 + 272):
        d.ellipse([lx - 7, y0 + 22, lx + 7, y0 + 36], fill=(255, 214, 90))
        d.line([lx, y0 + 36, lx - 8, y1 - 8], fill=(40, 40, 40), width=3)
        d.line([lx, y0 + 36, lx + 8, y1 - 8], fill=(40, 40, 40), width=3)


def panel_tanker(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(150, 172, 182))
    d.rectangle([x0, y0 + 62, x1, y1], fill=(62, 96, 118))
    for wy in range(y0 + 74, y1 - 6, 14):
        d.line([x0 + 10, wy, x1 - 10, wy], fill=(86, 122, 142), width=2)
    hx, hy = x0 + 36, y0 + 52
    d.polygon([(hx, hy), (hx + 220, hy), (hx + 198, hy + 20), (hx + 20, hy + 20)],
              fill=(52, 52, 56))
    d.rectangle([hx + 8, hy - 8, hx + 212, hy], fill=(168, 62, 48))
    d.rectangle([hx + 150, hy - 30, hx + 182, hy - 8], fill=(225, 222, 210))
    d.rectangle([hx + 60, hy - 18, hx + 84, hy - 8], fill=(90, 90, 94))
    # smoke / fire glow
    d.ellipse([hx + 196, hy - 34, hx + 224, hy - 8], fill=(235, 130, 50))
    d.ellipse([hx + 210, hy - 52, hx + 246, hy - 20], fill=(105, 100, 96))


# ---------- page composition ----------

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 30           # margin
    CW = W - 2 * M   # content width

    # Masthead
    centered(d, 10, "THE  WORLD  TODAY", F(SERIF_B, 60))
    y = 82
    d.line([M, y, W - M, y], fill=RULE, width=2)
    y += 5
    f_meta = F(SANS, 12)
    left = "Vol. XLI  ·  No. 327"
    mid = "Monday, 23 November 2026"
    right = "World Edition  ·  Price $2.00"
    d.text((M, y), left, font=f_meta, fill=INK)
    mw = d.textlength(mid, font=F(SANS_B, 13))
    d.text(((W - mw) / 2, y - 1), mid, font=F(SANS_B, 13), fill=INK)
    rw = d.textlength(right, font=f_meta)
    d.text((W - M - rw, y), right, font=f_meta, fill=INK)
    y += 20
    d.line([M, y, W - M, y], fill=RULE, width=3)
    d.line([M, y + 4, W - M, y + 4], fill=RULE, width=1)
    y += 12

    # Markets ticker strip
    d.rectangle([M, y, W - M, y + 24], fill=(28, 28, 30))
    ticker = ("NIKKEI 225 -5.06%  ·  KOSPI -4%  ·  S&P 500 -3.7%  ·  NASDAQ -5.3%  ·  "
              "BRENT $92.29  ·  WTI $83.26  ·  GOLD +2.7%  ·  VIX 35.89")
    tf = F(SANS_B, 13)
    tw = d.textlength(ticker, font=tf)
    d.text(((W - tw) / 2, y + 5), ticker, font=tf, fill=(245, 241, 230))
    y += 34

    # Lead story
    d.text((M, y), "COP31  ·  ANTALYA", font=F(SANS_B, 13), fill=(150, 30, 25))
    y += 20
    y = centered(d, y, "CLIMATE TALKS COLLAPSE", F(SERIF_B, 47))
    y = centered(d, y - 2, "IN ANTALYA", F(SERIF_B, 47))
    y += 2
    stand = ("UN summit ends after two days of overtime with no agreement, "
             "as 130 parties reject a draft that never mentions fossil fuels")
    y = para(d, M + 90, y, stand, F(SERIF_I, 15), CW - 180, 19)
    y += 6
    panel_conference(d, (M, y, W - M, y + 148))
    d.rectangle([M, y, W - M, y + 148], outline=RULE, width=2)
    y += 154
    y = para(d, M, y, "Delegates leave the plenary hall in Antalya after the talks broke down on Sunday night.  (Illustration)",
             F(SERIF_I, 11), CW, 14, fill=GREY)
    y += 4
    lead = ("ANTALYA — The COP31 climate summit collapsed on Sunday night after two days of "
            "overtime, the first failure of the UN talks since 2009. The European Union and "
            "about 130 parties rejected a draft text that omitted any mention of fossil fuels, "
            "after oil-producing states lobbied to keep them out. Negotiators left without an "
            "overall agreement, and no date was set to resume.")
    colw = (CW - 16) // 2
    lines = wrap(d, lead, F(SERIF, 13), colw)
    half = (len(lines) + 1) // 2
    ly = y
    for line in lines[:half]:
        d.text((M, ly), line, font=F(SERIF, 13), fill=INK); ly += 16
    ly2 = y
    for line in lines[half:]:
        d.text((M + colw + 16, ly2), line, font=F(SERIF, 13), fill=INK); ly2 += 16
    y = max(ly, ly2) + 8
    d.line([M, y, W - M, y], fill=RULE, width=3)
    y += 10

    # Lower grid: three columns
    col_w = (CW - 24) // 3
    xs = [M, M + col_w + 12, M + 2 * (col_w + 12)]
    f_h = F(SERIF_B, 17)
    f_h2 = F(SERIF_B, 15)
    f_b = F(SERIF, 12)

    def story(idx, yy, head, body, font_h=f_h, panel=None, caption=None):
        if panel is not None:
            panel(d, (xs[idx], yy, xs[idx] + col_w, yy + 84))
            d.rectangle([xs[idx], yy, xs[idx] + col_w, yy + 84], outline=RULE, width=1)
            yy += 88
            yy = para(d, xs[idx], yy, caption, F(SERIF_I, 10), col_w, 12, fill=GREY)
            yy += 3
        yy = para(d, xs[idx], yy, head, font_h, col_w, font_h.size + 3)
        yy += 2
        yy = para(d, xs[idx], yy, body, f_b, col_w, 15)
        return yy + 8

    # Column 1: Markets + Shenzhen
    y1 = y
    y1 = story(0, y1, "AI SELL-OFF GOES GLOBAL",
               "Japan's Nikkei fell 5.06% and South Korea's KOSPI slid about 4%, as Seoul "
               "pledged a stabilisation fund. Hong Kong hit a 19-month low after last week's "
               "plunge in US AI shares. US futures rebounded early on Monday.",
               panel=panel_chart, caption="Screens in Tokyo as the AI rout spread across Asia.")
    d.line([xs[0], y1 - 2, xs[0] + col_w, y1 - 2], fill=RULE, width=1)
    y1 = story(0, y1 + 4, "TRUMP, PUTIN AND XI SIGN PEACE DECLARATION",
               "The three presidents issued a \u201cDeclaration toward Peace\u201d at their "
               "trilateral summit in Shenzhen. Mr Trump called Mr Putin \u201cmy friend\u201d "
               "as the leaders pledged further talks.", font_h=f_h2)

    # Column 2: Ukraine + Hormuz
    y2 = y
    y2 = story(1, y2, "STRIKE ON FLATS KILLS 10 NEAR KYIV",
               "A Russian strike on an apartment block in Dymer, north of Kyiv, killed at "
               "least 10 people. Rescuers pulled a seven-year-old boy alive from the rubble, "
               "and drones struck homes in the capital overnight.",
               panel=panel_dymer, caption="Rescue lights at the damaged block in Dymer.")
    d.line([xs[1], y2 - 2, xs[1] + col_w, y2 - 2], fill=RULE, width=1)
    y2 = story(1, y2 + 4, "TANKERS HIT MINES NEAR HORMUZ",
               "Iran said two supertankers hit mines and caught fire near the Strait of "
               "Hormuz. Mr Trump threatened to sink Iranian vessels running the naval "
               "blockade, and strikes were reported on Bahrain.", font_h=f_h2,
               panel=None)

    # Column 3: US politics + Science + Sport
    y3 = y
    y3 = story(2, y3, "DEMOCRATS TAKE BIGGEST HOUSE MAJORITY SINCE 1992",
               "Democrats clinched at least 258 House seats after a recount in North "
               "Carolina, their largest majority since 1992.", font_h=f_h2)
    d.line([xs[2], y3 - 2, xs[2] + col_w, y3 - 2], fill=RULE, width=1)
    y3 = story(2, y3 + 4, "CLAIM OF PROOF FOR RIEMANN HYPOTHESIS",
               "Anthropic mathematician Levent Alp\u00f6ge, working with Claude, claimed a "
               "proof of the Riemann Hypothesis, unsolved for over 160 years. Experts are "
               "checking the work.", font_h=f_h2)
    d.line([xs[2], y3 - 2, xs[2] + col_w, y3 - 2], fill=RULE, width=1)
    y3 = story(2, y3 + 4, "VERSTAPPEN WINS IN LAS VEGAS; METS' $450M DEAL",
               "Max Verstappen won the Las Vegas Grand Prix. The New York Mets agreed a "
               "record nine-year, $450 million deal for pitcher Tarik Skubal.", font_h=f_h2)

    # World in brief strip
    by = max(y1, y2, y3) + 2
    d.line([M, by, W - M, by], fill=RULE, width=2)
    by += 8
    d.text((M, by), "WORLD IN BRIEF", font=F(SANS_B, 13), fill=INK)
    by += 20
    brief = ("LIBYA: The Russian corvette Merkury sank at Benghazi naval base after a suspected Ukrainian naval-drone attack.   ·   "
             "INDONESIA: A fire at a candy factory in Banten killed three people, with dozens of workers still missing.   ·   "
             "JAPAN: A preliminary magnitude 6.1 earthquake jolted northern Japan.   ·   "
             "SOUTH KOREA: Annual exports topped $1 trillion for the first time; the education minister resigned over an AI exam-cheating scandal.")
    by = para(d, M, by, brief, F(SERIF, 12), CW, 15)
    by += 6
    # Tanker mini-panel + Hormuz note sits in brief area right? keep footer clean
    d.line([M, by, W - M, by], fill=RULE, width=3)
    by += 8
    d.text((M, by), "Page 1  ·  WORLD", font=F(SANS_B, 12), fill=INK)
    cont = "Continued inside  ·  Markets p.14  ·  Sport p.24"
    cw2 = d.textlength(cont, font=F(SANS, 12))
    d.text((W - M - cw2, by), cont, font=F(SANS, 12), fill=GREY)

    out = Path(__file__).resolve().parent.parent / "assets" / "final-page.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
