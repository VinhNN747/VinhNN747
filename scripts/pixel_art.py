#!/usr/bin/env python3
"""Draws the README pixel art as animated SVGs.  Usage: python3 scripts/pixel_art.py  (needs Pillow)"""
import random
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets"
# 3x5 pixel font, rows separated by "/"
GLYPHS = {
    "A": ".#./#.#/###/#.#/#.#", "B": "##./#.#/##./#.#/##.", "C": ".##/#../#../#../.##",
    "D": "##./#.#/#.#/#.#/##.", "E": "###/#../##./#../###", "F": "###/#../##./#../#..",
    "G": ".##/#../#.#/#.#/.##", "H": "#.#/#.#/###/#.#/#.#", "I": "###/.#./.#./.#./###",
    "J": "..#/..#/..#/#.#/.#.", "K": "#.#/#.#/##./#.#/#.#", "L": "#../#../#../#../###",
    "M": "#...#/##.##/#.#.#/#...#/#...#", "N": "##./#.#/#.#/#.#/#.#", "O": ".#./#.#/#.#/#.#/.#.",
    "P": "##./#.#/##./#../#..", "Q": ".#./#.#/#.#/.##/..#", "R": "##./#.#/##./#.#/#.#",
    "S": ".##/#../.#./..#/##.", "T": "###/.#./.#./.#./.#.", "U": "#.#/#.#/#.#/#.#/###",
    "V": "#.#/#.#/#.#/#.#/.#.", "X": "#.#/#.#/.#./#.#/#.#", "Y": "#.#/#.#/.#./.#./.#.",
    "W": "#...#/#...#/#.#.#/##.##/#...#", "Z": "###/..#/.#./#../###",
    "0": "###/#.#/#.#/#.#/###", "1": ".#./##./.#./.#./###", "2": "##./..#/.#./#../###",
    "3": "##./..#/.#./..#/##.", "4": "#.#/#.#/###/..#/..#", "5": "###/#../##./..#/##.",
    "6": ".##/#../###/#.#/###", "7": "###/..#/.#./.#./.#.", "8": "###/#.#/###/#.#/###",
    "9": "###/#.#/###/..#/##.", "%": "#.#/..#/.#./#../#.#", "#": ".#.#./#####/.#.#./#####/.#.#.",
    ".": "././././#", "-": ".../.../###/.../...", "/": "..#/..#/.#./#../#..", "<": "..#/.#./#../.#./..#",
    "'": "#/#/././.", "?": "##./..#/.#./.../.#.",
    "+": ".../.#./###/.#./...", " ": "./././././",
}


def text_width(t):
    return sum(len(GLYPHS.get(c, GLYPHS["?"]).split("/")[0]) + 1 for c in t.upper()) - 1

CSS = """
.p{shape-rendering:crispEdges}
@keyframes a{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}
@keyframes ty{0%{opacity:0}1%,90%{opacity:1}91%,100%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.alt{opacity:0}}
"""


class Layer:
    """A transparent pixel grid; `style` animates the whole layer."""

    def __init__(self, w, h, style="", cls=""):
        self.im = Image.new("RGBA", (w, h))
        self.d = ImageDraw.Draw(self.im)
        self.style, self.cls = style, cls

    def r(self, x, y, w, h, c):
        self.d.rectangle((x, y, x + w - 1, y + h - 1), fill=c)

    def sprite(self, x, y, rows, pal, s=1):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in pal:
                    self.r(x + i * s, y + j * s, s, s, pal[ch])

    def text(self, x, y, t, c):
        for ch in t.upper():
            rows = GLYPHS.get(ch, GLYPHS["?"]).split("/")
            self.sprite(x, y, rows, {"#": c})
            x += len(rows[0]) + 1

    def svg(self):
        px, (w, h), paths = self.im.load(), self.im.size, {}
        for y in range(h):
            x = 0
            while x < w:
                c, x0 = px[x, y], x
                while x < w and px[x, y] == c:
                    x += 1
                if c[3]:
                    paths.setdefault("#%02x%02x%02x" % c[:3], []).append(
                        f"M{x0} {y}h{x - x0}v1h-{x - x0}z")
        body = "".join(f'<path fill="{c}" d="{"".join(p)}"/>' for c, p in paths.items())
        attrs = (f' class="{self.cls}"' if self.cls else "") + (f' style="{self.style}"' if self.style else "")
        return f"<g{attrs}>{body}</g>"


