#!/usr/bin/env python3
"""Draws assets/stats.svg from public GitHub data.

    GITHUB_TOKEN=... python3 scripts/stats.py <username>
    python3 scripts/stats.py --placeholder
"""
import json
import os
import sys
import urllib.request
from collections import Counter

from pixel_art import Layer, save, text_width

TOP = 6
QUERY = """query($login: String!, $after: String) {
  user(login: $login) {
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      pageInfo { hasNextPage endCursor }
      nodes { languages(first: 50) { edges { size node { name } } } }
    }
    contributionsCollection {
      commitContributionsByRepository(maxRepositories: 100) {
        contributions { totalCount }
        repository { isPrivate primaryLanguage { name } }
      }
    }
  }
}"""


def query(login, after):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        json.dumps({"query": QUERY, "variables": {"login": login, "after": after}}).encode(),
        {"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json",
         "User-Agent": "readme-stats"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if data.get("errors"):
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def fetch(login):
    sizes, commits, after = Counter(), Counter(), None
    while True:
        user = query(login, after)
        for repo in user["repositories"]["nodes"]:
            for e in repo["languages"]["edges"]:
                sizes[e["node"]["name"]] += e["size"]
        page = user["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        after = page["endCursor"]
    for c in user["contributionsCollection"]["commitContributionsByRepository"]:
        if not c["repository"]["isPrivate"]:
            lang = c["repository"]["primaryLanguage"]
            commits[lang["name"] if lang else "No code"] += c["contributions"]["totalCount"]
    return sizes, commits


def top(counter):
    rows = [r for r in counter.most_common() if r[1]]
    if len(rows) > TOP:
        rows = rows[:TOP - 1] + [("Other", sum(v for _, v in rows[TOP - 1:]))]
    return rows


def fit(label, width):
    while text_width(label) > width:
        label = label[:-1].rstrip()
    return label


def percent(v, total):
    return "<1%" if v / total < .005 else f"{v / total:.0%}"


def draw(sizes, commits, empty="No public data"):
    W, pw, rowh = 212, 103, 13
    panels = [
        ("Code by language", top(sizes), sum(sizes.values()), "#4fa896", percent),
        ("Commits by language", top(commits), sum(commits.values()), "#f0985a", lambda v, _: str(v)),
    ]
    H = 4 + 14 + max([1] + [len(p[1]) for p in panels]) * rowh + 3
    b = Layer(W, H); b.r(0, 0, W, H, "#1d141b")
    for i, (title, rows, total, color, fmt) in enumerate(panels):
        x = 2 + i * (pw + 2)
        b.r(x, 2, pw, H - 4, "#8a5138"); b.r(x + 1, 3, pw - 2, H - 6, "#33232f")
        b.r(x + 1, 3, pw - 2, 11, "#12303f")
        b.text(x + 4, 6, title, "#f7e8c3")
        if not rows:
            b.text(x + 4, 19, empty, "#b9a88f")
            continue
        peak, full = max(v for _, v in rows), pw - 8
        for k, (name, v) in enumerate(rows):
            y, val = 17 + k * rowh, fmt(v, total)
            b.text(x + pw - 4 - text_width(val), y, val, "#f7e8c3")
            b.text(x + 4, y, fit(name, full - text_width(val) - 4), "#f7e8c3")
            b.r(x + 4, y + 7, full, 3, "#241820")
            b.r(x + 4, y + 7, max(1, round(full * v / peak)), 3, color)
    alt = "; ".join(f"{t}: " + (", ".join(f"{n} {f(v, tot)}" for n, v in r) or empty)
                    for t, r, tot, _, f in panels)
    save("stats.svg", W, H, 4, [b], alt.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;"))


if __name__ == "__main__":
    if sys.argv[1:] == ["--placeholder"]:
        draw(Counter(), Counter(), "Loading...")
    elif len(sys.argv) == 2:
        sizes, commits = fetch(sys.argv[1])
        draw(sizes, commits)
    else:
        sys.exit(__doc__)
