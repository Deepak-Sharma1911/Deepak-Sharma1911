import os
import requests
from collections import Counter
from datetime import datetime

USERNAME = "Deepak-Sharma1911"

TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

BASE_URL = "https://api.github.com"


def github_api(endpoint):
    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def get_repositories():
    repositories = []

    page = 1

    while True:
        data = github_api(
            f"/users/{USERNAME}/repos"
            f"?per_page=100&page={page}&type=owner"
        )

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def calculate_stats(repositories):
    total_stars = sum(repo["stargazers_count"] for repo in repositories)

    total_forks = sum(repo["forks_count"] for repo in repositories)

    total_repositories = len(repositories)

    return total_repositories, total_stars, total_forks


def get_languages(repositories):
    language_counter = Counter()

    for repo in repositories:
        if repo["fork"]:
            continue

        try:
            languages = github_api(
                f"/repos/{USERNAME}/{repo['name']}/languages"
            )

            for language, bytes_count in languages.items():
                language_counter[language] += bytes_count

        except requests.RequestException:
            continue

    return language_counter


def generate_stats_svg(repositories):
    total_repositories, total_stars, total_forks = calculate_stats(
        repositories
    )

    username = escape_xml(USERNAME)

    generated_at = datetime.utcnow().strftime("%Y-%m-%d")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="495"
height="210"
viewBox="0 0 495 210">

<rect width="495" height="210" rx="12"
fill="#1a1b27"/>

<text x="30" y="40"
font-family="Arial, sans-serif"
font-size="20"
font-weight="600"
fill="#ffffff">
GitHub Stats
</text>

<text x="30" y="62"
font-family="Arial, sans-serif"
font-size="12"
fill="#8B5CF6">
{username}
</text>

<text x="45" y="105"
font-family="Arial, sans-serif"
font-size="24"
font-weight="700"
fill="#ffffff">
{total_repositories}
</text>

<text x="45" y="125"
font-family="Arial, sans-serif"
font-size="12"
fill="#a9b1d6">
Repositories
</text>

<text x="200" y="105"
font-family="Arial, sans-serif"
font-size="24"
font-weight="700"
fill="#ffffff">
{total_stars}
</text>

<text x="200" y="125"
font-family="Arial, sans-serif"
font-size="12"
fill="#a9b1d6">
Stars
</text>

<text x="350" y="105"
font-family="Arial, sans-serif"
font-size="24"
font-weight="700"
fill="#ffffff">
{total_forks}
</text>

<text x="350" y="125"
font-family="Arial, sans-serif"
font-size="12"
fill="#a9b1d6">
Forks
</text>

<line x1="30" y1="150" x2="465" y2="150"
stroke="#303347"/>

<text x="30" y="180"
font-family="Arial, sans-serif"
font-size="11"
fill="#565f89">
Updated {generated_at}
</text>

</svg>
"""

    os.makedirs("assets", exist_ok=True)

    with open("assets/github-stats.svg", "w", encoding="utf-8") as file:
        file.write(svg)


def generate_languages_svg(languages):
    top_languages = languages.most_common(6)

    total = sum(value for _, value in top_languages)

    width = 420
    height = 240

    rows = []

    y = 85

    for language, value in top_languages:
        percentage = (value / total * 100) if total else 0

        rows.append(
            f"""
            <text x="30" y="{y}"
            font-family="Arial, sans-serif"
            font-size="13"
            fill="#ffffff">
            {escape_xml(language)}
            </text>

            <text x="365" y="{y}"
            font-family="Arial, sans-serif"
            font-size="12"
            text-anchor="end"
            fill="#a9b1d6">
            {percentage:.1f}%
            </text>

            <rect x="30" y="{y + 10}"
            width="350"
            height="6"
            rx="3"
            fill="#303347"/>

            <rect x="30" y="{y + 10}"
            width="{350 * percentage / 100}"
            height="6"
            rx="3"
            fill="#8B5CF6"/>
            """
        )

        y += 28

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<rect width="{width}" height="{height}" rx="12"
fill="#1a1b27"/>

<text x="30" y="40"
font-family="Arial, sans-serif"
font-size="20"
font-weight="600"
fill="#ffffff">
Top Languages
</text>

{''.join(rows)}

</svg>
"""

    os.makedirs("assets", exist_ok=True)

    with open("assets/top-languages.svg", "w", encoding="utf-8") as file:
        file.write(svg)


def main():
    repositories = get_repositories()

    generate_stats_svg(repositories)

    languages = get_languages(repositories)

    generate_languages_svg(languages)


if __name__ == "__main__":
    main()