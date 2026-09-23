"""Atualiza apenas a seção de projetos públicos do README do perfil."""

from datetime import datetime
from html import escape
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

OWNER = "AdrianoBuenoCruz"
PROJECTS = (
    ("gestao-agro", "Gestor Agro"),
    ("-Projeto-WEB-MOBILE-FIST", "Horta Municipal"),
    ("Projeto-Java-Biblioteca-Judiciario-Educacional-", "Biblioteca em Java"),
)
START = "<!-- projetos:auto:start -->"
END = "<!-- projetos:auto:end -->"


def latest_commit(repo):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/commits?per_page=1"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-updater",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=15) as response:
        commits = json.load(response)
    if not commits:
        raise RuntimeError(f"Sem commits públicos: {repo}")
    commit = commits[0]
    date = datetime.fromisoformat(
        commit["commit"]["committer"]["date"].replace("Z", "+00:00")
    )
    message = commit["commit"]["message"].splitlines()[0].strip()
    message = re.sub(r"[[]\\]", "", message)[:90]
    return date, f"- {date:%d/%m/%Y} · [{dict(PROJECTS)[repo]}]({commit['html_url']}) — {escape(message)}"


def main():
    readme_path = Path("README.md")
    readme = readme_path.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise RuntimeError("Marcadores da seção automática não encontrados.")

    entries = [latest_commit(repo) for repo, _ in PROJECTS]
    entries.sort(key=lambda item: item[0], reverse=True)
    section = "\n" + "\n".join(line for _, line in entries) + "\n"
    before, rest = readme.split(START, 1)
    _, after = rest.split(END, 1)
    updated = before + START + section + END + after
    if updated != readme:
        readme_path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