def save(name, w, h, scale, layers, title):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w*scale}" height="{h*scale}" '
        f'role="img" aria-label="{title}"><title>{title}</title><style>{CSS}</style>'
        f'<g class="p">{"".join(l.svg() for l in layers)}</g></svg>\n')


BIG = {
    "V": ["#...#"] * 4 + [".#.#."] * 2 + ["..#.."],
    "I": ["#####"] + ["..#.."] * 5 + ["#####"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "H": ["#...#"] * 3 + ["#####"] + ["#...#"] * 3,
}
CAT = [
    "...............#...#",
    "...............##.##",
    "...............#####",
    "...............#g#g#",
    "......#######..#####",
    "....##########.####.",
    "...################.",
    "...################.",
    "..################..",
    "..################..",
    "..###..........###..",
]
CAT_PAL = {"#": "#d9803f", "g": "#15131c"}
WALK = [[
    "#..................#...#",
    "##.................##.##",
    ".##................#####",
    "..##...............#g#g#",
    "...##..#################",
    "....###################.",
    ".....################...",
    ".....################...",
    ".....################...",
], ["....##.##......##.##....", "...##...##....##...##...", "...#.....#....#.....#..."],
   [".....####......####.....", "......###.......###.....", "......#.#.......#.#....."]]


def banner():
    rnd = random.Random(747)
    W, H = 212, 84
    new = lambda style="", cls="": Layer(W, H, style, cls)
    b = new()
    b.r(0, 0, W, H, "#33232f")                                  # wall
    for y in range(2, 66, 8):
        for x in range((y // 8 % 2) * 8, W, 16):
            b.r(x, y, 7, 1, "#3c2a37")
    # window + dusk sky
    b.r(4, 4, 126, 58, "#1d141b"); b.r(5, 5, 124, 56, "#8a5138")
    sky = ["#0f2a3d", "#143648", "#1b4759", "#2b6a74", "#5b968a", "#b9bd8e", "#f0c987"]
    edges = [7, 23, 32, 39, 45, 50, 54, 60]
    for c, y0, y1 in zip(sky, edges, edges[1:]):
        b.r(7, y0, 120, y1 - y0, c)
        if y0 > 7:                                               # dithered band edge
            for x in range(7 + y0 % 2, 127, 2):
                b.r(x, y0 - 1, 1, 1, c)
    b.d.ellipse((104, 11, 116, 23), fill="#f7e8c3")
    b.r(107, 14, 3, 2, "#dcc9a0"); b.r(112, 18, 2, 2, "#dcc9a0"); b.r(108, 19, 1, 1, "#dcc9a0")
    stars = [new(f"animation:tw {t}s steps(4) -{t/3:.1f}s infinite") for t in (3, 4.5, 6)]
    for i in range(30):
        x, y = rnd.randrange(9, 100), rnd.randrange(8, 38)
        stars[i % 3].r(x, y, 1, 1, "#f7e8c3")
    # skyline
    wins = [new(f"animation:a {t}s steps(1) -{t/2}s infinite") for t in (7, 11)]
    for col, lo, hi in (("#1f5060", 6, 13), ("#12303f", 3, 9)):
        x = 7
        while x < 127:
            w = min(rnd.randrange(6, 12), 127 - x); h = rnd.randrange(lo, hi)
            b.r(x, 60 - h, w, h, col)
            if col == "#12303f":
                for wy in range(62 - h, 59, 2):
                    for wx in range(x + 1, x + w - 1, 2):
                        q = rnd.random()
                        if q < .25: b.r(wx, wy, 1, 1, "#f0c987")
                        elif q < .45: wins[q > .35].r(wx, wy, 1, 1, "#f0c987")
            x += w
    b.r(80, 37, 1, 13, "#1f5060")
    red = new("animation:a 2s steps(1) infinite"); red.r(80, 36, 1, 1, "#ff6b57")
    # name
    n = new()
    for k, ch in enumerate("VINH"):
        n.sprite(15 + k * 19, 12, BIG[ch], {"#": "#0a1b28"}, 3)
        n.sprite(14 + k * 19, 11, BIG[ch], {"#": "#f7e8c3"}, 3)
    n.text(16, 36, "backend + ai", "#0a1b28"); n.text(15, 35, "backend + ai", "#f7e8c3")
    # bookshelf
    b.r(134, 22, 34, 2, "#8a5138"); b.r(134, 24, 34, 1, "#1d141b")
    x = 136
    for w, h, c in [(3, 11, "#d9573f"), (3, 13, "#5b968a"), (2, 10, "#f0c987"), (4, 12, "#2b6a74"),
                    (3, 9, "#c98a5a"), (2, 13, "#f7e8c3")]:
        b.r(x, 22 - h, w, h, c); b.r(x, 22 - h + 2, w, 1, "#33232f"); x += w
    b.r(158, 18, 7, 4, "#c05a3c"); b.r(161, 12, 1, 6, "#6fa05c")
    for px, py in [(158, 14), (159, 12), (163, 12), (164, 14), (160, 11), (162, 10)]:
        b.r(px, py, 2, 2, "#6fa05c")
    # desk
    b.r(0, 68, W, 2, "#c98a5a"); b.r(0, 70, W, 6, "#9b5b3c"); b.r(0, 76, W, 1, "#6d3d2c"); b.r(0, 77, W, 7, "#57302a")
    for i in range(26):
        b.r(rnd.randrange(0, 200), rnd.randrange(71, 76), rnd.randrange(4, 12), 1, "#8a4f36")
    # monitor
    b.r(133, 32, 38, 28, "#1d141b"); b.r(134, 33, 36, 26, "#d8cbb0"); b.r(136, 35, 32, 20, "#0d1f22")
    b.r(165, 57, 2, 1, "#6fd08c"); b.r(149, 60, 6, 6, "#a89a80"); b.r(144, 66, 16, 2, "#d8cbb0")
    code = [(0, [(6, "#ff8f6b"), (9, "#f7e8c3")]), (2, [(5, "#8fd3c1"), (12, "#f0c987")]),
            (4, [(8, "#f7e8c3"), (5, "#8fd3c1")]), (4, [(4, "#ff8f6b"), (10, "#f0c987")]),
            (2, [(9, "#8fd3c1")]), (0, [(3, "#f7e8c3")])]
    lines = []
    for i, (ind, toks) in enumerate(code):
        l = new(f"animation:ty 12s steps(1) {i*1.2:.1f}s infinite both"); x = 138 + ind
        for w, c in toks:
            l.r(x, 37 + i * 3, w, 1, c); x += w + 1
        lines.append(l)
    # keyboard, mug
    b.r(136, 70, 30, 4, "#d8cbb0")
    for x in range(137, 165, 2): b.r(x, 71, 1, 1, "#7d705c"); b.r(x, 72, 1, 1, "#7d705c")
    b.r(114, 60, 9, 8, "#d9573f"); b.r(114, 60, 9, 1, "#4a2a22"); b.r(123, 62, 2, 1, "#d9573f")
    b.r(125, 62, 1, 4, "#d9573f"); b.r(123, 65, 2, 1, "#d9573f")
    st1, st2 = new("animation:a 1.6s steps(1) infinite"), new("animation:a 1.6s steps(1) -.8s infinite", "alt")
    for s, o in ((st1, 0), (st2, 1)):
        for k in range(6): s.r(117 + (k + o) % 2, 53 + k, 1, 1, "#e9dcc4")
    # server rack
    b.r(175, 10, 33, 58, "#1d141b"); b.r(176, 11, 31, 56, "#4b5566")
    leds = [new(f"animation:a {t}s steps(1) -{o}s infinite") for t, o in ((.7, 0), (1.1, .4), (1.9, .9))]
    for i in range(6):
        y = 13 + i * 9
        b.r(178, y, 27, 7, "#20262f"); b.r(178, y, 27, 1, "#6b7688")
        for x in range(189, 203, 2): b.r(x, y + 2, 1, 4, "#39424f")
        for k in range(3):
            b.r(180 + k * 3, y + 3, 1, 2, "#39424f")
            leds[(i + k) % 3].r(180 + k * 3, y + 3, 1, 2, ("#6fd08c", "#f0c987", "#6fd08c")[k])
    # cat on the desk
    c = new(); c.sprite(22, 57, CAT, CAT_PAL)
    for sx in (28, 32, 36): c.r(sx, 61, 2, 3, "#9b5b3c")
    t1, t2 = new("animation:a 2.4s steps(1) infinite"), new("animation:a 2.4s steps(1) -1.2s infinite", "alt")
    for px, py in [(23, 66), (22, 66), (21, 65), (20, 64), (20, 63), (19, 62)]: t1.r(px, py, 2, 1, "#d9803f")
    for px, py in [(23, 67), (21, 67), (19, 67), (17, 66), (16, 65)]: t2.r(px, py, 3, 1, "#d9803f")
    save("banner.svg", W, H, 4, [b, *stars, *wins, red, n, *lines, st1, st2, *leds, c, t1, t2],
         "Vinh, backend and AI: pixel art desk at dusk with a cat, a monitor and a server rack")


# 12x12 icons, one per tool
P = {"k": "#15131c", "w": "#f7e8c3", "r": "#d9573f", "o": "#f0985a", "y": "#f0c987", "g": "#6fa05c",
     "G": "#a3cf7f", "b": "#4f86b8", "B": "#8fbfe0", "t": "#4fa896", "n": "#9b5b3c", "s": "#8d98a8"}
ICONS = [
    ("Java", ["....w..w....", "...w..w.....", "....w..w....", "............", ".rrrrrrrr...", ".rnnnnnnrrr.",
              ".rrrrrrrr.r.", ".rrrrrrrr.r.", ".rrrrrrrrrr.", "..rrrrrr....", "............", "wwwwwwwwww.."]),
    ("Spring", ["..........G.", "........GGG.", "....GGGGGGG.", "...GGGGGGgG.", "..GGGGGGgGG.", "..GGGGGgGGG.",
                "..GGGGgGGG..", "..GGGgGGGG..", "..GGgGGGG...", "...gGGG.....", "..g.........", ".g.........."]),
    ("Python", ["...bbbbb....", "..bbwbbbb...", "..bbbbbbb...", ".......bb...", "..bbbbbbb.y.", ".bbbbbbb.yy.",
                ".bbb.yyyyyy.", ".bb.yyyyyy..", "....yy......", "....yyyyyy..", "....yyyywy..", ".....yyyy..."]),
    ("FastAPI", ["....tttt....", "..tttttttt..", ".ttttttwttt.", ".tttttwwttt.", "tttttwwttttt", "ttttwwwwtttt",
                 "ttttttwwtttt", ".ttttwwtttt.", ".ttttwttttt.", "..tttttttt..", "....tttt....", "............"]),
    ("Postgres", ["............", "..bbbbbbbb..", ".bBBbbbbBBb.", "bBBBbbbbBBBb", "bBBBkbbkBBBb", ".bBBbbbbBBb.",
                  "..bbbbbbbb..", "...wbbbbw...", "....bbb.....", "....bbb.....", ".....bb.bb..", ".....bbbb..."]),
    ("MSSQL", ["...rrrrrr...", ".rrwwwwwwrr.", ".rrrrrrrrrr.", ".rrrrrrrrrr.", "............", ".rrrrrrrrrr.",
                    ".rrrrrrrwrr.", "............", ".rrrrrrrrrr.", ".rrrrrrrwrr.", "...rrrrrr...", "............"]),
    ("Docker", ["....yy......", "....yy......", "............", ".oo.yy.oo...", ".oo.yy.oo...", "..........b.",
                "bbbbbbbbbbbb", "bbbbbbbbbbb.", "bwbbbbbbbb..", ".bbbbbbbb...", "..bbbbbb....", "............"]),
    ("Git", ["..oo........", ".oooo.......", ".oooo...oo..", "..oo...oooo.", "..oo...oooo.", "..oo....oo..",
             "..oo...oo...", "..oooooo....", "..oo........", ".oooo.......", ".oooo.......", "..oo........"]),
    ("Linux", ["....ssss....", "...ssssss...", "...swssws...", "...ssooss...", "..sswwwwss..", "..swwwwwws..",
               ".sswwwwwwss.", ".sswwwwwwss.", "..swwwwwws..", "..sswwwwss..", ".ooo....ooo.", "............"]),
    ("Postman", ["............", "oooooooooooo", "owwwwwwwwwwo", "oowwwwwwwwoo", "owowwwwwwowo", "owwowwwwowwo",
                 "owwwoooowwwo", "owwwwwwwwwwo", "owwwwwwwwwwo", "oooooooooooo", "............", "............"]),
]


def inventory():
    cols, cw, ch, gap = 5, 40, 42, 2
    W = 212; H = 2 * ch + gap + 4
    b = Layer(W, H); b.r(0, 0, W, H, "#1d141b")
    layers = [b]
    for i, (name, rows) in enumerate(ICONS):
        x, y = 2 + i % cols * (cw + gap), 2 + i // cols * (ch + gap)
        b.r(x, y, cw, ch, "#8a5138"); b.r(x + 1, y + 1, cw - 2, ch - 2, "#33232f")
        b.r(x + 1, y + ch - 13, cw - 2, 12, "#12303f")
        for cx, cy in ((x, y), (x + cw - 1, y), (x, y + ch - 1), (x + cw - 1, y + ch - 1)):
            b.r(cx, cy, 1, 1, "#1d141b")
        b.sprite(x + 8, y + 3, rows, P, 2)
        b.text(x + (cw - text_width(name) + 1) // 2, y + ch - 9, name, "#f7e8c3")
    save("stack.svg", W, H, 4, layers, "Tech stack: " + ", ".join(n for n, _ in ICONS))


def footer():
    W, H = 212, 20
    b = Layer(W, H)
    b.r(0, 16, W, 1, "#c98a5a"); b.r(0, 17, W, 2, "#9b5b3c"); b.r(0, 19, W, 1, "#57302a")
    body, l1, l2 = Layer(W, H), Layer(W, H, "animation:a .5s steps(1) infinite"), \
        Layer(W, H, "animation:a .5s steps(1) -.25s infinite", "alt")
    coat = {"#": "#d9803f", "g": "#15131c"}
    body.sprite(0, 4, WALK[0], coat); l1.sprite(0, 13, WALK[1], coat); l2.sprite(0, 13, WALK[2], coat)
    for s in (7, 11, 15): body.r(s, 8, 2, 3, "#9b5b3c")
    inner = body.svg() + l1.svg() + l2.svg()
    OUT.joinpath("footer.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W*4}" height="{H*4}" role="img" '
        f'aria-label="A pixel cat walking"><title>A pixel cat walking</title><style>{CSS}'
        '@keyframes go{from{transform:translateX(-26px)}to{transform:translateX(214px)}}'
        '.cat{animation:go 24s steps(120) -8s infinite}</style>'
        f'<g class="p">{b.svg()}<g class="cat">{inner}</g></g></svg>\n')


if __name__ == "__main__":
    banner(); inventory(); footer()
