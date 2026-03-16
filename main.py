"""
Coverage-Aware Task Allocation in Crowdsourcing - Main Entry Point
===================================================================
Runs algorithm comparison experiments in parallel using MPI.

Each MPI rank handles one independent simulation.
Results are written per-rank to the output folder and can be
aggregated afterwards with a separate analysis script.

Usage (single process):
    python main.py

Usage (multi-process via MPI):
    mpirun -n <num_processes> python main.py

All experiment parameters are defined in config.py.
"""

import os
import sys
import random
import numpy as np
from datetime import datetime
from time import process_time

# ---------- path setup so src/ is importable ----------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import functions as f
import algorithms as algo
from config import (
    READ_DATA_PATH_WORKERS,
    READ_DATA_PATH_POIS,
    WRITE_DATA_PATH,
    FIXED_USER,
    NUMBER_OF_FIXED_USER,
    LIST_OF_NONFIXED_USER,
    REWARD_SCHEME,
    ALGORITHMS,
    ALGORITHM_NAMES,
    UPPER_BOUNDED,
)

from mpi4py import MPI

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def select_random_sampling(all_workers, all_cworkers, m):
    """Sample m workers uniformly at random and re-index them from 0."""
    workers = random.sample(all_workers, m)
    new_workers = []
    new_cworkers = []
    for i, w in enumerate(workers):
        new_workers.append([i, w[1]])
        new_cworkers.append(all_cworkers[w[0]])
    return new_workers, new_cworkers


def detect_dataset_name(path):
    """Infer dataset label from the workers data path suffix."""
    if path[-2] == "T":
        return "KAIST"
    if path[-2] == "k":
        return "New York"
    return "Random"


def scheme_subfolder(scheme):
    """Map reward scheme index to its subfolder name."""
    return {0: "general", 1: "proportional", 2: "normalized", 3: "fair_general"}.get(
        scheme, "general"
    )


# ---------------------------------------------------------------------------
# Core parallel function
# ---------------------------------------------------------------------------

def algorithm_comparison_parallel(
    read_data_path_workers,
    read_data_path_pois,
    write_data_path,
    fixed_user,
    number_of_fixed_user,
    list_of_nonfixed_user,
    number_of_simulation,
    scheme,
    algorithms,
    algorithm_names,
    upper_bounded=False,
):
    """
    Run one simulation per MPI rank and write per-rank result files.

    Parameters
    ----------
    read_data_path_workers : str
        Path to the folder containing worker trajectory files.
    read_data_path_pois : str
        Path to the folder containing PoI.txt and Cworkers.txt.
    write_data_path : str
        Root folder where result sub-folders will be created.
    fixed_user : str
        Which entity is held fixed across x-axis: "task" or "worker".
    number_of_fixed_user : int
        Size of the fixed population.
    list_of_nonfixed_user : list[int]
        Sizes of the variable population to sweep over.
    number_of_simulation : int
        Total number of independent simulation runs (= MPI world size).
    scheme : int
        Reward scheme (0=general, 1=proportional, 2=normalized, 3=fair_general).
    algorithms : list[callable]
        Algorithm functions to compare.
    algorithm_names : list[str]
        Human-readable names matching the algorithm list.
    upper_bounded : bool
        Whether to apply the extended coverage metric for the upper-bound algorithm.
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # Each rank gets a unique simulation index
    comm.scatter([i for i in range(number_of_simulation)], root=0)

    # ---- folder naming ----
    timestamp = (datetime.now()).strftime("%d-%m-%Y %H.%M.%S")
    if fixed_user == "task":
        n = number_of_fixed_user
        folder_name = f"{n}-task {timestamp}"
    else:  # "worker"
        m = number_of_fixed_user
        folder_name = f"{m}-worker {timestamp}"

    dataset_name = detect_dataset_name(read_data_path_workers)
    folder_path = os.path.join(
        write_data_path, dataset_name, f"fixed {fixed_user}", scheme_subfolder(scheme), folder_name
    )

    # ---- add CSTAp for proportional / normalized schemes ----
    algs = algorithms.copy()
    alg_names = algorithm_names.copy()
    if scheme in (1, 2):
        algs.append(algo.stableTaskAssignment)
        alg_names.append("CSTAp")

    # ---- rank-0 creates the output folder ----
    if rank == 0:
        os.makedirs(folder_path, exist_ok=True)
        print(f"[rank 0] Output folder: {folder_path}")

    # Synchronise so all ranks see the folder before writing
    comm.Barrier()

    # ---- load data ----
    all_workers = f.read_Data_Set(read_data_path_workers)
    all_poi, _ = f.readPoIandCworkers(read_data_path_pois)

    # ---- simulation loop (sweep over non-fixed population sizes) ----
    all_metrics = []
    file_index = f"simulation_{rank}.txt"
    file_full_path = os.path.join(folder_path, file_index)

    for number_of_nonfixed in list_of_nonfixed_user:

        if fixed_user == "task":
            m = number_of_nonfixed
            n = number_of_fixed_user
        else:
            n = number_of_nonfixed
            m = number_of_fixed_user

        if rank == 0:
            print(f"  {'worker' if fixed_user == 'task' else 'task'} = {number_of_nonfixed}")

        poi = f.indexPoI(all_poi)
        all_cworkers = f.ComputeCworkers(poi, all_workers)

        workers, _ = select_random_sampling(all_workers, all_cworkers, m)
        tasks = f.generateTasks(n, poi, scheme)
        f.CworkerTask(tasks, workers, f.ComputeCworkers(poi, all_workers))

        if scheme == 3:
            rewards = f.generateGeneralandFairRewards(workers, tasks, poi)
        elif scheme == 1:
            rewards = f.generateProportionalRewards(workers, tasks)
        elif scheme == 2:
            rewards = f.generateNormalizedProportionalRewards(workers, tasks)
        else:  # scheme == 0
            rewards = f.generateGeneralRewards(workers, tasks)

        metrics = f.run_simulation(algs, alg_names, workers, tasks, poi, rewards, upper_bounded)
        all_metrics.append(metrics)

    # ---- write results ----
    with open(file_full_path, "w") as fout:
        for metrics in all_metrics:
            line = " ".join(",".join(str(v) for v in metric) for metric in metrics)
            fout.write(line + "\n")

    if rank == 0:
        print(f"[rank 0] Done. Results written to {folder_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    algorithm_comparison_parallel(
        read_data_path_workers=READ_DATA_PATH_WORKERS,
        read_data_path_pois=READ_DATA_PATH_POIS,
        write_data_path=WRITE_DATA_PATH,
        fixed_user=FIXED_USER,
        number_of_fixed_user=NUMBER_OF_FIXED_USER,
        list_of_nonfixed_user=LIST_OF_NONFIXED_USER,
        number_of_simulation=MPI.COMM_WORLD.Get_size(),
        scheme=REWARD_SCHEME,
        algorithms=ALGORITHMS,
        algorithm_names=ALGORITHM_NAMES,
        upper_bounded=UPPER_BOUNDED,
    )
