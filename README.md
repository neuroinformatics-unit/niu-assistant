# niu-assistant

Answers how-to questions from the public docs of the Neuroinformatics Unit
and the tools it maintains: the NIU how-to guides (the SWC HPC cluster, SSH,
SLURM, SLEAP on the cluster, ceph, cookiecutter, licensing, data sharing, GIN,
electrophysiology), [movement](https://github.com/neuroinformatics-unit/movement),
[BrainGlobe](https://brainglobe.info) and
[photon-mosaic](https://github.com/photon-mosaic/photon-mosaic).

Nothing is copied. [`niu_assistant/index.toml`](niu_assistant/index.toml)
lists each page with a one-line summary and pins its source repository to a
release tag or commit; pages are read from GitHub at that pin when a
question needs them. Moving a pin is a deliberate commit, followed by a
benchmark run.

It comes in two forms: a Claude Code plugin (a skill plus two tools), and the
same two tools as an MCP server for any other MCP client.

## Claude Code

```bash
claude plugin marketplace add neuroinformatics-unit/niu-assistant
claude plugin install niu-assistant@niu
```

The plugin starts its server with [uv](https://docs.astral.sh/uv/), so `uvx`
must be on your path. Then ask a question, for example "how do I request a
GPU in a SLURM job?".

## Any other MCP client

The server speaks MCP over stdio. Add it to your client's MCP configuration:

```json
{
  "mcpServers": {
    "niu": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/neuroinformatics-unit/niu-assistant", "niu-assistant"]
    }
  }
}
```

It offers two tools: `find_docs` (pages matching a question, with links) and
`read_doc` (one page in full). The answers are only as good as the model
using them; the benchmark below measures this for Claude models.

## Benchmark

[`evals/questions.json`](evals/questions.json) holds ten questions, each with
the page that answers it and the facts a good answer must contain.

```bash
uv run --extra dev pytest
```

checks, without a model, that each question's page is in the top three
search results.

```bash
uv run niu-assistant-eval --model sonnet --effort medium
```

asks each question twice through Claude Code with this checkout as the
plugin and scores the answers. The scores go to `evals/results/scores.csv`,
one row per question per run, with the model ID that answered and the Claude
Code version; the answers go to
`evals/results/<model>-<effort>/<time>/results.json`. The printed summary
flags any question that passed in the previous run of the same model and
effort and now fails on every repeat, lists those that pass on some repeats
only, and says when the model ID has changed since that run. Commit the
results, so the next run has something to compare against. It runs on your
own Claude Code login.

## Adding a page

Add a `[[source.page]]` entry under its source in `index.toml`, with a
summary written after reading the page at the pinned version. For a new
source, add a `[[source]]` with its repository, its docs folder and a pin.
If the page answers a question worth tracking, add that question to
`evals/questions.json`. A new source or topic also goes into the four
descriptions that say what the assistant covers, or questions about it will
not reach the tools: the skill's `description` in `skills/niu-docs/SKILL.md`,
`INSTRUCTIONS` in `niu_assistant/server.py`, the `description` in
`.claude-plugin/plugin.json`, and the first paragraph of this README.
