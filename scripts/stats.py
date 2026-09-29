#!/usr/bin/env python3
"""Render the GitHub stats cards for the profile README as SVG files.

The data comes straight from the GitHub GraphQL API, so the README does not
depend on a third-party card service. Writes a light and a dark variant of
two cards: activity (contributions, streaks, repositories, stars) and the
most used languages of the public repositories.

Usage:
    GITHUB_TOKEN=... python3 scripts/stats.py --user andreaseirich --out output
    python3 scripts/stats.py --from-json data.json --out output   # offline render
"""

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from html import escape

API_URL = "https://api.github.com/graphql"

PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar { totalContributions }
    }
  }
}
"""

CALENDAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "title": "#0969da",
        "text": "#1f2328", "muted": "#59636e", "track": "#eaeef2",
    },
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "title": "#58a6ff",
        "text": "#e6edf3", "muted": "#8b949e", "track": "#21262d",
    },
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
WIDTH, HEIGHT = 400, 182
TOP_LANGUAGES = 6


def graphql(token, query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(API_URL, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "profile-stats-script",
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit(f"GitHub API answered {error.code}: {error.read().decode(errors='replace')}")
    if payload.get("errors"):
        sys.exit(f"GitHub API errors: {json.dumps(payload['errors'])}")
    return payload["data"]


def fetch(token, login):
    """Collect everything the cards need into one plain dict."""
    user = graphql(token, PROFILE_QUERY, {"login": login})["user"]
    if user is None:
        sys.exit(f"User {login!r} not found")

    now = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    days = {}
    # contributionsCollection accepts at most one year per request
    for year in range(start.year, now.year + 1):
        begin = max(start, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        end = min(now, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        data = graphql(token, CALENDAR_QUERY, {
            "login": login, "from": begin.isoformat(), "to": end.isoformat(),
        })
        weeks = data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        for week in weeks:
            for day in week["contributionDays"]:
                days[day["date"]] = day["contributionCount"]

    languages = {}
    colors = {}
    stars = 0
    repos = user["repositories"]
    for repo in repos["nodes"]:
        stars += repo["stargazerCount"]
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            languages[name] = languages.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or "#8b949e"

    return {
        "login": login,
        "generated": now.date().isoformat(),
        "last_year": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "days": days,
        "public_repos": repos["totalCount"],
        "stars": stars,
        "languages": languages,
        "colors": colors,
    }


def streaks(days):
    """Return (current, longest) streak in days from a {date: count} map."""
    if not days:
        return 0, 0
    dates = sorted(days)
    longest = run = 0
    for date in dates:
        run = run + 1 if days[date] > 0 else 0
        longest = max(longest, run)
    # a day without contributions yet does not break the streak until it is over
    index = len(dates) - 1
    if days[dates[index]] == 0:
        index -= 1
    current = 0
    while index >= 0 and days[dates[index]] > 0:
        current += 1
        index -= 1
    return current, longest


def card(theme, title, body, note=""):
    t = THEMES[theme]
    note_svg = (
        f'<text x="{WIDTH - 20}" y="32" text-anchor="end" font-size="10" fill="{t["muted"]}">'
        f"{escape(note)}</text>" if note else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(title)}">'
        f'<g font-family="{FONT}">'
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6" '
        f'fill="{t["bg"]}" stroke="{t["border"]}"/>'
        f'<text x="20" y="32" font-size="16" font-weight="600" fill="{t["title"]}">{escape(title)}</text>'
        f"{note_svg}{body}</g></svg>\n"
    )


def activity_card(stats, theme):
    t = THEMES[theme]
    current, longest = streaks(stats["days"])
    total = sum(stats["days"].values())
    items = [
        ("Contributions, last 12 months", f'{stats["last_year"]:,}'),
        ("Total contributions", f"{total:,}"),
        ("Current streak", f'{current} day{"" if current == 1 else "s"}'),
        ("Longest streak", f'{longest} day{"" if longest == 1 else "s"}'),
        ("Public repositories", f'{stats["public_repos"]:,}'),
        ("Stars earned", f'{stats["stars"]:,}'),
    ]
    body = []
    for i, (label, value) in enumerate(items):
        x = 20 + (i % 2) * 190
        y = 62 + (i // 2) * 42
        body.append(
            f'<text x="{x}" y="{y}" font-size="11" fill="{t["muted"]}">{escape(label)}</text>'
            f'<text x="{x}" y="{y + 20}" font-size="18" font-weight="600" fill="{t["text"]}">{escape(value)}</text>'
        )
    return card(theme, "GitHub Activity", "".join(body), note=f'updated {stats["generated"]}')


def languages_card(stats, theme):
    t = THEMES[theme]
    total = sum(stats["languages"].values())
    ranked = sorted(stats["languages"].items(), key=lambda item: item[1], reverse=True)
    # languages under 1 % would only show up as "0.x %" noise; they go into "Other"
    shown = [(name, size) for name, size in ranked[:TOP_LANGUAGES] if size >= total * 0.01]
    rest = total - sum(size for _, size in shown)
    entries = [(name, size, stats["colors"][name]) for name, size in shown]
    if total and rest >= total * 0.001:
        entries.append(("Other", rest, t["muted"]))

    bar_x, bar_y, bar_w, bar_h = 20, 50, WIDTH - 40, 10
    body = [
        f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5"/></clipPath>',
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5" fill="{t["track"]}"/>',
        '<g clip-path="url(#bar)">',
    ]
    offset = bar_x
    for name, size, color in entries:
        width = bar_w * size / total if total else 0
        body.append(f'<rect x="{offset:.2f}" y="{bar_y}" width="{width:.2f}" height="{bar_h}" fill="{color}"/>')
        offset += width
    body.append("</g>")

    for i, (name, size, color) in enumerate(entries):
        x = 20 + (i % 2) * 190
        y = 88 + (i // 2) * 24
        share = 100 * size / total if total else 0
        body.append(
            f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{color}"/>'
            f'<text x="{x + 16}" y="{y}" font-size="12" fill="{t["text"]}">{escape(name)} '
            f'<tspan fill="{t["muted"]}">{share:.1f}%</tspan></text>'
        )
    if not entries:
        body.append(f'<text x="20" y="92" font-size="12" fill="{t["muted"]}">No public code yet</text>')
    return card(theme, "Most Used Languages", "".join(body))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER"))
    parser.add_argument("--out", default="output")
    parser.add_argument("--from-json", help="render from saved data instead of calling the API")
    parser.add_argument("--save-json", help="also write the fetched data to this file")
    args = parser.parse_args()

    if args.from_json:
        with open(args.from_json) as handle:
            stats = json.load(handle)
    else:
        token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token or not args.user:
            sys.exit("Set GITHUB_TOKEN (or STATS_TOKEN) and --user")
        stats = fetch(token, args.user)
        if args.save_json:
            with open(args.save_json, "w") as handle:
                json.dump(stats, handle, indent=2, sort_keys=True)

    os.makedirs(args.out, exist_ok=True)
    for theme in THEMES:
        for name, render in (("activity", activity_card), ("languages", languages_card)):
            path = os.path.join(args.out, f"{name}-{theme}.svg")
            with open(path, "w") as handle:
                handle.write(render(stats, theme))
            print(f"wrote {path}")


if __name__ == "__main__":
    main()
