# An Efficient Task Allocation in Mobile Crowdsensing Environments

> **This repository is the official implementation of the research article:**
>
> **"An Efficient Task Allocation in Mobile Crowdsensing Environments"**
> Published in: *IEEE Transactions on Network and Service Management ( Volume: 22, Issue: 3, June 2025)*
> DOI: [10.1109/TNSM.2025.3540293](https://doi.org/10.1109/TNSM.2025.3540293)
> 
> This repository contains the implementation and experiments for **coverage-aware task allocation** in spatial crowdsourcing environments.
The core contribution is the **WFIV** algorithm, which is benchmarked against several baseline methods under different reward schemes and population sizes.
---
---

## Problem Statement

In a spatial crowdsourcing system:
- **Workers** are mobile users who carry sensing devices and can cover geographic Points of Interest (PoIs).
- **Tasks** are spatial jobs, each associated with a set of PoIs (with importance weights) and a monetary budget.
- **Goal**: assign workers to tasks to maximise the total **coverage quality** (weighted fraction of PoIs covered) while respecting each task's budget.

Each worker is paid a **reward** that depends on the coverage they contribute.
Three reward schemes are supported: *proportional*, *normalised proportional*, and *fair general*.

---

## Algorithms

| Name | Label in code | Description |
|---|---|---|
| **WFIV** | `AlgoWFIV` | Proposed algorithm – Worker-First Iterative Voting |
| **GRPS** | `AlgoPS` | Greedy Round-Robin Proportional Scheme |
| **RRTS** | `AlgoRR` | Round-Robin Task Selection |
| **Greedy** | `Greedy` | Greedy coverage maximisation |
| **CSTAg / CSTAp** | `stableTaskAssignment` | Coalition Stable Task Assignment (general / proportional) |
| **Upper-bound** | `OrToolSolver_reduction` | ILP upper bound via OR-Tools |

---

## Repository Structure

```
WFIV/
├── main.py                  # Entry point – runs parallel algorithm comparison
├── config.py                # All tunable parameters (paths, algorithms, scheme, …)
├── requirements.txt         # Python dependencies
├── run.sh                   # Convenience script to launch with MPI
├── src/
│   ├── algorithms.py        # All task allocation algorithms
│   └── functions.py         # Utility and helper functions
├── data/
│   ├── data_generation.py   # Placeholder – fill in to regenerate data from raw traces
│   ├── Random/              # Synthetic worker trajectory files (worker 0.txt … worker N.txt)
│   └── Generation/
│       ├── PoI.txt          # One PoI per line:  <x>  <y>
│       └── Cworkers.txt     # One worker per line: space-separated  <x>,<y>  PoI coords
└── results/                 # Auto-created output folder (not committed)
```

---

## Installation

**Prerequisites:** Python 3.8+, a working MPI distribution (e.g. OpenMPI or MPICH).

```bash
# Clone
git clone https://github.com/<your-username>/WFIV.git
cd WFIV

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> **OR-Tools note:** `pip install ortools` installs the pre-built wheel.
> If you are on a cluster with a non-standard architecture, check the [OR-Tools installation guide](https://developers.google.com/optimization/install).

---

## Dataset

### Pre-generated synthetic data (included)

The `data/` folder already contains a synthetic dataset generated from random worker trajectories:

| Folder | Content |
|---|---|
| `data/Random/` | 200 worker trajectory files (`worker 0.txt` … `worker 199.txt`). Each line: `<worker_id>  <x>  <y>`. |
| `data/Generation/PoI.txt` | 400 Points of Interest. Each line: `<x>  <y>`. |
| `data/Generation/Cworkers.txt` | Coverage map. Line *i* lists the PoIs that worker *i* can cover, as `<x>,<y>` pairs. |

### Generating data from raw traces (e.g. KAIST)

The raw KAIST GPS traces are **not** included in this repository.
Once you have the data, fill in `data/data_generation.py` and run:

```bash
python data/data_generation.py \
    --input /path/to/KAIST/raw \
    --output data/ \
    --num_poi 400 \
    --coverage_radius 150
```

This overwrites `data/Random/` and `data/Generation/` with the newly generated files.

---

## Running Experiments

### 1. Configure

Open [config.py](config.py) and adjust:

```python
# Dataset paths (absolute or relative to project root)
READ_DATA_PATH_WORKERS = "data/Random"
READ_DATA_PATH_POIS    = "data/Generation"
WRITE_DATA_PATH        = "results"

# Experiment setup
FIXED_USER             = "worker"   # fix workers, sweep tasks
NUMBER_OF_FIXED_USER   = 150
LIST_OF_NONFIXED_USER  = [10, 40, 80, 120, 150]

# Reward scheme: 0=general, 1=proportional, 2=normalized, 3=fair_general
REWARD_SCHEME          = 3
```

### 2. Run (single process)

```bash
python main.py
```

### 3. Run (parallel with MPI)

```bash
mpirun -n 10 python main.py
# or use the provided shell script:
bash run.sh
```

Each MPI rank handles one independent simulation.
Results are written to `results/<dataset>/fixed <entity>/<scheme>/<timestamp>/simulation_<rank>.txt`.

---

## Output Format

Each `simulation_<rank>.txt` file contains one line per population size in `LIST_OF_NONFIXED_USER`.
Each line is a space-separated list of metric tuples, one per algorithm:

```
coverage_0,budget_0,time_0 coverage_1,budget_1,time_1 ... coverage_K,budget_K,time_K
```

| Field | Meaning |
|---|---|
| `coverage` | Average coverage quality (%) across all tasks |
| `budget` | Average used budget (% of task budget) |
| `time` | CPU time (seconds) |

---

## Reward Schemes

| Scheme | Value | Description |
|---|---|---|
| General | `0` | Workers negotiate a reward freely |
| Proportional | `1` | Reward proportional to coverage contribution |
| Normalised | `2` | Reward normalised by worker's maximum possible contribution |
| Fair General | `3` | General scheme with a fairness constraint |

---

## Citation

If you use this code in your research, please cite:

```bibtex
@article{abdeddine2025wfiv,
  title   = {An Efficient Task Allocation in Mobile Crowdsensing Environments},
  author  = {Abdeddine, Abderrafi and Iraqi, Youssef and Mekouar, Loubna},
  journal = {IEEE Transactions on Network and Service Management},
  volume  = {22},
  number  = {3},
  pages   = {2323--2342},
  year    = {2025},
  doi     = {10.1109/TNSM.2025.3540293}
}
```

---

## License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.
