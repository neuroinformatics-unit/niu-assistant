---
name: niu-docs
description: Answer how-to questions from the public docs of the Neuroinformatics Unit and the tools it maintains. Use when someone asks how to log in to or run jobs on the SWC HPC cluster (SSH, SLURM, GPUs, VS Code, port forwarding, SLEAP on the cluster), mount ceph on Ubuntu, keep a cookiecutter project up to date, choose a software licence, share data or use GIN, get started with extracellular electrophysiology, or install and use movement, BrainGlobe (atlases, brainreg, cellfinder, brainrender) or photon-mosaic.
allowed-tools: mcp__plugin_niu-assistant_niu__find_docs, mcp__plugin_niu-assistant_niu__read_doc
---

Answer from the docs before anything else.

1. Call `find_docs` with the question's key words.
2. Read the one or two pages that fit with `read_doc`.
3. Answer from what the pages say and give the link of each page you used. Give only commands, options and names that appear on the pages; if a page doesn't give one, say so instead of suggesting a likely-sounding one.
4. If no page covers the question, say so plainly, and point to the project's own docs site if the question is about one of these tools.
