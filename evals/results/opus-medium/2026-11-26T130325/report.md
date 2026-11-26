# 10/10 passed (opus-medium)

Worse than last run: no earlier run
Passing on some repeats only: none

## ssh-cluster: pass (2/2)

> How do I connect to the SWC HPC cluster from my laptop?


## Connecting to the SWC HPC cluster

**Prerequisites:** an SWC account (username + password), basic command-line familiarity, and an SSH client. macOS/Linux have one pre-installed. On Windows, the guide recommends installing [Git Bash](https://gitforwindows.org/) so you can follow all the commands as written (Windows 10+ `cmd`/PowerShell also works for the login and config parts, but not the `ssh-copy-id` key step).

**From outside the SWC network** (home, eduroam, anywhere not wired-at-SWC and not on the VPN) you go through the *bastion* node first, then the *gateway* node:

```console
$ ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
<SWC-USERNAME>@sgw2:~$ ssh hpc-gw2
<SWC-USERNAME>@hpc-gw2:~$
```

**If you're at SWC on a wired connection or on the SWC VPN**, you can go straight to the gateway:

```console
$ ssh <SWC-USERNAME>@hpc-gw2.hpc.swc.ucl.ac.uk
```

Your password won't be echoed as you type. `exit` undoes the last `ssh` hop.

### Make it one command

Add this to `~/.ssh/config` on your laptop (create the file with `nano config` in `~/.ssh` if needed) — this is the from-outside version:

```bash
# Specify our intermediate jump host, aka the bastion node
Host swc-bastion
    HostName ssh.swc.ucl.ac.uk
    User <SWC-USERNAME>

# Specify how to get to the gateway node by jumping through the bastion node
Host swc-gateway
    HostName hpc-gw2
    User <SWC-USERNAME>
    ProxyJump swc-bastion
```

Then `ssh swc-gateway` gets you to the gateway in one step.

### Skip the password

```console
$ ssh-keygen -t ed25519
$ ssh-copy-id -i ~/.ssh/id_ed25519.pub swc-gateway
```

Since your SWC home directory is shared across all HPC nodes, the key works on all of them. Never share the private key (`id_ed25519`).

### Once you're on

The gateway is a staging area only — filesystem navigation, editing scripts, and job submission. Don't compute on it; request a compute node via SLURM, e.g. `srun -p cpu -n 4 --mem 8G --pty bash -i` for an interactive session.

Source: [Set up SSH for the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SSH-SWC-cluster.md)

Pages read: niu-howto/programming/SSH-SWC-cluster.md.


## Connecting to the SWC HPC cluster

**Prerequisites:** an SWC account (username + password), an SSH client (pre-installed on Linux/macOS; on Windows the guide recommends installing [Git Bash](https://gitforwindows.org/)).

**If you're on the SWC wired network or SWC VPN** — connect straight to the *gateway* node:

```console
$ ssh <SWC-USERNAME>@hpc-gw2.hpc.swc.ucl.ac.uk
```

**From anywhere else (home, eduroam)** — go through the *bastion* node first:

```console
$ ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
<SWC-USERNAME>@sgw2:~$ ssh hpc-gw2
```

Your password won't be echoed as you type. `exit` undoes the last `ssh` hop.

### Make it one command

Add this to `~/.ssh/config` on your laptop (for connecting from outside the network):

```bash
Host swc-bastion
    HostName ssh.swc.ucl.ac.uk
    User <SWC-USERNAME>

Host swc-gateway
    HostName hpc-gw2
    User <SWC-USERNAME>
    ProxyJump swc-bastion
```

Then `ssh swc-gateway` gets you there in one step. To skip the password too, generate a key with `ssh-keygen -t ed25519` and copy it over with `ssh-copy-id -i ~/.ssh/id_ed25519.pub swc-gateway`.

### Once you're on the gateway

Use it only for navigating files, editing scripts, and submitting jobs — don't compute there, it's shared. Request a compute node instead, e.g.:

```console
$ srun -p cpu -n 4 --mem 8G --pty bash -i
```

Source: [Set up SSH for the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SSH-SWC-cluster.md)

Pages read: niu-howto/programming/SSH-SWC-cluster.md.

## slurm-gpu: pass (2/2)

> How do I ask for a GPU in a SLURM batch script?


Two directives are needed — the `gpu` partition **and** `--gres`:

```bash
#!/bin/bash

#SBATCH -J my_job            # job name
#SBATCH -p gpu               # partition (queue)
#SBATCH -N 1                 # number of nodes
#SBATCH --mem 16G            # memory pool for all cores
#SBATCH -n 4                 # number of cores
#SBATCH -t 0-06:00           # time (D-HH:MM)
#SBATCH --gres gpu:1         # request 1 GPU (of any kind)
#SBATCH -o slurm.%x.%N.%j.out
#SBATCH -e slurm.%x.%N.%j.err
```

Key point from the docs: **no GPU is allocated unless you specify `--gres`, even if you're on the `gpu` partition.**

- Any GPU: `--gres gpu:1`
- A specific type: include its name, e.g. `--gres gpu:rtx2080:1`. Other example values given: `gpu:rtx5000:1`, `gpu:a100_2g.10gb:1`

Available GPU types are listed on the SWC internal wiki (linked from the page); `sinfo` on the cluster shows the partitions, their nodes and time limits.

Source: [SLURM arguments primer](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SLURM-arguments.md)

Pages read: niu-howto/programming/SLURM-arguments.md.


Two directives, and you need both:

```bash
#SBATCH -p gpu          # the gpu partition
#SBATCH --gres gpu:1    # request 1 GPU (of any kind)
```

The key gotcha the docs call out: **no GPU is allocated unless you specify `--gres`, even if you're on the `gpu` partition.**

- Any GPU: `--gres gpu:1`
- A specific type, by name: `--gres gpu:rtx2080:1`, `--gres gpu:rtx5000:1`, `--gres gpu:a100_2g.10gb:1`

Available GPU types are listed on the SWC internal wiki (linked from the page); `sinfo` on the cluster shows partitions, their nodes and time limits.

In context, a minimal script:

```bash
#!/bin/bash

#SBATCH -J my_job                 # job name
#SBATCH -p gpu                    # partition
#SBATCH -N 1                      # nodes
#SBATCH -n 4                      # cores
#SBATCH --mem 16G                 # memory for all cores
#SBATCH -t 0-06:00                # time (D-HH:MM)
#SBATCH --gres gpu:1
#SBATCH -o slurm.%x.%N.%j.out
#SBATCH -e slurm.%x.%N.%j.err
```

Source: [SLURM arguments primer](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SLURM-arguments.md) (NIU how-to guides)

Pages read: niu-howto/programming/SLURM-arguments.md.

## jupyter-on-node: pass (2/2)

> I'm running Jupyter on a cluster node. How do I open it in my browser?


The docs cover exactly this — SSH port forwarding from your assigned compute node.

**1. On the cluster, get an interactive job** (don't SSH into unallocated nodes):

```bash
ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
ssh hpc-gw2
srun -p gpu --gres=gpu:1 --mem=16G --pty bash -i
```

**2. On the assigned node, launch Jupyter** on a chosen port with no browser:

```bash
conda activate my_env
cd /path/to/your/project
jupyter lab --no-browser --port=8082
```

Look for the "Or copy and paste one of these URLs:" lines in the output — those carry the `?token=...` you need.

**3. On your laptop, in a separate terminal**, tunnel that port through the bastion and gateway:

```bash
ssh -N <SWC-USERNAME>@<node-name> -J <SWC-USERNAME>@ssh.swc.ucl.ac.uk,<SWC-USERNAME>@hpc-gw2 -L 8082:localhost:8082
```

Replace `<node-name>` with your actual assigned node (e.g. `gpu-sr670-20`).

**4. In your browser**, paste the full URL from the Jupyter output, including the `?token=` part — e.g. `http://localhost:8082/lab?token=abc123def456...`. You can swap `127.0.0.1` for `localhost` if needed.

Troubleshooting from the page: use the same port in both commands, keep the SLURM session alive or the connection drops, and if the port is in use pick another (`8888`, `8090`) in both places.

Source: [Accessing HTTP servers on the HPC with port forwarding](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/port-forwarding.md) — the same page also shows the approach for Dash and Streamlit apps, and links to [Using VS Code with interactive SLURM jobs](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/vscode-with-slurm-job.md) if you'd rather have a full IDE.

Pages read: niu-howto/programming/port-forwarding.md.


SSH port forwarding through the bastion and gateway. The docs' approach: don't SSH into arbitrary nodes — only tunnel to the node SLURM assigned you.

**1. Get an interactive job** (on the cluster):

```bash
ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
ssh hpc-gw2
srun -p gpu --gres=gpu:1 --mem=16G --pty bash -i
```

**2. Launch Jupyter on the assigned node**, with a fixed port and no browser:

```bash
conda activate my_env
cd /path/to/your/project
jupyter lab --no-browser --port=8082
```

Note the lines after "Or copy and paste one of these URLs:" — you need the full URL *including* the `?token=...` part.

**3. Tunnel from your laptop** (separate local terminal):

```bash
ssh -N <SWC-USERNAME>@<node-name> -J <SWC-USERNAME>@ssh.swc.ucl.ac.uk,<SWC-USERNAME>@hpc-gw2 -L 8082:localhost:8082
```

Replace `<node-name>` with your actual assigned compute node (e.g. `gpu-sr670-20`).

**4. Paste the full tokenised URL into your browser**, e.g. `http://localhost:8082/lab?token=abc123def456...`

Troubleshooting from the page: use the same port in both commands; keep the SLURM session alive or the connection drops; if the port is in use, pick another (8888, 8090) in *both* commands.

Source: [Accessing HTTP servers on the HPC with port forwarding](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/port-forwarding.md) — the same page also covers Dash and Streamlit, and points to the [VS Code with interactive SLURM jobs](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/vscode-with-slurm-job.md) guide if you'd rather have a full IDE.

Pages read: niu-howto/programming/port-forwarding.md.

## sleap-cluster: pass (2/2)

> How do I train a SLEAP model on the SWC cluster?


There's a how-to guide covering exactly this: [Use SLEAP on the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/data_analysis/HPC-module-SLEAP.md).

The work splits in two: you prepare the job locally in the SLEAP GUI, then run it as a SLURM job on the cluster.

## 1. Prerequisites

- SSH access to the gateway: `ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk` then `ssh hpc-gw2`.
- SLEAP installed locally for the GUI work. Match your local version to the cluster module — for the current default `SLEAP/2026-05-08` (SLEAP v1.6.3):
  ```
  uv tool install --python 3.13 "sleap[nn]==1.6.3" --with "sleap-io==0.7.0" --with "sleap-nn==0.2.0" --torch-backend auto
  ```
- Data on `ceph` — the cluster has fast access there; copy it over with `rsync` if it lives elsewhere.
- Check what's available with `module avail SLEAP`. `module load SLEAP` gets the PyTorch-backend default (recommended for new projects); older modules like `SLEAP/2025-09-30` are the legacy TensorFlow backend.

If you have a managed Linux desktop from SWC IT, you can skip the prerequisites and just `module load SLEAP` locally — but still read the training section if you want HPC GPUs.

## 2. Prepare the training job (locally, in the GUI)

Label frames per the SLEAP tutorial, saving the project (e.g. `labels.v002.slp`) on the mounted SWC filesystem. Then *Predict* → *Run Training…* → **Export Training Job Package…** — do **not** hit `Run`, that trains locally. Set *Inference Target* to *Nothing* (run training and inference separately on the cluster). Save the `.zip` to the SWC filesystem and unzip it; the resulting folder holds the YAML configs and the packaged `.pkg.slp` labels.

## 3. Write a SLURM script

Create `train-slurm.sh` **inside the training job folder** — the commands use paths relative to it:

```bash
#!/bin/bash
#SBATCH -J slp_train
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --mem 32G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH -t 0-06:00
#SBATCH --gres gpu:a100:1
#SBATCH -o slurm.%x.%N.%j.out
#SBATCH -e slurm.%x.%N.%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=user@domain.com

nvidia-smi
module load SLEAP

sleap train --config-name centroid.yaml --config-dir . trainer_config.ckpt_dir='models'
sleap train --config-name centered_instance.yaml --config-dir . trainer_config.ckpt_dir='models'
```

Two `sleap train` calls here because the example uses the Top-Down config (centroid + centered-instance models) — adjust to whichever YAMLs your export produced.

A couple of points the guide flags specifically:

- **Don't copy `train-script.sh` verbatim.** SLEAP generates it, but its paths may point at the machine that exported the package, and its `trainer_config.run_name=...` value can contain an `=` that makes SLEAP fail with `mismatched input '=' expecting`. Writing the commands fresh, as above, lets SLEAP name runs automatically.
- **`--ntasks-per-node=1`, not `--ntasks`/`-n`** — PyTorch Lightning (which SLEAP uses) needs that form and manages GPU parallelism inside the single process.
- For any GPU use `--gres gpu:1`; list types with `sinfo -p gpu,gpu_lowp -o "%N %G" --noheader`. Avoid compute capability < 7.5 (currently just `p5000`). No separate `cuda` module needed — PyTorch bundles its own runtime.

## 4. Submit and monitor

```
cd /path/to/labels.v002.slp.training_job
sbatch train-slurm.sh
```

Monitor with `squeue --me`, `sacct`, or `cat slurm.<node>.<jobid>.out` / `.err`.

If you hit OOM: CPU RAM is `--mem`; GPU memory depends on the card, so request a bigger one (`--gres gpu:a100:1`). Failing that, shrink the model — input scaling, max stride, batch size.

## 5. Evaluate

A `models/` folder appears in the training job folder, one subfolder per run (e.g. `260512_151547.centroid.n=46`) containing `best.ckpt`, `training_config.yaml`, and metrics. In the local GUI: *Predict* → *Evaluation Metrics for Trained Models…* → *Add Trained Model(s)*.

From there you'd run inference with `sleap track` in a similar `infer-slurm.sh` (that section uses absolute paths, so it can live anywhere), then correct predictions in the GUI and loop.

If the module misbehaves, the guide's troubleshooting section has you grab an interactive GPU node (`srun -p gpu --gres=gpu:1 --pty bash -i`) and run `sleap doctor`.

Pages read: niu-howto/data_analysis/HPC-module-SLEAP.md.


Training splits into two halves: prepare the job package locally in the SLEAP GUI, then run it as a SLURM job on the cluster.

## 1. Prepare locally (SLEAP GUI on your own machine)

- Label frames following the SLEAP tutorial, saving the project (e.g. `labels.v002.slp`) **on the mounted SWC filesystem**, not local disk. Data should live on `ceph` — the cluster has fast access to it (`rsync` it over if not).
- *Predict* → *Run Training…* → **Export Training Job Package…** (don't hit *Run*, that trains locally). Set *Inference Target* to **Nothing** — run training and inference as separate cluster jobs.
- Save the `.zip` next to your project file and unzip it. The folder contains the YAML configs (e.g. `centroid.yaml`, `centered_instance.yaml`), `labels.v002.pkg.slp`, and a `train-script.sh`.
- Install SLEAP locally at a version matching the cluster module. For the current default module (`SLEAP/2026-05-08` = SLEAP v1.6.3):
  ```
  uv tool install --python 3.13 "sleap[nn]==1.6.3" --with "sleap-io==0.7.0" --with "sleap-nn==0.2.0" --torch-backend auto
  ```

## 2. Run on the cluster

```console
ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
ssh hpc-gw2
cd /ceph/.../labels.v002.slp.training_job
```

`module load SLEAP` gets the recommended PyTorch build; `module avail SLEAP` lists alternatives.

Create `train-slurm.sh` **inside the training job folder** (the commands use relative paths):

```bash
#!/bin/bash
#SBATCH -J slp_train
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --mem 32G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH -t 0-06:00
#SBATCH --gres gpu:a100:1
#SBATCH -o slurm.%x.%N.%j.out
#SBATCH -e slurm.%x.%N.%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=user@domain.com

nvidia-smi
module load SLEAP

sleap train --config-name centroid.yaml --config-dir . trainer_config.ckpt_dir='models'
sleap train --config-name centered_instance.yaml --config-dir . trainer_config.ckpt_dir='models'
```

Then submit from that same folder:

```console
sbatch train-slurm.sh
squeue --me        # or sacct, or cat slurm.*.out / .err
```

Notes worth knowing:
- Write the `sleap train` commands yourself rather than reusing the exported `train-script.sh` — it may reference paths from the exporting machine, and its `trainer_config.run_name=...` value can contain an `=` that makes SLEAP fail with `mismatched input '=' expecting`.
- `--ntasks-per-node=1` is required: PyTorch Lightning manages GPU parallelism inside one process.
- One `sleap train` call per model — the two above are the Top-Down config (centroid + centered instance).
- `--gres gpu:1` for any GPU; list types with `sinfo -p gpu,gpu_lowp -o "%N %G" --noheader`. Avoid `p5000` cards (compute capability too low for PyTorch ≥ 2.5).

## 3. Evaluate

A `models/` subfolder appears with one directory per run (e.g. `260512_151547.centroid.n=46`) holding `best.ckpt`, `training_config.yaml` and metrics. In the local GUI: *Predict* → *Evaluation Metrics for Trained Models…* → *Add Trained Model(s)*.

If the module misbehaves, grab an interactive GPU node with `srun -p gpu --gres=gpu:1 --pty bash -i`, then `nvidia-smi` and `sleap doctor` (check the `[GPU / CUDA]` section).

Source: [Use SLEAP on the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/data_analysis/HPC-module-SLEAP.md) — it also covers inference with `sleap track` and the legacy TensorFlow modules (`sleap-train`/`sleap-track` with JSON configs).

Pages read: niu-howto/data_analysis/HPC-module-SLEAP.md.

## cruft: pass (2/2)

> How do I pull template updates into a project I made with the NIU cookiecutter?


Use **cruft**. Per the NIU how-to:

**1. One-time setup (if there's no `.cruft.json` yet)**

```bash
pip install cruft
cruft link https://github.com/neuroinformatics-unit/python-cookiecutter
```

It re-asks the original cookiecutter questions — give the same answers as before, except enter **"provide later"** for `github_repository_url` (the docs note that a real URL there makes `cruft diff` fail). Then it asks for the commit hash of the template version you originally generated from; you find that manually in the template's history (the page's example: `9daec12bffbc32da6a252605c5e67c90028fefc0`).

This writes `.cruft.json` (template URL, commit hash, your answers) — track it in git.

**2. Pull updates**

```bash
cruft diff     # see what differs from the template
cruft update   # apply; confirm with y, or press v to view first
cruft check    # boolean: up to date or not
```

**Caveats from the page**

- `cruft update` only touches cookiecutter-generated files — it won't delete files you added, and won't delete files that were since removed from the template (do that by hand).
- Conflicts produce `your_file.rej` files; apply those bits manually and delete the `.rej` files afterwards.
- After a successful update, `.cruft.json` holds the new commit hash, so future updates build on it. Updating often makes conflicts smaller.

**3.** Commit to a branch, open a PR into `main`, check GitHub Actions pass, then merge.

Source: [Update cookiecutter-generated files with cruft](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/Cookiecutter-cruft.md)

Pages read: niu-howto/programming/Cookiecutter-cruft.md.


Use `cruft`. The docs cover it in two stages.

**One-time setup (`cruft link`)**

```bash
pip install cruft
cruft link https://github.com/neuroinformatics-unit/python-cookiecutter
```

It re-asks the cookiecutter questions — give the same answers you gave originally, except enter **"provide later"** for `github_repository_url` (a real URL there makes `cruft diff` fail). Then it asks for the template commit hash your repo was generated from; you have to find this manually in the template's history. This creates `.cruft.json` (URL, commit hash, your answers) — track it in git.

**Applying updates**

- `cruft diff` — see what changed vs. the template; you can apply a subset by hand.
- `cruft update` — let cruft apply them; confirm with `y`, or press `v` to view first.
- `cruft check` — boolean "am I up to date".

Caveats from the page:

- `cruft update` only touches cookiecutter-generated files — it won't delete files you added, and won't delete files removed from the template since (do that manually).
- Conflicts produce a `your_file.rej` per file; apply those by hand and delete the `.rej` files afterwards.
- On success `.cruft.json` gets the new commit hash, so later updates start from there.

Finally, commit on a branch, open a PR to `main`, and check GitHub Actions before merging.

Source: [Update cookiecutter-generated files with cruft](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/Cookiecutter-cruft.md)

Pages read: niu-howto/programming/Cookiecutter-cruft.md.

## licence: pass (2/2)

> Which licence should I choose for my research software?


**Short answer: BSD-3-Clause**, unless your software has commercial potential or depends on other software with a restrictive licence.

That's the NIU recommendation — a simple licence allowing virtually unrestricted use, with a liability disclaimer.

Before you commit to it, the docs list these checks:

1. Confirm you have permission to license it yourself (usually your group leader or department head decides).
2. Get written permission from any other contributors, especially anyone at another institute — and check their institution's and funders' requirements. Easiest if you pick the licence *before* work starts.
3. If it might have commercial potential, contact your IP/tech-transfer team (e.g. UCL Business) *before* releasing.
4. Follow funder/institute requirements. At the time of writing, UCL, Gatsby and Wellcome have no formal OSS licensing policy.
5. Check the licences of your dependencies and release accordingly.
6. Consider what other tools in the field use — compatible licences make contributing to a wider ecosystem easier.

A couple of points worth flagging:

- **Don't write your own licence** (e.g. "academic use only") unless you're an IP lawyer — use a well-established one so others don't need legal advice to use your code.
- **GPL dependencies:** if you just call the library (e.g. a separately installed Python package), licence as normal. If you bundle or link against it, check that specific licence's terms — GPL/LGPL/AGPL vary.
- **Changing later:** you can, but earlier versions stay under the original terms — hence choosing carefully up front.

**Adding it:** copy the licence text into a file named `LICENSE.txt` alongside your software. On GitHub, creating a new file named `LICENSE.txt` via the web interface gives you a "Choose a license template" button.

Useful resources the page points to: [choosealicense.com](https://choosealicense.com/), [tldrlegal.com](https://tldrlegal.com/), and the [EU licence compatibility checker](https://joinup.ec.europa.eu/collection/eupl/solution/joinup-licensing-assistant/jla-compatibility-checker) if you've included third-party code.

Source: [Software licensing — NIU how-to guides](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/Licensing.md) (note the page's own disclaimer: not written by lawyers, not legal advice, and not official SWC/GCNU/UCL guidance).

Pages read: niu-howto/open_science/Licensing.md.


The NIU how-to guide on software licensing has a direct recommendation:

**Unless your software has commercial potential or depends on other software with a restrictive licence, use the [3-Clause BSD License (BSD-3-Clause)](https://opensource.org/licenses/BSD-3-Clause)** — a simple licence allowing virtually unrestricted use, with a liability disclaimer.

Before settling on it, the guide asks you to work through:

1. Check you have permission to licence it yourself — usually your research group leader's or department head's call.
2. Get permission from any other contributors, in writing if any part was developed at another institute. Changing a licence later with external collaborators involved is tricky, so decide before work starts.
3. If the software may have commercial potential, contact your institutional IP/tech transfer team (e.g. UCL Business) **before** releasing the code.
4. Follow funder and institutional requirements. For SWC/GCNU researchers: at the time of writing, UCL, Gatsby and Wellcome have no formal OSS licensing policy.
5. Check the licences of your dependencies and release in accordance with them.
6. Consider what other software in your field uses — compatible licences make it easier to contribute to a wider ecosystem.
7. If you have specific requirements, consult a guide such as [choosealicense.com](https://choosealicense.com/) or [tldrlegal.com](https://tldrlegal.com/). Otherwise, BSD-3-Clause.

Two points worth noting: don't write your own licence (including "academic use only" variants) unless you're an IP lawyer — use a well-established one so others don't need their own legal advice. And you can change the licence later, but earlier versions stay under the original terms.

To add it: copy the licence text into a file named `LICENSE.txt` alongside your software. On GitHub, creating a new file named `LICENSE.txt` through the web interface offers a "Choose a license template" button.

The page also covers the GPL-dependency case: if the restrictive library is installed separately and you just call it (e.g. a Python package), you can licence your code as normal; bundling or linking against it may constrain you, and GPL-family terms vary.

Source: [Software licensing — NIU how-to guides](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/Licensing.md) (the guide notes it isn't written by lawyers and isn't legal advice or official SWC/GCNU/UCL guidance).

Pages read: niu-howto/open_science/Licensing.md.

## gin-dataset: pass (2/2)

> How do I publish a dataset on GIN?


## One-time setup

1. Create a [GIN account](https://gin.g-node.org/user/sign_up).
2. [Download the GIN CLI](https://gin.g-node.org/G-Node/Info/wiki/GIN+CLI+Setup#setup-gin-client), then `gin login` (prompts for username and password).
3. Check it works: `gin --version`.

## Create the repository and upload the data

Log in first with `gin login`. On MacOS/Ubuntu you may need `sudo` for some `gin` commands.

**New directory:**
```
gin create <repository-name>
```
Creates the repo on the GIN server under your account plus a local directory of the same name; then move/copy your data in.

**Existing directory** — `cd` into it, then:
```
gin create --here <repository-name>
```
(Alternatively `gin init` and `gin add-remote <remote-name> <remote-repository-location>`, e.g. `gin:<username>/<remote-repository-name>`.)

Then record and upload, in small commits:
```
gin commit --message <message> <filename>
gin upload <filename>
```
`<filename>` can be a wildcard, a whitespace-separated list, or `.` for all changes. `gin upload` sends *all* changes including deletions and renames, so a file you delete locally also disappears from the server. Uncommitted files included in the upload get committed automatically.

## Make it public

New GIN repos are **private** by default. To publish:

1. Open the remote repo's homepage (`gin repos --all` lists the URLs you have access to).
2. Click *Settings* (top right).
3. Unselect the *Private* checkbox under *Basic settings*.

## Worth deciding before you finish

Whether to **lock** the files (`gin lock <filename>` / `gin unlock <filename>`, then commit the state change). The docs recommend locking when the repo is long-term archival storage and files are read-only — it avoids storing two copies — and unlocking when people need to edit large files. Lock state is persistent: it carries over to whoever clones the repo next.

Useful checks: `gin ls` for status, `gin sync` to sync both ways.

The page doesn't cover DOI minting or formal publication/registration of a GIN dataset — only creating the repo and making it public.

Source: [Create a GIN repository for your dataset](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/GIN-repositories.md)

Pages read: niu-howto/open_science/GIN-repositories.md.


Here's the workflow from the NIU how-to guide.

## One-time setup

1. Create [a GIN account](https://gin.g-node.org/user/sign_up).
2. [Download the GIN CLI](https://gin.g-node.org/G-Node/Info/wiki/GIN+CLI+Setup#setup-gin-client) and run `gin login` (prompts for username and password).
3. Check it works: `gin --version`.

On MacOS/Ubuntu you may need `sudo` for some `gin` commands.

## Create the repository

Log in first with `gin login`, then:

- **New directory:** `gin create <repository-name>` — creates the repo on the GIN server under your account plus a local directory of the same name. Then move/copy your data files in.
- **Existing directory:** `cd` there and run `gin create --here <repository-name>`.

(Alternatively, create it [in the browser](https://gin.g-node.org/repo/create) and `gin get <username>/<remote-repository-name>`; or `gin init` plus `gin add-remote <remote-name> <remote-repository-location>`, e.g. `gin:<username>/<repo>`.)

## Upload the data

```
gin commit --message <message> <filename>
gin upload <filename>
```

`<filename>` can be a wildcard (`*.png`), a whitespace-separated list, or `.` for everything changed. Small commits are recommended; you can upload after several commits. `--to <remote-name>` targets a specific remote (`gin remotes` lists them). Note `gin upload` syncs *all* changes including deletions and renames — deleting a file locally and uploading removes it from the server too. Uncommitted changes in the file set are committed automatically on upload.

## Make it public

New GIN repos are **private** by default. To publish:

1. Open the remote repo's homepage (`gin repos --all` shows URLs).
2. Click **Settings** (top right).
3. Unselect the **Private** checkbox under **Basic settings**.

## Consider locking

Decide whether to lock the files (`gin lock <filename>` / `gin unlock <filename>`, then commit the state change). The docs recommend **locked** when the goal is long-term archival storage of read-only files on a filesystem supporting symlinks — it avoids storing two copies. Keep files **unlocked** if people need to edit large files and snapshot progress, at the cost of extra storage per commit. Lock state is persistent and carries over to whoever clones next.

Useful checks: `gin ls` for status, `gin sync` to sync bidirectionally.

Source: [Create a GIN repository for your dataset](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/GIN-repositories.md)

Pages read: niu-howto/open_science/GIN-repositories.md.

## movement-load: pass (2/2)

> How do I load DeepLabCut or SLEAP tracks into movement?


The docs cover this. There are two routes: the unified `load_dataset()` function, or the format-specific loaders.

## Unified loader (recommended)

```python
from movement.io import load_dataset

ds = load_dataset("/path/to/file.h5", source_software="auto", fps=30)
```

`source_software="auto"` is the default — movement infers it from the file format. Pass `fps` so time coordinates are in seconds rather than frame numbers. Set `source_software` explicitly if you want to pin the loader, which matters for DeepLabCut-style `.csv` files since LightningPose uses the same format (movement records the ambiguity as `ds.attrs["source_software"] = "DeepLabCut/LightningPose"`):

```python
ds = load_dataset("/path/to/file.csv", source_software="DeepLabCut", fps=30)
```

## Format-specific loaders

```python
from movement.io import load_poses

# DeepLabCut — .h5 or .csv
ds = load_poses.from_dlc_file("/path/to/file.h5", fps=30)
ds = load_poses.from_dlc_file("/path/to/file.csv", fps=30)
ds = load_poses.from_dlc_style_df(df, fps=30)   # from a DLC-style DataFrame

# SLEAP — analysis .h5 (recommended)
ds = load_poses.from_sleap_file("/path/to/file.analysis.h5", fps=30)
# SLEAP .slp (experimental)
ds = load_poses.from_sleap_file("/path/to/file.predictions.slp", fps=30)
```

Either way you get a movement dataset with the trajectories, confidence values, and metadata attributes.

## Caveats from the docs

- Only **tracked** predictions are supported — identities must be known frame to frame. Manually labelled data over non-continuous frames is not supported.
- All individuals must share the same set of keypoints. DeepLabCut's multi-animal projects allow per-individual keypoints; movement doesn't support that.
- For SLEAP, the analysis `.h5` is preferred over `.slp`.

To try it without your own data: `sample_data.list_datasets()` then `sample_data.fetch_dataset("SLEAP_three-mice_Aeon_proofread.analysis.h5")`. Use `get_supported_source_software()` to list everything loadable.

Source: [Input/Output — movement user guide](https://github.com/neuroinformatics-unit/movement/blob/v0.18.0/docs/source/user_guide/input_output.md)

Pages read: movement/user_guide/input_output.md.


The docs cover this on movement's **Input/Output** page. Two routes:

## 1. The unified loader (`load_dataset`)

```python
from movement.io import load_dataset

ds = load_dataset("/path/to/file.h5", source_software="auto", fps=30)
```

`source_software="auto"` is the default — movement infers it from the file format via `infer_source_software`. Pass it explicitly if you want to pin the loader (useful for DLC-style `.csv`, which LightningPose also uses; ambiguous cases get recorded as e.g. `ds.attrs["source_software"] = "DeepLabCut/LightningPose"`):

```python
ds = load_dataset("/path/to/file.csv", source_software="DeepLabCut", fps=30)
```

Giving `fps` puts the time coordinate in seconds instead of frame numbers.

## 2. Software-specific functions

```python
from movement.io import load_poses

# DeepLabCut — .h5 or .csv
ds = load_poses.from_dlc_file("/path/to/file.h5", fps=30)
ds = load_poses.from_dlc_file("/path/to/file.csv", fps=30)
ds = load_poses.from_dlc_style_df(df, fps=30)   # a DLC-style pandas DataFrame

# SLEAP — analysis .h5 (recommended)
ds = load_poses.from_sleap_file("/path/to/file.analysis.h5", fps=30)
# .slp is supported but experimental
ds = load_poses.from_sleap_file("/path/to/file.predictions.slp", fps=30)
```

Either way you get a movement dataset with the trajectories, confidence values, and metadata attributes.

**Two caveats the page flags:** movement only works with *tracked* predictions — manually labelled data (non-continuous frames) isn't supported; and for DLC, all individuals must share the same keypoint set, so multi-animal projects with per-individual keypoints won't load.

To try it without your own files, `sample_data.fetch_dataset("SLEAP_three-mice_Aeon_proofread.analysis.h5")` (list options with `sample_data.list_datasets()`).

Source: [Input/Output](https://github.com/neuroinformatics-unit/movement/blob/v0.18.0/docs/source/user_guide/input_output.md)

Pages read: movement/user_guide/input_output.md.

## brainglobe-install: pass (2/2)

> How do I install the BrainGlobe tools?


Install into a virtual environment (`conda` or `venv`) running Python 3.10, 3.11 or 3.12.

With conda, you can set the Python version at creation time:

```bash
conda create -c conda-forge -n brainglobe-env python=3.12
```

Then, in the activated environment:

```bash
pip install brainglobe
```

That fetches all BrainGlobe tools, their Python APIs, and their `napari` plugins — plus `napari` itself so the plugins are usable.

If you also want the analysis workflows (such as `brainmapper`, previously the `cellfinder` CLI):

```bash
pip install brainglobe-workflows>=1.0.0
```

This builds on the `brainglobe` tools, and will install `brainglobe` too if the environment doesn't already have it.

**Updating:**

```bash
pip install brainglobe --upgrade
```

Individual tools can be installed on their own by following each tool's own install instructions, but the docs note they can't guarantee a consistent, interoperable set that way — version conflicts or dependency issues are possible — so the combined `brainglobe` package is the recommended route.

Source: [Installing BrainGlobe](https://github.com/brainglobe/brainglobe.github.io/blob/37ddde1a5d1b5f15cc90649641b80bb14f4c5348/docs/source/documentation/index.md)

Pages read: brainglobe/documentation/index.md.


Install into a virtual environment (managed by `conda` or `venv`), running Python 3.10, 3.11 or 3.12.

**1. Create and activate an environment** (conda example):

```bash
conda create -c conda-forge -n brainglobe-env python=3.12
conda activate brainglobe-env
```

**2. Install all the BrainGlobe tools:**

```bash
pip install brainglobe
```

This fetches all BrainGlobe tools, their Python APIs, and their `napari` plugins where they have one — plus `napari` itself so you can use the plugins.

**3. Optionally, the analysis workflows** (e.g. `brainmapper`, previously the `cellfinder` CLI):

```bash
pip install brainglobe-workflows>=1.0.0
```

If `brainglobe` isn't already in the environment, this installs it too; otherwise it uses what you have.

**Updating:**

```bash
pip install brainglobe --upgrade
```

Individual tools can be installed on their own by following that tool's own install instructions, but the docs note they can't then guarantee a consistent, interoperable set — you may hit version or dependency conflicts.

A couple of notes from the conda page: you must run `conda activate ENV_NAME` in every new terminal window, and conda makes CUDA/cuDNN setup easier if you want GPU acceleration.

Sources:
- [Installing BrainGlobe](https://github.com/brainglobe/brainglobe.github.io/blob/37ddde1a5d1b5f15cc90649641b80bb14f4c5348/docs/source/documentation/index.md)
- [Using conda](https://github.com/brainglobe/brainglobe.github.io/blob/37ddde1a5d1b5f15cc90649641b80bb14f4c5348/docs/source/documentation/setting-up/conda.md)

Pages read: brainglobe/documentation/index.md, brainglobe/documentation/setting-up/conda.md.

## photon-mosaic-suite2p: pass (2/2)

> How do I install photon-mosaic with suite2p support?


Install it into a `uv`-managed virtual environment with the `suite2p` extra. Python 3.12 and 3.13 are supported:

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install "photon-mosaic[suite2p]"
```

The docs list three extras: `widgets` (interactive widget functionality), `suite2p` (suite2p functionality, the default for many steps), and `deconvolution` (spike deconvolution with OASIS). The example notebooks need all three:

```bash
uv pip install "photon-mosaic[widgets,suite2p,deconvolution]"
```

Source: [photon-mosaic — Usage](https://github.com/photon-mosaic/photon-mosaic/blob/v0.0.2/docs/source/user-guide.md)

Pages read: photon-mosaic/user-guide.md.


Install it into a virtual environment managed by [uv](https://docs.astral.sh/uv/getting-started/installation/), with the `suite2p` extra:

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install "photon-mosaic[suite2p]"
```

Notes from the docs:

- Supported Python versions are 3.12 and 3.13.
- `suite2p` is the extra for suite2p functionality (the default for many steps). The other extras are `widgets` (interactive widgets) and `deconvolution` (spike deconvolution with OASIS).
- If you want to run the example notebooks, they need all three: `uv pip install "photon-mosaic[widgets,suite2p,deconvolution]"`

Source: [photon-mosaic — Usage](https://github.com/photon-mosaic/photon-mosaic/blob/v0.0.2/docs/source/user-guide.md)

Pages read: photon-mosaic/user-guide.md.
