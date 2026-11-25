#!/usr/bin/env python3
"""Refreshes the Overview section of README.md from GitHub data.

    GITHUB_TOKEN=... python3 scripts/stats.py <username>
"""
import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- overview:start -->", "<!-- overview:end -->"
TOP = 6
QUERY = """query($login: String!, $after: String) {
  user(login: $login) {
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      pageInfo { hasNextPage endCursor }
      nodes { languages(first: 50) { edges { size node { name } } } }
    }
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
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
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = {date.fromisoformat(d["date"]): d["contributionCount"] for w in weeks for d in w["contributionDays"]}
    return sizes, commits, days


def percent(v, total):
    return "<1%" if v / total < .005 else f"{v / total:.0%}"


def longest_streak(days):
    best = run = 0
    for d in sorted(days):
        run = run + 1 if days[d] else 0
        best = max(best, run)
    return best


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def table(*rows):
    head, *body = ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    return "\n".join([head, "|" + " :---: |" * len(rows[0]), *body])


def overview(sizes, commits, days):
    active, best_txt = sum(1 for v in days.values() if v), "-"
    if active:
        peak = max(days.values())
        best = max(d for d in days if days[d] == peak)           # latest, on a tie
        best_txt = f"{peak} on {best:%b} {best.day}"
    out = table(("Contributions this past year", "Active days", "Longest streak", "Best day"),
                (f"**{sum(days.values())}**", f"**{active}**", f"**{plural(longest_streak(days), 'day')}**",
                 f"**{best_txt}**"))
    code, made = sum(sizes.values()) or 1, sum(commits.values()) or 1
    names = sorted(set(sizes) | set(commits), key=lambda n: -max(sizes[n] / code, commits[n] / made))[:TOP]
    names.sort(key=lambda n: (-sizes[n], -commits[n], n))
    if names:
        out += "\n\n" + table(("Top languages", "Code", "Commits"),
                              *((n, percent(sizes[n], code) if sizes[n] else "-", commits[n] or "-") for n in names))
    return out


def update_readme(text):
    readme = README.read_text()
    head, rest = readme.split(START, 1)
    _, tail = rest.split(END, 1)
    README.write_text(f"{head}{START}\n\n{text}\n\n{END}{tail}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    update_readme(overview(*fetch(sys.argv[1])))
