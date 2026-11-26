# 10/10 passed (sonnet-medium)

Worse than last run: no earlier run
Passing on some repeats only: none

## ssh-cluster: pass (2/2)

> How do I connect to the SWC HPC cluster from my laptop?


## Connecting to the SWC HPC cluster

**If you're at SWC on a wired connection, or on the SWC VPN**, connect directly to the gateway node:
```
ssh <SWC-USERNAME>@hpc-gw2.hpc.swc.ucl.ac.uk
```

**Otherwise** (e.g. from home, on eduroam), you need to go through the bastion node first, then hop to the gateway:
```
ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
<SWC-USERNAME>@sgw2:~$ ssh hpc-gw2
```
You'll be prompted for your SWC password each time (it won't display as you type). Type `exit` to go back a step.

**To skip typing the full address each time**, add this to `~/.ssh/config` on your laptop:
```
Host swc-bastion
    HostName ssh.swc.ucl.ac.uk
    User <SWC-USERNAME>

Host swc-gateway
    HostName hpc-gw2
    User <SWC-USERNAME>
    ProxyJump swc-bastion
```
Then just run `ssh swc-gateway`.

**To avoid typing your password every time**, set up SSH keys:
```
ssh-keygen -t ed25519
ssh-copy-id -i ~/.ssh/id_ed25519.pub swc-gateway
```

Note: the *gateway* node is only for navigating the filesystem, editing scripts, and submitting SLURM jobs — don't run computations there directly; use `srun`/`sbatch` to get a compute node instead.

Windows users: Git Bash is recommended so the commands above work as-is; native `cmd`/PowerShell is possible too but the SSH key section doesn't apply the same way.

Source: [Set up SSH for the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SSH-SWC-cluster.md)

Pages read: niu-howto/programming/SSH-SWC-cluster.md.


## Connecting to the SWC HPC cluster via SSH

**If you're on-site at SWC (wired, not eduroam) or on the SWC VPN:**
```
ssh <SWC-USERNAME>@hpc-gw2.hpc.swc.ucl.ac.uk
```

**From anywhere else** (e.g. your laptop off-site), you need to hop through the bastion node first:
```
ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
```
then, once on the bastion:
```
ssh hpc-gw2
```

