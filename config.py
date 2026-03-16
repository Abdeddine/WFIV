"""
Experiment Configuration
========================
Edit this file to change dataset paths, algorithm selection,
reward scheme, and population sweep parameters.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import algorithms as algo

# ---------------------------------------------------------------------------
# Dataset paths
# ---------------------------------------------------------------------------

# Root of this project (used to build default data paths)
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Path to the folder containing worker trajectory files (worker 0.txt, worker 1.txt, …)
READ_DATA_PATH_WORKERS = os.path.join(_PROJECT_ROOT, "data", "Random")

# Path to the folder containing PoI.txt and Cworkers.txt
READ_DATA_PATH_POIS = os.path.join(_PROJECT_ROOT, "data", "Generation")

# Root folder where experiment sub-folders will be created
WRITE_DATA_PATH = os.path.join(_PROJECT_ROOT, "results")

# ---------------------------------------------------------------------------
# Experiment setup
# ---------------------------------------------------------------------------

# Which population is fixed on the x-axis: "task" or "worker"
FIXED_USER = "worker"

# Size of the fixed population
NUMBER_OF_FIXED_USER = 150

# Values of the non-fixed population to sweep over (x-axis)
LIST_OF_NONFIXED_USER = [10, 40, 80, 120, 150]

# ---------------------------------------------------------------------------
# Reward scheme
# ---------------------------------------------------------------------------
# 0 = general
# 1 = proportional
# 2 = normalized proportional
# 3 = fair general
REWARD_SCHEME = 3

# ---------------------------------------------------------------------------
# Algorithms to compare
# ---------------------------------------------------------------------------
# Each entry must be a callable with signature:
#   algorithm(workers, tasks, rewards, PoI, scheme, list_of_importance, cpw)
# and return (Mt, Mw, timex).

ALGORITHMS = [
    algo.OrToolSolver_reduction,  # Upper-bound  (ILP via OR-Tools)
    algo.AlgoPS,                  # GRPS
    algo.AlgoRR,                  # RRTS
    algo.AlgoWFIV,                # WFIV  ← proposed algorithm
    algo.Greedy,                  # Greedy
    algo.stableTaskAssignment,    # CSTAg
]

ALGORITHM_NAMES = [
    "Upper-bound",
    "GRPS",
    "RRTS",
    "WFIV",
    "Greedy",
    "CSTAg",
]

# Colours used when plotting (must match ALGORITHM_NAMES length)
COLORS = ["peru", "r", "g", "b", "k", "magenta"]

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

# Set to True to use the extended coverage metric for the upper-bound algorithm
UPPER_BOUNDED = False
