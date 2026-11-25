#!/usr/bin/env python3
"""Draws the README header, divider and section icons.  Usage: python3 scripts/night.py  (needs Pillow)"""
import math
import random

from pixel_art import BIG, CAT, CAT_PAL, Layer, save, text_width

SKY = ["#070b1f", "#0a1029", "#0e1634", "#131d40", "#1a264d", "#23305a", "#2f3b68"]
CREAM, GOLD = "#f7e8c3", "#ffd98a"


def big_text(layer, x, y, t, c, s=2):
    small = Layer(text_width(t), 5)
    small.text(0, 0, t, c)
    im = small.im.resize((small.im.width * s, 5 * s), 0)
    layer.im.paste(im, (x, y), im)


def header():
    W, H, LEDGE = 424, 176, 146
    rnd = random.Random(2005)
    new = lambda style="", cls="": Layer(W, H, style, cls)
    b = new()
    for i, c in enumerate(SKY):
        y = i * LEDGE // len(SKY)
        b.r(0, y, W, H - y, c)
        for k, step in enumerate((2, 4)):                        # dithered band edges
            for x in range(k, W, step) if i else ():
                b.r(x, y - 1 - k, 1, 1, c)

    # moon with a soft stepped halo
    mx, my = 338, 48
    for r, c in ((46, "#121b3b"), (38, "#1a2549"), (31, "#283459")):
        b.d.ellipse((mx - r, my - r, mx + r, my + r), fill=c)
    b.d.ellipse((mx - 24, my - 24, mx + 24, my + 24), fill=CREAM)
    for x, y, r in ((-9, -8, 5), (8, 6, 6), (-6, 11, 3), (11, -10, 3), (-16, 3, 2)):
        b.d.ellipse((mx + x - r, my + y - r, mx + x + r, my + y + r), fill="#e2d0a4")
        b.d.arc((mx + x - r, my + y - r, mx + x + r, my + y + r), 120, 300, fill="#cbb78a")

    stars = [new(f"animation:tw {t}s steps(4) -{t / 3:.1f}s infinite") for t in (3, 4.5, 6)]
    for i in range(150):
        x, y = rnd.randrange(W), int(rnd.random() ** 1.4 * 100)
        if math.hypot(x - mx, y - my) < 48:
            continue
        c = rnd.choice((CREAM, CREAM, "#9fb4e8", GOLD))
        l = stars[i % 3]
        l.r(x, y, 1, 1, c)
        if i % 16 == 0:
            l.r(x - 1, y, 3, 1, c); l.r(x, y - 1, 1, 3, c)

    # thin clouds
    for x, y, w in ((268, 70, 60), (284, 73, 92), (30, 108, 70), (48, 111, 96), (356, 96, 60)):
        b.r(x, y, w, 2, "#39466f"); b.r(x + 6, y - 1, w - 18, 1, "#39466f")

    # city in three layers
    wins = [new(f"animation:a {t}s steps(1) -{t / 2}s infinite") for t in (7, 11, 17)]
    red = new("animation:a 2s steps(1) infinite")
    for col, edge, lo, hi, lit in (("#2a3562", "#34406f", 24, 50, 0), ("#1a2348", "#26305a", 16, 42, .18),
                                   ("#0e1430", "#19213f", 8, 28, .34)):
        x = -3
        while x < W:
            w, h = rnd.randrange(14, 30), rnd.randrange(lo, hi)
            top = LEDGE - h
            for l in wins:
                l.r(x, top, w, h, (0, 0, 0, 0))
            red.r(x, top, w, h, (0, 0, 0, 0))
            b.r(x, top, w, h, col); b.r(x, top, w, 1, edge); b.r(x, top, 1, h, edge)
            kind = rnd.random()
            if kind < .25:                                       # stepped roof
                b.r(x + 4, top - 4, w - 8, 4, col); b.r(x + 4, top - 4, w - 8, 1, edge)
            elif kind < .42:                                     # antenna
                b.r(x + w // 2, top - 10, 1, 10, col)
                if lit:
                    red.r(x + w // 2, top - 11, 1, 2, "#ff6b57")
            elif kind < .55 and lit:                             # water tank
                b.r(x + 4, top - 8, 7, 5, col); b.r(x + 4, top - 3, 1, 3, col); b.r(x + 10, top - 3, 1, 3, col)
            if lit:
                for wy in range(top + 4, LEDGE - 2, 5):
                    for wx in range(x + 3, x + w - 3, 4):
                        q = rnd.random()
                        tone = rnd.choice((GOLD, GOLD, "#f0a860", "#8fd3e8"))
                        if q < lit:
                            b.r(wx, wy, 2, 2, tone)
                        elif q < lit + .07:
                            wins[rnd.randrange(3)].r(wx, wy, 2, 2, tone)
                        else:
                            b.r(wx, wy, 2, 2, edge)
            x += w + rnd.choice((0, 0, 1, 3))

    # rooftop
    b.r(0, LEDGE, W, 3, "#6a5a86"); b.r(0, LEDGE + 3, W, 1, "#453a63")
    b.r(0, LEDGE + 4, W, H - LEDGE - 4, "#2a2346"); b.r(0, H - 4, W, 4, "#1c1733")
    for j, y in enumerate(range(LEDGE + 5, H - 5, 5)):
        for x in range(-8 + j % 2 * 8, W, 16):
            b.r(x, y, 15, 4, rnd.choice(("#332b54", "#332b54", "#3a315e", "#2f274d")))
    for x in range(0, W, 3):                                     # moonlight on the ledge
        if 270 < x < 410:
            b.r(x, LEDGE, 2, 1, "#a596c4")

    # string lights
    for x0, x1 in ((0, 106), (106, 212), (212, 318), (318, 424)):
        b.r(x0, 118, 2, 28, "#0a0d22")
        for x in range(x0, x1):
            t = (x - x0) / (x1 - x0)
            b.r(x, 119 + round(36 * t * (1 - t)), 1, 1, "#0a0d22")
        for k in range(1, 8):
            x = x0 + k * (x1 - x0) // 8
            t = (x - x0) / (x1 - x0)
            y = 120 + round(36 * t * (1 - t))
            c = (GOLD, "#ff9e7a", "#8fd3e8")[k % 3]
            b.r(x - 1, y, 3, 3, "#4b3f52"); b.r(x, y, 1, 1, "#0a0d22")
            stars[k % 3].r(x - 1, y + 1, 3, 2, c)

    # laptop, mug, plant
    for l in (*stars, *wins, red):                               # lights stay behind the props
        for x, y, w, h in ((60, 122, 40, 24), (52, 144, 56, 2), (116, 136, 13, 10), (21, 136, 16, 10),
                           (20, 115, 18, 21), (0, LEDGE, W, H - LEDGE)):
            l.r(x, y, w, h, (0, 0, 0, 0))
    b.r(60, 122, 40, 24, "#0a0d22"); b.r(61, 123, 38, 22, "#8d98b8"); b.r(63, 125, 34, 17, "#0d1f2c")
    b.r(56, 144, 48, 2, "#b8c2dc"); b.r(52, 145, 56, 1, "#8d98b8")
    lines = []
    code = [(0, [(6, "#ff8f6b"), (10, CREAM)]), (3, [(5, "#8fd3c1"), (13, GOLD)]), (3, [(8, CREAM), (6, "#8fd3c1")]),
            (6, [(4, "#ff8f6b"), (9, GOLD)]), (0, [(3, CREAM)])]
    for i, (ind, toks) in enumerate(code):
        l, x = new(f"animation:ty 12s steps(1) {i * 1.2:.1f}s infinite both"), 65 + ind
        for w, c in toks:
            l.r(x, 127 + i * 3, w, 1, c); x += w + 1
        lines.append(l)
    b.r(116, 136, 10, 10, "#d9573f"); b.r(116, 136, 10, 1, "#f08a6c"); b.r(117, 137, 8, 1, "#4a2a22")
    b.r(126, 138, 3, 1, "#d9573f"); b.r(128, 139, 1, 4, "#d9573f"); b.r(126, 143, 3, 1, "#d9573f")
    st1, st2 = new("animation:a 1.6s steps(1) infinite"), new("animation:a 1.6s steps(1) -.8s infinite", "alt")
    for s, o in ((st1, 0), (st2, 1)):
        for k in range(7):
            s.r(119 + (k + o) % 2, 126 + k, 1, 1, "#c9c3dc"); s.r(123 - (k + o) % 2, 128 + k, 1, 1, "#c9c3dc")
    b.r(22, 137, 14, 9, "#b5673f"); b.r(21, 136, 16, 2, "#d08a4a")
    for x, y, w, h in ((28, 118, 2, 18), (22, 122, 6, 3), (30, 120, 6, 3), (20, 128, 8, 3), (30, 127, 8, 3), (26, 115, 5, 4)):
        b.r(x, y, w, h, "#3f7d63"); b.r(x, y, w, 1, "#62a883")

    # cat in the moonlight
    for l in (*stars, *wins, red):
        l.sprite(316, LEDGE - 22, CAT, dict.fromkeys("#g", (0, 0, 0, 0)), 2)
    cat = new(); cat.sprite(316, LEDGE - 22, CAT, CAT_PAL, 2)
    for sx in (328, 336, 344):
        cat.r(sx, LEDGE - 14, 4, 6, "#9b5b3c")
    t1, t2 = new("animation:a 2.4s steps(1) infinite"), new("animation:a 2.4s steps(1) -1.2s infinite", "alt")
    for x, y in ((316, -4), (313, -6), (311, -8), (310, -11), (309, -14)):
        t1.r(x, LEDGE + y, 4, 3, "#d9803f")
    for x, y in ((316, -3), (312, -3), (308, -3), (305, -5), (303, -7)):
        t2.r(x, LEDGE + y, 4, 3, "#d9803f")

    # name
    n = new()
    for k, ch in enumerate("VINH"):
        n.sprite(27 + k * 40, 27, BIG[ch], {"#": "#4b3f86"}, 6)
        n.sprite(24 + k * 40, 24, BIG[ch], {"#": CREAM}, 6)
    big_text(n, 25, 79, "Backend + AI", "#070b1f"); big_text(n, 24, 78, "Backend + AI", GOLD)

    shoot = new("animation:sh 9s linear 2s infinite both", "alt")
    for k in range(14):
        shoot.r(236 + k, 12 + k // 2, 1, 1, ("#4a5c94", "#9fb4e8", CREAM)[k // 5])
    save("header.svg", W, H, 2, [b, *stars, *wins, red, shoot, n, *lines, st1, st2, cat, t1, t2],
         "Pixel art rooftop at night: the name VINH in a starry sky, a full moon, city lights, a laptop and a cat",
         "@keyframes sh{0%{transform:none;opacity:0}1%,5%{opacity:1}9%,100%{transform:translate(70px,35px);opacity:0}}")


def divider():
    W, H = 424, 12
    rnd = random.Random(7)
    b = Layer(W, H)
    b.r(2, 0, W - 4, H, SKY[1]); b.r(0, 2, W, H - 4, SKY[1]); b.r(1, 1, W - 2, H - 2, SKY[1])
    tw = [Layer(W, H, f"animation:tw {t}s steps(4) -{t / 3:.1f}s infinite") for t in (3, 4.5, 6)]
    for i in range(60):
        tw[i % 3].r(rnd.randrange(4, W - 4), rnd.randrange(2, H - 2), 1, 1, rnd.choice((CREAM, "#9fb4e8", GOLD)))
    b.r(202, 0, 20, H, SKY[1])
    for l in tw:
        l.r(202, 0, 20, H, (0, 0, 0, 0))
    b.d.ellipse((207, 1, 216, 10), fill=CREAM); b.d.ellipse((210, 0, 218, 8), fill=SKY[1])
    for i, x in enumerate((194, 227)):
        tw[i].r(x, 5, 5, 1, GOLD); tw[i].r(x + 2, 3, 1, 5, GOLD)
    save("divider.svg", W, H, 2, [b, *tw], "Night sky divider")


ICONS = {
    "about": ["#........#", "##......##", "##########", "##########", "##g####g##", "##########", "####pp####", ".########."],
    "stack": ["ssssssssss", "sl.s.s.s.s", "ssssssssss", "..........", "ssssssssss", "sy.s.s.s.s", "ssssssssss", ".........."],
    "contrib": ["....yy....", "...yyyy...", "..dyyyyb..", "..dddbbb..", "..dddbbb..", "..dddbbb..", "...ddbb...", "....db...."],
}
PAL = {"#": "#d9803f", "g": "#15131c", "p": "#f2a5a0", "s": "#8d98b8", "l": "#6fd08c", "y": GOLD, "b": "#8fb0f0", "w": CREAM, "d": "#4f6cb8"}


def icons():
    for name, rows in ICONS.items():
        b = Layer(16, 16)
        b.r(1, 0, 14, 16, SKY[2]); b.r(0, 1, 16, 14, SKY[2])
        b.sprite(3, 4, rows, PAL)
        save(f"icon-{name}.svg", 16, 16, 2, [b], name)


if __name__ == "__main__":
    header(); divider(); icons()
