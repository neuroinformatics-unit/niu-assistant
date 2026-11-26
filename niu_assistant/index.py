"""The pinned index of public docs pages, searched and read at their pins."""

from __future__ import annotations

import re
import tomllib
import urllib.request
from functools import cache
from pathlib import Path

INDEX = Path(__file__).with_name("index.toml")
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{root}/{path}"
LINK = "https://github.com/{repo}/blob/{ref}/{root}/{path}"
STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "for", "from", "how", "i", "in",
    "into", "is", "it", "my", "of", "on", "or", "the", "to", "what",
    "which", "with", "you",
}  # fmt: skip


@cache
def pages() -> dict[str, dict[str, str]]:
    """Every page by id ("<source>/<path>"), with its source's pin."""
    sources = tomllib.loads(INDEX.read_text(encoding="utf-8"))["source"]
    out = {}
    for source in sources:
        pin = {key: source[key] for key in ("repo", "ref", "root")}
        for page in source["page"]:
            out[f"{source['name']}/{page['path']}"] = {
                **page,
                **pin,
                "source": source["title"],
            }
    return out


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOPWORDS


def find_docs(query: str, limit: int = 5) -> list[dict[str, str]]:
    """Pages ranked by the words their title and summary share with the
    query, best first. An empty query lists every page."""
    wanted = _words(query)
    scored = []
    for page_id, page in pages().items():
        shared = len(wanted & _words(f"{page['title']} {page['summary']}"))
        if shared or not wanted:
            scored.append((shared, page_id, page))
    scored.sort(key=lambda hit: -hit[0])
    return [
        {
            "id": page_id,
            "source": page["source"],
            "title": page["title"],
            "summary": page["summary"],
            "link": LINK.format(**page),
        }
        for _, page_id, page in scored[: limit if wanted else None]
    ]


@cache
def read_doc(page_id: str) -> str:
    """The page's source text at its pin, with its link on top."""
    page = pages().get(page_id)
    if page is None:
        raise ValueError(f"No page {page_id!r}; use an id from find_docs.")
    with urllib.request.urlopen(RAW.format(**page), timeout=20) as response:
        text = response.read().decode("utf-8")
    return f"Source: {LINK.format(**page)}\n\n{text}"
