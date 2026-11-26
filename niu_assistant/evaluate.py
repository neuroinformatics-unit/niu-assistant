"""niu-assistant-eval: ask the test questions through Claude Code with this
checkout as the plugin, score the answers, and save the run per model.

Each question in evals/questions.json lists the facts a good answer must
contain (any one of each group of alternatives). Every question is asked
REPEATS times, since answers vary between runs; it passes only if every
repeat does. The run is saved under evals/results/<model>-<effort>/<time>/
as results.json and report.md, and the report flags questions that passed
in the last run of the same model and effort and now fail on every repeat.

Usage: niu-assistant-eval --model sonnet [--effort medium] [--repeats 2]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QUESTIONS = REPO / "evals" / "questions.json"
RESULTS = REPO / "evals" / "results"
# The plugin's two tools as Claude Code names them, approved ahead of the run.
TOOLS = (
    "mcp__plugin_niu-assistant_niu__find_docs",
    "mcp__plugin_niu-assistant_niu__read_doc",
)


def load(path: Path = QUESTIONS) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def score(question: dict, answer: str) -> list[str]:
    """The facts the answer is missing; empty when it passes."""
    low = answer.lower()
    return [
        alternatives[0]
        for alternatives in question["facts"]
        if not any(a.lower() in low for a in alternatives)
    ]


def ask(question: str, model: str, effort: str) -> tuple[str, list[str]]:
    """One question through Claude Code with this checkout loaded as the
    plugin, in an empty folder with project settings only, so the runner's
    own settings stay out."""
    with tempfile.TemporaryDirectory() as empty:
        out = subprocess.run(
            [
                "claude",
                "-p",
                question,
                "--plugin-dir",
                str(REPO),
                "--setting-sources",
                "project",
                "--allowedTools",
                ",".join((*TOOLS, "Skill")),
                "--model",
                model,
                "--effort",
                effort,
                "--output-format",
                "stream-json",
                "--verbose",
            ],
            cwd=empty,
            capture_output=True,
            text=True,
            check=True,
            timeout=600,
        ).stdout
    events = [json.loads(line) for line in out.splitlines() if line.strip()]
    answer = next(
        (e.get("result", "") for e in events if e.get("type") == "result"),
        "",
    )
    pages = [
        block["input"].get("id", "")
        for e in events
        if e.get("type") == "assistant"
        for block in e["message"]["content"]
        if block.get("type") == "tool_use" and block.get("name") == TOOLS[1]
    ]
    return answer, pages


def run(questions: list[dict], model: str, effort: str, repeats: int):
    results = []
    for question in questions:
        start = time.time()
        tries = []
        for _ in range(repeats):
            answer, pages = ask(question["question"], model, effort)
            tries.append(
                {
                    "answer": answer,
                    "pages": pages,
                    "missing": score(question, answer),
                }
            )
        passes = sum(not t["missing"] for t in tries)
        results.append(
            {
                "id": question["id"],
                "question": question["question"],
                "passed": passes == repeats,
                "passes": passes,
                "seconds": round(time.time() - start, 1),
                "tries": tries,
            }
        )
    return results


def report(results: list[dict], previous: list[dict] | None, name: str):
    passed_before = {r["id"] for r in previous or [] if r["passed"]}
    worse = [
        r["id"]
        for r in results
        if r["passes"] == 0 and r["id"] in passed_before
    ]
    flaky = [
        f"{r['id']} ({r['passes']}/{len(r['tries'])})"
        for r in results
        if 0 < r["passes"] < len(r["tries"])
    ]
    total = sum(r["passed"] for r in results)
    out = [
        f"# {total}/{len(results)} passed ({name})",
        "",
        "Worse than last run: "
        + (", ".join(worse) or "none" if previous else "no earlier run"),
        "Passing on some repeats only: " + (", ".join(flaky) or "none"),
        "",
    ]
    for r in results:
        status = "pass" if r["passed"] else "FAIL"
        out += [
            f"## {r['id']}: {status} ({r['passes']}/{len(r['tries'])})",
            "",
            f"> {r['question']}",
            "",
        ]
        for t in r["tries"]:
            if t["missing"]:
                out.append(f"Missing: {', '.join(t['missing'])}")
            out += [
                "",
                t["answer"],
                "",
                f"Pages read: {', '.join(t['pages']) or 'none'}.",
                "",
            ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", required=True, help="e.g. sonnet, opus")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args(argv)

    name = f"{args.model}-{args.effort}"
    out = RESULTS / name
    earlier = sorted(out.glob("*/results.json"))
    previous = json.loads(earlier[-1].read_text()) if earlier else None
    results = run(load(), args.model, args.effort, args.repeats)
    folder = out / datetime.now(UTC).strftime("%Y-%m-%dT%H%M%S")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(json.dumps(results, indent=1))
    (folder / "report.md").write_text(report(results, previous, name))
    print((folder / "report.md").read_text().split("\n## ")[0])
    print(f"Full report: {folder / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
