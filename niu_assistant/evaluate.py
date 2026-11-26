"""niu-assistant-eval: ask the test questions through Claude Code with this
checkout as the plugin, score the answers, and save the run per model.

Each question in evals/questions.json lists the facts a good answer must
contain (any one of each group of alternatives). Every question is asked
REPEATS times, since answers vary between runs; it passes only if every
repeat does. The scores go to evals/results/scores.csv, one row per
question per run, with the model ID that answered and the Claude Code
version; that file is committed. The answers are saved locally under
evals/results/<model>-<effort>/<time>/results.json and are not
committed. The printed summary flags questions that passed in the last run
of the same model and effort and now fail on every repeat, and says when
the model ID differs from that run's.

Usage: niu-assistant-eval --model sonnet [--effort medium] [--repeats 2]
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QUESTIONS = REPO / "evals" / "questions.json"
RESULTS = REPO / "evals" / "results"
SCORES = RESULTS / "scores.csv"
COLUMNS = ("run", "model", "model_id", "claude_code", "effort", "question",
           "passes", "repeats", "seconds")  # fmt: skip
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


def ask(question: str, model: str, effort: str) -> tuple[str, list[str], str]:
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
    model_id = next(
        (
            e["message"]["model"]
            for e in events
            if e.get("type") == "assistant" and e["message"].get("model")
        ),
        "",
    )
    return answer, pages, model_id


def run(questions: list[dict], model: str, effort: str, repeats: int):
    results, model_ids = [], set()
    for question in questions:
        start = time.time()
        tries = []
        for _ in range(repeats):
            answer, pages, model_id = ask(question["question"], model, effort)
            model_ids.add(model_id)
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
    return results, ",".join(sorted(m for m in model_ids if m))


def previous_run(model: str, effort: str) -> list[dict]:
    """The rows of the last run of this model and effort in scores.csv."""
    if not SCORES.exists():
        return []
    with SCORES.open(newline="") as f:
        rows = [
            r for r in csv.DictReader(f)
            if r["model"] == model and r["effort"] == effort
        ]  # fmt: skip
    last = max((r["run"] for r in rows), default=None)
    return [r for r in rows if r["run"] == last]


def summary(results: list[dict], previous: list[dict], name: str, model_id):
    passed_before = {
        r["question"] for r in previous if r["passes"] == r["repeats"]
    }
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
        f"{total}/{len(results)} passed ({name}, {model_id})",
        "Worse than last run: "
        + (", ".join(worse) or "none" if previous else "no earlier run"),
        "Passing on some repeats only: " + (", ".join(flaky) or "none"),
    ]
    earlier_id = previous[0]["model_id"] if previous else ""
    if previous and earlier_id != model_id:
        out.append(
            f"Model changed since last run: {earlier_id or 'not recorded'}"
            f" -> {model_id}"
        )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", required=True, help="e.g. sonnet, opus")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args(argv)

    name = f"{args.model}-{args.effort}"
    previous = previous_run(args.model, args.effort)
    claude_code = subprocess.run(
        ["claude", "--version"], capture_output=True, text=True, check=True
    ).stdout.split()[0]
    results, model_id = run(load(), args.model, args.effort, args.repeats)
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%S")
    folder = RESULTS / name / stamp
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(json.dumps(results, indent=1))
    new = not SCORES.exists()
    with SCORES.open("a", newline="") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(COLUMNS)
        for r in results:
            writer.writerow(
                (stamp, args.model, model_id, claude_code, args.effort,
                 r["id"], r["passes"], len(r["tries"]), r["seconds"])
            )  # fmt: skip
    print(summary(results, previous, name, model_id))
    print(f"Answers: {folder / 'results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
