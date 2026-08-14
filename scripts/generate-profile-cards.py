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


def card_stats(user: dict, repos: list[dict], metrics: dict, theme: str) -> str:
    dark = theme == "dark"
    stage = "#08081a" if dark else "#f7f7ff"
    card = "#0a0d1f" if dark else "#ffffff"
    text_main = "#fef3c7" if dark else "#172033"
    text_muted = "#94a3b8"
    foil_stops = "#67e8f9;#f472b6;#fcd34d;#6ee7b7;#67e8f9"
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    activity = metrics.get("commits", 0) + metrics.get("pull_requests", 0) + metrics.get("issues", 0)
    rows = [
        ("⚡ Commits this year", metrics.get("commits", 0), "#fcd34d"),
        ("🌊 Contribution streak", f"{metrics.get('current_streak', 0)}d", "#a78bfa"),
        ("✦ Stars earned", stars, "#67e8f9"),
    ]
    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300" width="600" height="300" role="img" aria-labelledby="holo-title holo-desc">
      <title id="holo-title">GitHub Holographic Profile Stats</title><desc id="holo-desc">Live GitHub stats for {esc(USERNAME)}</desc>
      <defs>
        <linearGradient id="hfp-foil" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#67e8f9"><animate attributeName="stop-color" values="{foil_stops}" dur="10s" repeatCount="indefinite"/></stop><stop offset=".5" stop-color="#f472b6"><animate attributeName="stop-color" values="#f472b6;#fcd34d;#a78bfa;#67e8f9;#f472b6" dur="10s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="#fcd34d"><animate attributeName="stop-color" values="#fcd34d;#a78bfa;#67e8f9;#f472b6;#fcd34d" dur="10s" repeatCount="indefinite"/></stop></linearGradient>
        <linearGradient id="hfp-sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
        <pattern id="hfp-scales" x="0" y="0" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M0,11 Q5.5,3 11,11 Q16.5,19 22,11" fill="none" stroke="#fff" stroke-width=".3" opacity=".18"/></pattern>
        <clipPath id="hfp-clip"><rect x="60" y="40" width="480" height="220" rx="14"/></clipPath>
      </defs>
      <rect width="600" height="300" fill="{stage}"/><rect x="60" y="40" width="480" height="220" rx="14" fill="{card}"/>
      <g clip-path="url(#hfp-clip)"><rect x="60" y="40" width="480" height="220" fill="url(#hfp-foil)" opacity=".42"/><rect x="60" y="40" width="480" height="220" fill="url(#hfp-scales)"/><g transform="skewX(-22)"><rect x="-200" y="-20" width="100" height="350" fill="url(#hfp-sheen)"><animate attributeName="x" values="-200;700;-200" dur="5s" repeatCount="indefinite" keyTimes="0;.7;1"/></rect></g></g>
      <rect x="60" y="40" width="480" height="220" rx="14" fill="none" stroke="url(#hfp-foil)" stroke-width="1.5"/>
      <text x="86" y="92" font-family="Space Grotesk,system-ui,sans-serif" font-size="24" font-weight="800" fill="{text_main}">{esc(USERNAME.upper())}</text><text x="86" y="110" font-family="JetBrains Mono,monospace" font-size="8" fill="#fcd34d" letter-spacing="3">GITHUB PROFILE · LIVE STATS</text>
      <text x="514" y="92" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="8" fill="#fbbf24" letter-spacing="2">ACTIVITY</text><text x="514" y="116" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="21" font-weight="700" fill="{text_main}">{activity:,}</text><line x1="86" y1="124" x2="514" y2="124" stroke="url(#hfp-foil)" stroke-width=".6" opacity=".7"/>''']
    for index, (label, value, color) in enumerate(rows):
        y = 148 + index * 28
        out.append(f'<g transform="translate(86,{y})"><text font-family="Space Grotesk,system-ui,sans-serif" font-size="12" font-weight="600" fill="{text_main}">{esc(label)}</text><text x="428" font-family="JetBrains Mono,monospace" font-size="10" fill="{color}" text-anchor="end">{esc(value)}</text></g>')
    out.append(f'<line x1="86" y1="228" x2="514" y2="228" stroke="url(#hfp-foil)" stroke-width=".6" opacity=".7"/><text x="86" y="246" font-family="JetBrains Mono,monospace" font-size="7" fill="{text_muted}" letter-spacing="2">UPDATED BY GITHUB ACTIONS · {esc(USERNAME.upper())}</text><text x="514" y="246" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="7" fill="#fcd34d" letter-spacing="2">★★★★★ HOLO</text></svg>')
    return "".join(out)


def trophy_rank(score: int, category: str) -> str:
    thresholds = {
        "Stars": (1000, 100, 10),
        "Commit": (1000, 500, 100),
        "Followers": (1000, 100, 10),
        "Issues": (100, 50, 10),
        "Repositories": (100, 50, 10),
        "PullRequest": (100, 50, 10),
    }
    s, a, b = thresholds[category]
    return "S" if score >= s else "A" if score >= a else "B" if score >= b else "C"


def card_trophies(user: dict, repos: list[dict], metrics: dict, theme: str) -> str:
    width, height = 760, 270
    start, end = shell(width, height, "GitHub Trophies", "Real milestones, ranked by your strongest signals", theme)
    dark = theme == "dark"
    ink = "#e8edf7" if dark else "#172033"
    muted = "#93a4bf" if dark else "#64748b"
    panel = "#141d33" if dark else "#ffffff"
    border = "#26324b" if dark else "#dbe3ef"
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    trophies = [
        ("Stars", total_stars, "Stars"),
        ("Commit", metrics.get("commits", 0), "Commit"),
        ("Followers", user.get("followers", 0), "Followers"),
        ("Issues", metrics.get("issues", 0), "Issues"),
        ("Repositories", user.get("public_repos", 0), "Repositories"),
        ("PullRequest", metrics.get("pull_requests", 0), "PullRequest"),
    ]
    trophies = sorted((item for item in trophies if item[1] > 0), key=lambda item: item[1], reverse=True)[:6]
    out = [start]
    for index, (label, value, caption) in enumerate(trophies):
        x = 24 + index * 119
        y = 111
        card_width = 108
        accent = ["#f7c95d", "#62e6d3", "#8b7cf6", "#f7498b", "#f7b955", "#6ea8fe"][index]
        rank = trophy_rank(value, caption)
        out.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="116" rx="14" fill="{panel}" stroke="{border}" filter="url(#shadow)"/>')
        out.append(text(x + card_width / 2, y + 18, label, 10, muted, 750, "middle"))
        cup_x = x + 54
        cup_y = y + 27
        out.append(f'<path d="M{cup_x-18} {cup_y+3}H{cup_x-25}C{cup_x-25} {cup_y+14} {cup_x-19} {cup_y+19} {cup_x-12} {cup_y+19}M{cup_x+18} {cup_y+3}H{cup_x+25}C{cup_x+25} {cup_y+14} {cup_x+19} {cup_y+19} {cup_x+12} {cup_y+19}" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>')
        out.append(f'<path d="M{cup_x-18} {cup_y}H{cup_x+18}L{cup_x+13} {cup_y+20}C{cup_x+11} {cup_y+28} {cup_x+5} {cup_y+32} {cup_x} {cup_y+32}C{cup_x-5} {cup_y+32} {cup_x-11} {cup_y+28} {cup_x-13} {cup_y+20}Z" fill="{accent}" opacity=".92"/>')
        out.append(f'<path d="M{cup_x} {cup_y+32}V{cup_y+40}M{cup_x-9} {cup_y+43}H{cup_x+9}M{cup_x-13} {cup_y+47}H{cup_x+13}" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cup_x}" cy="{cup_y+14}" r="10" fill="{panel}" stroke="{accent}" stroke-width="2"/>')
        out.append(text(cup_x, cup_y + 19, rank, 12, ink, 800, "middle"))
        out.append(text(x + card_width / 2, y + 76, f"{value:,} pt", 16, ink, 800, "middle"))
        out.append(text(x + card_width / 2, y + 94, f"{rank} rank · {value:,} points", 8, muted, 700, "middle"))
        out.append(f'<rect x="{x+16}" y="{y+105}" width="{card_width-32}" height="3" rx="1.5" fill="{accent}"/>')
    if not trophies:
        out.append(text(48, 175, "No trophy points yet", 16, muted, 600))
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


def fetch_data() -> tuple[dict, list[dict], list[dict], dict]:
    user = github(f"/users/{urllib.parse.quote(USERNAME)}")
    repos = github(f"/users/{urllib.parse.quote(USERNAME)}/repos?per_page=100&sort=updated&type=owner")
    query = """
    query($login: String!) {
      user(login: $login) {
        repositoriesContributedTo(first: 10, includeUserRepositories: false, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, PULL_REQUEST_REVIEW]) {
          nodes { nameWithOwner stargazerCount }
        }
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          contributionCalendar {
            weeks {
              contributionDays { contributionCount date }
            }
          }
        }
      }
    }
    """
    metrics = {"commits": 0, "issues": 0, "pull_requests": 0, "weeks": [], "current_streak": 0, "longest_streak": 0}
    try:
        data = gql(query, {"login": USERNAME})["user"]
        contributed = data["repositoriesContributedTo"]["nodes"]
        collection = data["contributionsCollection"]
        metrics = {
            "commits": collection.get("totalCommitContributions", 0),
            "issues": collection.get("totalIssueContributions", 0),
            "pull_requests": collection.get("totalPullRequestContributions", 0),
        }
        weeks = collection.get("contributionCalendar", {}).get("weeks", [])
        days = [day for week in weeks for day in week.get("contributionDays", [])]
        metrics["weeks"] = weeks
        run = longest = 0
        for day in days:
            run = run + 1 if day.get("contributionCount", 0) > 0 else 0
            longest = max(longest, run)
        current = 0
        for day in reversed(days):
            if day.get("contributionCount", 0) == 0 and current == 0:
                continue
            if day.get("contributionCount", 0) == 0:
                break
            current += 1
        metrics["current_streak"] = current
        metrics["longest_streak"] = longest
    except Exception as error:
        print(f"warning: contribution query failed: {error}", file=sys.stderr)
        contributed = []
    return user, repos, contributed, metrics


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    user, repos, contributed, metrics = fetch_data()
    for theme in ("dark", "light"):
        (ASSETS / f"github-stats-{theme}.svg").write_text(card_stats(user, repos, metrics, theme), encoding="utf-8")
        (ASSETS / f"github-languages-{theme}.svg").write_text(card_languages(repos, theme), encoding="utf-8")
        (ASSETS / f"github-contributions-{theme}.svg").write_text(card_contributions(user, contributed, theme), encoding="utf-8")


if __name__ == "__main__":
    main()
