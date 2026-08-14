#!/usr/bin/env python3
"""Generate self-hosted GitHub profile SVG cards."""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USERNAME = os.environ.get("GITHUB_USERNAME", "HitDrama")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def github(path: str, method: str = "GET", body: dict | None = None) -> dict | list:
    url = "https://api.github.com" + path
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "HitDrama-profile-cards",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body else None,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def gql(query: str, variables: dict) -> dict:
    result = github("/graphql", "POST", {"query": query, "variables": variables})
    if result.get("errors"):
        raise RuntimeError(result["errors"][0].get("message", "GitHub GraphQL error"))
    return result["data"]


def esc(value: object) -> str:
    return escape(str(value), quote=True)


def text(x: int, y: int, value: object, size: int = 14, color: str = "#e8edf7", weight: int = 400, anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI, sans-serif" font-size="{size}px" font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'


def shell(width: int, height: int, title: str, subtitle: str, theme: str) -> tuple[str, str]:
    dark = theme == "dark"
    bg = "#0b1020" if dark else "#f8fafc"
    panel = "#11182b" if dark else "#ffffff"
    border = "#26324b" if dark else "#dbe3ef"
    primary = "#f7498b" if dark else "#d92d75"
    muted = "#93a4bf" if dark else "#64748b"
    accent = "#62e6d3" if dark else "#0891b2"
    defs = f'''<defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="{('#15112b' if dark else '#fff1f7')}"/></linearGradient>
      <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{primary}"/><stop offset="1" stop-color="{accent}"/></linearGradient>
      <filter id="shadow"><feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="{('#000000' if dark else '#94a3b8')}" flood-opacity=".16"/></filter>
    </defs>'''
    opening = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(subtitle)}</desc>{defs}<rect width="100%" height="100%" rx="18" fill="url(#bg)"/><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="17" fill="none" stroke="{border}"/><rect x="24" y="22" width="64" height="5" rx="2.5" fill="url(#line)"/>'
    header = text(24, 58, title, 21, primary, 750) + text(24, 82, subtitle, 12, muted, 500)
    return opening + header, f"</svg>"


def card_stats(user: dict, repos: list[dict], theme: str) -> str:
    width, height = 760, 270
    start, end = shell(width, height, "GitHub Stats", "A quiet snapshot of the work behind the profile", theme)
    dark = theme == "dark"
    panel = "#141d33" if dark else "#ffffff"
    border = "#26324b" if dark else "#dbe3ef"
    muted = "#93a4bf" if dark else "#64748b"
    primary = "#f7498b" if dark else "#d92d75"
    ink = "#e8edf7" if dark else "#172033"
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    total_forks = sum(repo.get("forks_count", 0) for repo in repos)
    values = [("Repositories", user.get("public_repos", 0)), ("Followers", user.get("followers", 0)), ("Stars earned", total_stars), ("Forks", total_forks)]
    out = [start]
    for index, (label, value) in enumerate(values):
        x = 24 + (index % 4) * 181
        y = 112
        out.append(f'<rect x="{x}" y="{y}" width="165" height="112" rx="14" fill="{panel}" stroke="{border}" filter="url(#shadow)"/>')
        out.append(text(x + 16, y + 28, label.upper(), 10, muted, 700))
        out.append(text(x + 16, y + 72, f"{value:,}", 28, ink, 750))
        out.append(f'<circle cx="{x+140}" cy="{y+24}" r="5" fill="{primary if index % 2 == 0 else "#62e6d3"}"/>')
    return "".join(out) + end


def card_trophies(user: dict, repos: list[dict], theme: str) -> str:
    width, height = 760, 270
    start, end = shell(width, height, "GitHub Trophies", "Small milestones from a growing open-source journey", theme)
    dark = theme == "dark"
    ink = "#e8edf7" if dark else "#172033"
    muted = "#93a4bf" if dark else "#64748b"
    panel = "#141d33" if dark else "#ffffff"
    border = "#26324b" if dark else "#dbe3ef"
    colors = ["#f7498b", "#62e6d3", "#8b7cf6", "#f7b955", "#6ea8fe"]
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    total_forks = sum(repo.get("forks_count", 0) for repo in repos)
    trophies = [
        ("PUBLIC BUILDER", user.get("public_repos", 0), "repositories"),
        ("COMMUNITY", user.get("followers", 0), "followers"),
        ("STAR COLLECTOR", total_stars, "stars earned"),
        ("OPEN SOURCE", total_forks, "forks"),
        ("EARLY EXPLORER", user.get("created_at", "")[:4] or "—", "joined GitHub"),
    ]
    out = [start]
    for index, (label, value, caption) in enumerate(trophies):
        x = 24 + index * 143
        y = 111
        out.append(f'<rect x="{x}" y="{y}" width="127" height="116" rx="14" fill="{panel}" stroke="{border}" filter="url(#shadow)"/>')
        out.append(f'<circle cx="{x+26}" cy="{y+27}" r="12" fill="{colors[index]}"/>')
        out.append(text(x + 26, y + 31, "✦", 13, "#ffffff", 750, "middle"))
        out.append(text(x + 14, y + 59, value, 24, ink, 750))
        out.append(text(x + 14, y + 79, label, 9, muted, 750))
        out.append(text(x + 14, y + 98, caption, 10, muted, 500))
    return "".join(out) + end