Type your SWC password when prompted (it won't display as you type). Type `exit` to go back a step.

**To skip typing two commands every time**, add this to `~/.ssh/config` on your laptop:
```
Host swc-bastion
    HostName ssh.swc.ucl.ac.uk
    User <SWC-USERNAME>

Host swc-gateway
    HostName hpc-gw2
    User <SWC-USERNAME>
    ProxyJump swc-bastion
```
Then just run `ssh swc-gateway`.

**To avoid typing your password each time**, generate an SSH key pair and copy it over:
```
ssh-keygen -t ed25519
ssh-copy-id -i ~/.ssh/id_ed25519.pub swc-gateway
```

Note: the gateway node (`hpc-gw2`) is only for navigating the filesystem, editing scripts, and submitting jobs — don't run computations there; use `srun`/`sbatch` to get a compute node instead.

Source: [Set up SSH for the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SSH-SWC-cluster.md)

Pages read: , niu-howto/programming/SSH-SWC-cluster.md.

## slurm-gpu: pass (2/2)

> How do I ask for a GPU in a SLURM batch script?


To request a GPU in an SBATCH script on the SWC HPC cluster, use the `--gres` directive combined with the `gpu` partition:

```bash
#SBATCH -p gpu           # partition (queue)
#SBATCH --gres gpu:1     # request 1 GPU (of any kind)
```

Key points:
- **No GPU is allocated unless you specify `--gres`**, even if your job is on the `gpu` partition.
- To request a specific GPU type, include its name: `--gres gpu:rtx2080:1`, `--gres gpu:rtx5000:1`, `--gres gpu:a100_2g.10gb:1`, etc.
- Available GPU types are listed on the SWC internal wiki (linked from the doc below).

Source: [SLURM arguments primer](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SLURM-arguments.md)

Pages read: niu-howto/programming/SLURM-arguments.md.


To request a GPU in a SLURM batch script, use two `#SBATCH` directives together:

1. **Partition** — submit to the `gpu` partition:
   ```
   #SBATCH -p gpu
   ```
2. **Generic resources (GPU)** — explicitly request the GPU via `--gres`:
   ```
   #SBATCH --gres gpu:1
   ```

Note: no GPU is allocated unless you specify `--gres`, even if you're on the `gpu` partition.

- To request 1 GPU of any kind: `--gres gpu:1`
- To request a specific GPU type: `--gres gpu:rtx2080:1`, `--gres gpu:rtx5000:1`, `--gres gpu:a100_2g.10gb:1`

Example script:
```bash
#!/bin/bash

#SBATCH -J my_job # job name
#SBATCH -p gpu # partition (queue)
#SBATCH -N 1   # number of nodes
#SBATCH --mem 16G # memory pool for all cores
#SBATCH -n 4 # number of cores
#SBATCH -t 0-06:00 # time (D-HH:MM)
#SBATCH --gres gpu:1 # request 1 GPU (of any kind)
#SBATCH -o slurm.%x.%N.%j.out # STDOUT
#SBATCH -e slurm.%x.%N.%j.err # STDERR
```

You can see available GPU types on the SWC internal wiki (linked in the doc below).

Source: [SLURM arguments primer](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SLURM-arguments.md)

Pages read: niu-howto/programming/SLURM-arguments.md.

## jupyter-on-node: pass (2/2)

> I'm running Jupyter on a cluster node. How do I open it in my browser?


Here's how to open Jupyter from a cluster compute node in your browser, using SSH port forwarding:

**1. Connect to the cluster and get an interactive job** (if you haven't already):
```bash
ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
ssh hpc-gw2
srun -p gpu --gres=gpu:1 --mem=16G --pty bash -i
```

**2. On the assigned compute node**, launch Jupyter without opening a browser there, on a specific port:
```bash
conda activate my_env
cd /path/to/your/project
jupyter lab --no-browser --port=8082
```
Jupyter prints output with a line like:
```
http://localhost:8082/lab?token=abc123def456...
```
Note the port number and this full URL (with the token).

**3. On your local machine**, open a new terminal and forward that port through the bastion and gateway:
```bash
ssh -N <SWC-USERNAME>@<node-name> -J <SWC-USERNAME>@ssh.swc.ucl.ac.uk,<SWC-USERNAME>@hpc-gw2 -L 8082:localhost:8082
```
Replace `<node-name>` with your actual assigned compute node (e.g. `gpu-sr670-20`).

**4. In your local browser**, paste the complete URL from step 2 (including the `?token=` part) — that's what authenticates you to the Jupyter server.

Troubleshooting notes from the doc: make sure both commands use the same port, keep the SLURM session active (don't let it drop), and if the port is already in use try another (e.g. `8888`, `8090`) in both commands.

Source: [Accessing HTTP servers on the HPC with port forwarding](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/port-forwarding.md)

Pages read: niu-howto/programming/port-forwarding.md.


Here's the process, from the NIU how-to guide on [port forwarding on the HPC](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/port-forwarding.md):

**1. On the compute node**, launch Jupyter without a browser, on a specific port:
```bash
jupyter lab --no-browser --port=8082
```
Jupyter's output will include lines starting "Or copy and paste one of these URLs:" — note the full URL with the `?token=...` part.

**2. On your local machine**, open a new terminal and forward that port through the bastion and gateway to the compute node:
```bash
ssh -N <SWC-USERNAME>@<node-name> -J <SWC-USERNAME>@ssh.swc.ucl.ac.uk,<SWC-USERNAME>@hpc-gw2 -L 8082:localhost:8082
```
Replace `<node-name>` with your assigned compute node's name (e.g. `gpu-sr670-20`) and keep the port number consistent with step 1.

**3. In your browser**, paste in the full URL from Jupyter's output (including the `?token=` part) — e.g. `http://localhost:8082/lab?token=abc123...`.

Troubleshooting tips from the doc: if the port is in use, try a different one (e.g. `8888`, `8090`) in both commands; keep your SLURM session alive or the connection will drop.

Pages read: niu-howto/programming/port-forwarding.md.

## sleap-cluster: pass (2/2)

> How do I train a SLEAP model on the SWC cluster?


## Training a SLEAP model on the SWC HPC cluster

**Prerequisites**
- Install SLEAP locally (matching the cluster's module version) and mount the SWC filesystem, since you'll label frames locally but train on the cluster.
- SSH access: `ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk` then `ssh hpc-gw2`.
- On the cluster, check available modules with `module avail SLEAP`, and load the recommended version with `module load SLEAP` (default is the PyTorch-backed v1.6.3; use `module load SLEAP/2025-09-30` for the legacy TensorFlow version).

**1. Prepare the training job (on your local SLEAP install)**
- Label frames and save your project (e.g. `labels.v002.slp`) on the mounted SWC filesystem.
- In the SLEAP GUI: *Predict* → *Run Training…* → *Export Training Job Package…* (don't hit Run — that trains locally).
  - Set *Inference Target* to *Nothing* (train/infer separately on the cluster).
  - Save the exported zip (e.g. `labels.v002.slp.training_job.zip`) to the mounted filesystem and unzip it. This gives you a folder with YAML configs (e.g. `centroid.yaml`, `centered_instance.yaml`) and a packaged labels file (`.pkg.slp`).

**2. Run the training job (on the cluster)**
- SSH in, `cd` into the unzipped training job folder.
- Create a SLURM batch script, e.g. `train-slurm.sh`:

```bash
#!/bin/bash
#SBATCH -J slp_train # job name
#SBATCH -p gpu # partition (queue)
#SBATCH -N 1   # number of nodes
#SBATCH --mem 32G # memory pool for all cores
#SBATCH --ntasks-per-node=1 # one process per node
#SBATCH --cpus-per-task=8   # CPU cores available to the process
#SBATCH -t 0-06:00 # time (D-HH:MM)
#SBATCH --gres gpu:a100:1 # request 1 GPU of a given type
#SBATCH -o slurm.%x.%N.%j.out # STDOUT
#SBATCH -e slurm.%x.%N.%j.err # STDERR
#SBATCH --mail-type=ALL
#SBATCH --mail-user=user@domain.com

nvidia-smi
module load SLEAP

sleap train --config-name centroid.yaml --config-dir . trainer_config.ckpt_dir='models'
sleap train --config-name centered_instance.yaml --config-dir . trainer_config.ckpt_dir='models'
```

(Don't just copy the auto-generated `train-script.sh` verbatim — it can contain paths/args that break on the cluster; the doc recommends writing the `sleap train` commands yourself as above.)

- Submit it from inside the training job folder (relative paths matter): `sbatch train-slurm.sh`
- Monitor with `squeue --me`, `sacct`, or by viewing the `slurm.*.out`/`.err` log files.

**3. Evaluate**
- Trained models land in a `models/` subfolder (one per run), each with `best.ckpt`, `training_config.yaml`, and metrics.
- Use the local SLEAP GUI (*Predict* → *Evaluation Metrics for Trained Models...*) to inspect metrics.

Full guide with GPU-type selection, OOM troubleshooting, inference (`sleap track`), and the legacy TensorFlow equivalents: [Use SLEAP on the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/data_analysis/HPC-module-SLEAP.md)

Pages read: niu-howto/data_analysis/HPC-module-SLEAP.md.


## Training a SLEAP model on the SWC HPC cluster

**1. Prerequisites**
- Install SLEAP locally too (for labeling/GUI steps): `uv tool install --python 3.13 "sleap[nn]==1.6.3" --with "sleap-io==0.7.0" --with "sleap-nn==0.2.0" --torch-backend auto` (match your local version to the cluster module).
- Mount the SWC filesystem locally and keep your project data on `/ceph/...`.

**2. Prepare the training job (on your local SLEAP GUI)**
- Label frames and save the `.slp` project to the mounted `ceph` filesystem.
- In SLEAP GUI: *Predict* → *Run Training…* → **Export Training Job Package…** (don't hit Run). Set **Inference Target** to **Nothing**.
- Save/unzip the exported package (e.g. `labels.v002.slp.training_job.zip`) on `ceph`. It contains YAML configs (`centroid.yaml`, `centered_instance.yaml`, etc.) and a packaged labels file (`.pkg.slp`).

**3. Run the training job on the cluster**
```
ssh <SWC-USERNAME>@ssh.swc.ucl.ac.uk
ssh hpc-gw2
cd /path/to/labels.v002.slp.training_job
```
Create `train-slurm.sh`:
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
Then submit it from inside the training job folder (paths are relative):
```
sbatch train-slurm.sh
```

**4. Monitor**
`squeue --me`, `sacct`, or check the `slurm.*.out`/`.err` log files.

**5. Evaluate**
A `models/` folder appears with one subfolder per run (e.g. `best.ckpt`, `metrics.val.0.npz`). Load it in the local SLEAP GUI via *Predict* → *Evaluation Metrics for Trained Models...*.

Notes:
- `module load SLEAP` gives you the recommended PyTorch-based v1.6.3; for the legacy TensorFlow backend use `module load SLEAP/2025-09-30` and the `sleap-train`/JSON-config commands instead.
- Check available GPU types with `sinfo -p gpu,gpu_lowp -o "%N %G" --noheader`; avoid GPUs with CUDA compute capability below 7.5.

Full guide: [Use SLEAP on the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/data_analysis/HPC-module-SLEAP.md)

For SSH setup details: [Set up SSH for the SWC HPC cluster](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/SSH-SWC-cluster.md)

Pages read: niu-howto/data_analysis/HPC-module-SLEAP.md.

## cruft: pass (2/2)

> How do I pull template updates into a project I made with the NIU cookiecutter?


NIU recommends using **cruft** to keep a cookiecutter-generated project in sync with the template. Steps, from the docs:

1. **Install cruft**: `pip install cruft`
2. **First-time setup** — link your repo to the template:
   ```
   cruft link https://github.com/neuroinformatics-unit/python-cookiecutter
   ```
   - Answer the cookiecutter prompts the same way you did originally.
   - When asked for `github_repository_url`, choose "provide later" (entering the real URL makes `cruft diff` fail).
   - You'll then be asked for the commit hash of the cookiecutter version you originally generated from — find it by searching the template repo's history (e.g. `9daec12bffbc32da6a252605c5e67c90028fefc0`).
   - This creates a `.cruft.json` file (track it in git) storing the template URL, commit hash, and your prompt answers.
3. **See what changed**: `cruft diff`
4. **Apply the updates**: `cruft update` — confirm with `y` (or `v` to preview first).
   - It won't delete files you've added since creation, and won't delete files removed from the template — those you handle manually.
   - If some changes can't be applied cleanly, it creates `.rej` files per conflicting file; resolve those manually and delete the `.rej` files when done.
   - `.cruft.json` gets updated with the new commit hash afterward.
5. **Check status anytime**: `cruft check` (boolean: up to date or not)
6. **Commit** your changes on a new branch, open a PR, and check that CI passes before merging.

Source: [Update cookiecutter-generated files with cruft](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/Cookiecutter-cruft.md)

Pages read: , niu-howto/programming/Cookiecutter-cruft.md.


You use **cruft** to keep a NIU python-cookiecutter project in sync with the template:

**1. One-time setup** — `pip install cruft`, then:
```
cruft link https://github.com/neuroinformatics-unit/python-cookiecutter
```
Answer the cookiecutter prompts the same way you did originally, but choose "provide later" for `github_repository_url` (entering the real URL makes `cruft diff` fail). Cruft will then ask for the commit hash of the cookiecutter version you originally generated from — find this manually in the template's history. This creates a `.cruft.json` file (track it in git).

**2. Pulling updates:**
- `cruft diff` — shows what's changed between your repo and the template (you can apply a subset manually if you want).
- `cruft update` — applies the template changes for you; confirm with `y`, or press `v` first to preview.
- `cruft check` — just tells you (boolean) whether you're up to date.

Notes:
- `cruft update` won't delete files you've added since creation, and won't remove files that were deleted from the template — you handle those manually.
- If some changes can't be applied automatically, you'll get `your_file.rej` files per conflict; resolve manually and delete the `.rej` files when done.
- After `cruft update`, `.cruft.json` is updated with the new commit hash for future updates.

**3. Finish up** — commit to a new branch, open a PR into `main`, and check that CI passes before merging.

Source: [Update cookiecutter-generated files with cruft](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/programming/Cookiecutter-cruft.md)

Pages read: , niu-howto/programming/Cookiecutter-cruft.md.

## licence: pass (2/2)

> Which licence should I choose for my research software?


**Recommendation: BSD-3-Clause** — unless your software has commercial potential or depends on other software with a restrictive license.

Key points from the guide:
- **Default choice:** [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause) — simple, allows virtually unrestricted use, with a liability disclaimer.
- Use an existing, well-established license (don't write your own — e.g. don't restrict to "academic use only").
- Before choosing, make sure you have permission to license the software (from your group leader/department) and from any co-contributors, especially across institutions.
- If the software might have **commercial potential**, contact your institutional IP/tech transfer office (e.g. UCL Business) *before* release.
- Check licenses of any dependencies you bundle/link against — restrictive licenses (GPL family) may constrain your choice; calling a separately-installed library is usually fine.
- You can change the license later, but earlier released versions remain under the original terms — so choose carefully upfront.
- To add it: put the license text in a `LICENSE.txt` file in your repo (GitHub's "Choose a license template" button can help).

For specific/unusual requirements, use [choosealicense.com](https://choosealicense.com/) or [tldrlegal.com](https://tldrlegal.com/).

Source: [Software licensing — NIU how-to guides](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/Licensing.md)

Pages read: niu-howto/open_science/Licensing.md.


**Recommendation: BSD-3-Clause**, unless your software has commercial potential or depends on other software with a restrictive licence.

Key points from the NIU guide:

- Default: use the [3-Clause BSD License](https://opensource.org/licenses/BSD-3-Clause) — simple, allows virtually unrestricted use, with a liability disclaimer.
- Steps before choosing:
  1. Make sure you have permission to license it (often up to your group leader/department head).
  2. Get written permission from any other contributors, especially from other institutes.
  3. If it might have commercial potential, contact your institutional IP/tech transfer team (e.g. UCL Business) *before* releasing.
  4. Check your funder/institute requirements (note: UCL, Gatsby, and Wellcome had no formal OSS licensing policy at time of writing).
  5. Check the licences of dependencies and ensure compatibility.
  6. Consider what licences are common in your field, for ecosystem compatibility.
  7. For specific needs, use [choosealicense.com](https://choosealicense.com/).
- To add it: put the licence text in a `LICENSE.txt` file in your repo (GitHub's web UI has a "Choose a license template" button when you create that file).
- Note: you can change the licence later, but earlier releases remain under the original terms — so it's worth deciding carefully upfront.

This is **not legal advice** — the doc is explicit about that. Full page: [Software licensing](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/Licensing.md)

Pages read: niu-howto/open_science/Licensing.md.

## gin-dataset: pass (2/2)

> How do I publish a dataset on GIN?


**Source:** [Create a GIN repository for your dataset](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/GIN-repositories.md)

### One-time setup
1. Create a [GIN account](https://gin.g-node.org/user/sign_up).
2. [Download the GIN CLI](https://gin.g-node.org/G-Node/Info/wiki/GIN+CLI+Setup#setup-gin-client) and log in:
   ```
   $ gin login
   ```
3. Confirm it's working: `gin --version`

### Create and upload a repository
1. **Log in**: `gin login`
2. **Initialise a repository** — pick one:
   - In a new directory: `gin create <repository-name>` (creates the repo both on the GIN server and locally)
   - In an existing directory: `cd` into it, then `gin create --here <repository-name>`
3. **Add files**, then commit and upload:
   ```
   $ gin commit --message <message> <filename>
   $ gin upload <filename>
   ```
   `<filename>` can be a wildcard (e.g. `*.png`), a list of files, or `.` for all changed files. `gin upload` sends all local changes (including deletions/renames) to the server.
4. **Decide on file locking** (optional) — locked files save local disk space and prevent future edits; unlocked files can be edited but double local storage (see "File locking" section on the page). Toggle with `gin lock <filename>` / `gin unlock <filename>`, then commit the state change.

Helpful status commands: `gin ls` (status, like `git status`), `gin sync` (bi-directional sync), `gin logout`.

### Make it public
By default new GIN repos are **private**. To make one public:
1. Go to the repo's homepage (list yours with `gin repos --all`).
2. Click **Settings** (top right).
3. Uncheck **Private** under Basic settings.

That's the full publish workflow per the docs — let me know if you want the download/update side too.

Pages read: niu-howto/open_science/GIN-repositories.md.


Here's how to publish a dataset on GIN, per the NIU how-to guide:

**One-time setup**
1. Create a GIN account: https://gin.g-node.org/user/sign_up
2. Download/set up the GIN CLI, then log in:
   ```
   gin login
   ```
3. Check it's working: `gin --version`

**Create the repository**
- In a new directory:
  ```
  gin create <repository-name>
  ```
  This creates the repo both on the GIN server and locally, then you move/copy your files in.
- Or, in an existing directory, from inside it:
  ```
  gin create --here <repository-name>
  ```

**Add and upload your data**
```
gin commit --message <message> <filename>
gin upload <filename>
```
`<filename>` can be a wildcard (e.g. `*.png`), a list of files, or `.` for everything changed. `gin upload` (with no filename) syncs all changes, including deletions/renames.

**Decide on locking**
Optionally lock the data (`gin lock <filename>`) for long-term archival/read-only storage, or keep it unlocked if you'll keep editing large files — then commit the lock-state change.

**Make it public**
New GIN repos are private by default. To publish it publicly:
1. Go to the repo's homepage on GIN (list yours with `gin repos --all`)
2. Click *Settings* (top right)
3. Uncheck *Private* under *Basic settings*

Useful commands along the way: `gin ls` (status), `gin sync` (bidirectional sync), `gin logout`.

Source: [Create a GIN repository for your dataset](https://github.com/neuroinformatics-unit/neuroinformatics-unit/blob/29043ff0fe2692cddca11ee573d8a4e1ba263ecd/docs/source/howto/open_science/GIN-repositories.md)

Pages read: , niu-howto/open_science/GIN-repositories.md.

## movement-load: pass (2/2)

> How do I load DeepLabCut or SLEAP tracks into movement?


## Loading DeepLabCut or SLEAP tracks into `movement`

**Unified loader (recommended):**
```python
from movement.io import load_dataset

ds = load_dataset(
    "/path/to/file.h5",
    source_software="auto",  # default; infers from file format
    fps=30,
)
```
If you want to force a specific loader (useful since DLC-style `.csv` can be ambiguous with LightningPose):
```python
ds = load_dataset("/path/to/file.csv", source_software="DeepLabCut", fps=30)
```

**Software-specific functions** (from `movement.io.load_poses`):

- DeepLabCut (`.h5` or `.csv`):
  ```python
  from movement.io import load_poses
  ds = load_poses.from_dlc_file("/path/to/file.h5", fps=30)
  ```
  You can also load a DLC-style pandas DataFrame directly: `load_poses.from_dlc_style_df(df, fps=30)`.
  Note: all individuals must share the same set of keypoints — DLC's multi-animal per-individual keypoint sets aren't supported.

- SLEAP:
  ```python
  ds = load_poses.from_sleap_file("/path/to/file.analysis.h5", fps=30)  # recommended
  # or (experimental):
  ds = load_poses.from_sleap_file("/path/to/file.predictions.slp", fps=30)
  ```

Providing `fps` makes the dataset's time coordinates be in seconds rather than frame numbers.

Source: [movement Input/Output guide](https://github.com/neuroinformatics-unit/movement/blob/v0.18.0/docs/source/user_guide/input_output.md)

Pages read: movement/user_guide/input_output.md.


## Loading DeepLabCut or SLEAP tracks into `movement`

Use the unified `load_dataset()` function, which auto-detects the source software from the file format:

```python
from movement.io import load_dataset

ds = load_dataset("/path/to/file.h5", source_software="auto", fps=30)
```

Or specify the software explicitly if you want to be sure:

```python
# DeepLabCut (.h5 or .csv)
ds = load_dataset("/path/to/file.h5", source_software="DeepLabCut", fps=30)

# SLEAP (.analysis.h5 recommended, or .slp)
ds = load_dataset("/path/to/file.analysis.h5", source_software="SLEAP", fps=30)
```

`fps` is optional but recommended — it converts time coordinates to seconds instead of frame numbers.

### Software-specific loaders
If you want direct access instead of the auto-dispatching function:

```python
from movement.io import load_poses

# DeepLabCut
ds = load_poses.from_dlc_file("/path/to/file.h5", fps=30)        # .h5
ds = load_poses.from_dlc_file("/path/to/file.csv", fps=30)       # .csv
ds = load_poses.from_dlc_style_df(df, fps=30)                     # pandas DataFrame

# SLEAP
ds = load_poses.from_sleap_file("/path/to/file.analysis.h5", fps=30)   # recommended
ds = load_poses.from_sleap_file("/path/to/file.predictions.slp", fps=30)  # experimental
```

**Note:** `movement` requires all individuals to share the same set of keypoints — DeepLabCut's multi-animal projects with per-individual keypoints aren't supported.

Full reference: [movement Input/Output guide](https://github.com/neuroinformatics-unit/movement/blob/v0.18.0/docs/source/user_guide/input_output.md)

Pages read: movement/user_guide/input_output.md.

## brainglobe-install: pass (2/2)

> How do I install the BrainGlobe tools?


## Installing BrainGlobe

1. Create and activate a virtual environment (conda or venv) running Python 3.10, 3.11, or 3.12. For conda:
```bash
conda create -c conda-forge -n brainglobe-env python=3.12
```

2. Install all BrainGlobe tools with pip:
```bash
pip install brainglobe
```
This fetches all BrainGlobe tools, their Python APIs, `napari` plugins (where available), and `napari` itself.

3. (Optional) If you want the analysis workflows (e.g. `brainmapper`), also install:
```bash
pip install brainglobe-workflows>=1.0.0
```

**Updating:** `pip install brainglobe --upgrade`

**Individual tools:** Each tool in the suite can also be installed separately by following that tool's own install instructions, but the docs note this may lead to version conflicts or dependency issues, and recommend the combined `brainglobe` install unless you're confident resolving those yourself.

Source: [Installing BrainGlobe](https://github.com/brainglobe/brainglobe.github.io/blob/37ddde1a5d1b5f15cc90649641b80bb14f4c5348/docs/source/documentation/index.md)

Pages read: , brainglobe/documentation/index.md.


To install the BrainGlobe tools:

1. **Create and activate a virtual environment** (conda recommended), running Python 3.10, 3.11, or 3.12:
   ```bash
   conda create -c conda-forge -n brainglobe-env python=3.12
   conda activate brainglobe-env
   ```

2. **Install all BrainGlobe tools** with pip:
   ```bash
   pip install brainglobe
   ```
   This fetches all BrainGlobe tools, their Python APIs, and `napari` plugins (installing `napari` too).

3. **Optional — analysis workflows** (e.g. `brainmapper`, formerly the `cellfinder` CLI):
   ```bash
   pip install brainglobe-workflows>=1.0.0
   ```
   This installs `brainglobe` too if not already present.

To **update** later:
```bash
pip install brainglobe --upgrade
```

You can also install individual tools separately by following each tool's own install instructions, but the docs note this risks version conflicts/dependency issues, so they recommend the combined `brainglobe` package instead.

Source: [Installing BrainGlobe](https://github.com/brainglobe/brainglobe.github.io/blob/37ddde1a5d1b5f15cc90649641b80bb14f4c5348/docs/source/documentation/index.md), with conda setup details from [Using conda](https://github.com/brainglobe/brainglobe.github.io/blob/37ddde1a5d1b5f15cc90649641b80bb14f4c5348/docs/source/documentation/setting-up/conda.md).

Pages read: brainglobe/documentation/index.md, brainglobe/documentation/setting-up/conda.md.

## photon-mosaic-suite2p: pass (2/2)

> How do I install photon-mosaic with suite2p support?


To install photon-mosaic with suite2p support (from the [Usage page](https://github.com/photon-mosaic/photon-mosaic/blob/v0.0.2/docs/source/user-guide.md)):

1. Create and activate a virtual environment with `uv` (Python 3.12 or 3.13 supported):
```bash
uv venv --python 3.13
source .venv/bin/activate
```

2. Install photon-mosaic with the `suite2p` extra:
```bash
uv pip install "photon-mosaic[suite2p]"
```

If you also want the example-notebook dependencies (`widgets` and `deconvolution`), install all three extras together:
```bash
uv pip install "photon-mosaic[widgets,suite2p,deconvolution]"
```

Pages read: photon-mosaic/user-guide.md.


To install photon-mosaic with suite2p support (Python 3.12 or 3.13 required):

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install "photon-mosaic[suite2p]"
```

The `suite2p` extra is needed because suite2p functionality is the default for many of photon-mosaic's steps. If you also want the other extras (for the example notebooks), use `uv pip install "photon-mosaic[widgets,suite2p,deconvolution]"`.

Source: [photon-mosaic Usage docs](https://github.com/photon-mosaic/photon-mosaic/blob/v0.0.2/docs/source/user-guide.md)

Pages read: photon-mosaic/user-guide.md.