def card_languages(repos: list[dict], theme: str) -> str:
    counts: Counter[str] = Counter()
    for repo in repos:
        language = repo.get("language")
        if language:
            counts[language] += 1
    languages = counts.most_common(5)
    total = max(sum(counts.values()), 1)
    width, height = 760, 310
    start, end = shell(width, height, "Top Languages", "The languages shaping the public repositories", theme)
    dark = theme == "dark"
    ink = "#e8edf7" if dark else "#172033"
    muted = "#93a4bf" if dark else "#64748b"
    panel = "#141d33" if dark else "#ffffff"
    border = "#26324b" if dark else "#dbe3ef"
    colors = ["#f7498b", "#62e6d3", "#8b7cf6", "#f7b955", "#6ea8fe"]
    out = [start, f'<rect x="24" y="110" width="712" height="166" rx="14" fill="{panel}" stroke="{border}" filter="url(#shadow)"/>']
    if not languages:
        out.append(text(48, 175, "No public language data yet", 16, muted, 600))
    for index, (language, count) in enumerate(languages):
        y = 140 + index * 25
        pct = count / total
        out.append(f'<rect x="48" y="{y-10}" width="18" height="18" rx="5" fill="{colors[index]}"/>')
        out.append(text(78, y + 4, language, 14, ink, 650))
        out.append(text(690, y + 4, f"{pct*100:.0f}%", 13, muted, 650, "end"))
        out.append(f'<rect x="210" y="{y-4}" width="430" height="6" rx="3" fill="{border}"/><rect x="210" y="{y-4}" width="{430*pct:.1f}" height="6" rx="3" fill="{colors[index]}"/>')
    return "".join(out) + end


def card_contributions(user: dict, contributed: list[dict], theme: str) -> str:
    width, height = 760, 330
    start, end = shell(width, height, "Top Contributions", "Open-source places where your work has traveled", theme)
    dark = theme == "dark"
    ink = "#e8edf7" if dark else "#172033"
    muted = "#93a4bf" if dark else "#64748b"
    panel = "#141d33" if dark else "#ffffff"
    border = "#26324b" if dark else "#dbe3ef"
    primary = "#f7498b" if dark else "#d92d75"
    out = [start, f'<rect x="24" y="110" width="712" height="190" rx="14" fill="{panel}" stroke="{border}" filter="url(#shadow)"/>']
    for index, repo in enumerate(contributed[:4]):
        y = 145 + index * 38
        name = repo.get("nameWithOwner", "Unknown repository")
        stars = repo.get("stargazerCount", 0)
        out.append(f'<circle cx="52" cy="{y-4}" r="13" fill="{primary if index == 0 else border}"/>')
        out.append(text(52, y + 1, str(index + 1), 11, "#ffffff", 750, "middle"))
        out.append(text(80, y, name, 14, ink, 650))
        out.append(text(690, y, f"★ {stars:,}", 12, muted, 600, "end"))
        if index < min(len(contributed), 4) - 1:
            out.append(f'<path d="M80 {y+15}H690" stroke="{border}"/>')
    if not contributed:
        out.append(text(48, 175, "No contributed repositories found yet", 16, muted, 600))
    return "".join(out) + end


def fetch_data() -> tuple[dict, list[dict], list[dict]]:
    user = github(f"/users/{urllib.parse.quote(USERNAME)}")
    repos = github(f"/users/{urllib.parse.quote(USERNAME)}/repos?per_page=100&sort=updated&type=owner")
    query = """
    query($login: String!) { user(login: $login) { repositoriesContributedTo(first: 10, includeUserRepositories: false, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, PULL_REQUEST_REVIEW]) { nodes { nameWithOwner stargazerCount } } } }
    """
    try:
        contributed = gql(query, {"login": USERNAME})["user"]["repositoriesContributedTo"]["nodes"]
    except Exception as error:
        print(f"warning: contribution query failed: {error}", file=sys.stderr)
        contributed = []
    return user, repos, contributed


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    user, repos, contributed = fetch_data()
    for theme in ("dark", "light"):
        (ASSETS / f"github-trophies-{theme}.svg").write_text(card_trophies(user, repos, theme), encoding="utf-8")
        (ASSETS / f"github-stats-{theme}.svg").write_text(card_stats(user, repos, theme), encoding="utf-8")
        (ASSETS / f"github-languages-{theme}.svg").write_text(card_languages(repos, theme), encoding="utf-8")
        (ASSETS / f"github-contributions-{theme}.svg").write_text(card_contributions(user, contributed, theme), encoding="utf-8")


if __name__ == "__main__":
    main()
