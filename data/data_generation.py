"""
Dataset Generation Script
=========================
This script generates the synthetic worker and PoI datasets used by
the task allocation experiments from raw GPS traces (e.g., the KAIST
or New York check-in datasets).

TODO: Add the data generation code here.

Expected outputs
----------------
data/Random/
    worker 0.txt
    worker 1.txt
    ...
    worker N.txt

    Each file contains the GPS trajectory of one worker:
        <worker_id>  <x_coordinate>  <y_coordinate>
    one sensing event per line.

data/Generation/
    PoI.txt      – one PoI per line: <x>  <y>
    Cworkers.txt – one worker per line: space-separated  <x>,<y>  pairs
                   representing the set of PoIs that worker can cover.

Input data format (KAIST example)
----------------------------------
The raw KAIST traces are stored under:
    <KAIST_ROOT>/
        user_<id>/
            <date>.csv   (columns: timestamp, latitude, longitude, ...)

Usage (once the code is added)
-------------------------------
    python data/data_generation.py --input /path/to/raw/KAIST \
                                   --output data/ \
                                   --num_poi 400 \
                                   --coverage_radius 150
"""

# ---------------------------------------------------------------------------
# Imports (add more as needed)
# ---------------------------------------------------------------------------
import os
import argparse


# ---------------------------------------------------------------------------
# Placeholder functions – fill these in with the actual generation logic
# ---------------------------------------------------------------------------

def load_raw_traces(input_path: str):
    """
    Load raw GPS traces from *input_path*.

    Parameters
    ----------
    input_path : str
        Root directory containing the raw dataset.

    Returns
    -------
    workers : list
        List of worker objects as expected by src/functions.py.
    """
    raise NotImplementedError("TODO: implement load_raw_traces()")


def generate_poi(workers, num_poi: int = 400):
    """
    Generate a set of Points of Interest from worker trajectories.

    Parameters
    ----------
    workers : list
        Worker objects returned by load_raw_traces().
    num_poi : int
        Target number of PoIs to generate.

    Returns
    -------
    poi : list
        List of [index, [x, y]] PoI objects.
    """
    raise NotImplementedError("TODO: implement generate_poi()")


def compute_cworkers(workers, poi, coverage_radius: float = 150.0):
    """
    For each worker compute the subset of PoIs within *coverage_radius* metres.

    Parameters
    ----------
    workers : list
    poi : list
    coverage_radius : float
        Maximum distance (metres) for a worker to cover a PoI.

    Returns
    -------
    cworkers : list[list]
        cworkers[w] = list of [x, y] coordinates of PoIs covered by worker w.
    """
    raise NotImplementedError("TODO: implement compute_cworkers()")


def save_workers(workers, output_dir: str):
    """Write worker files to *output_dir*/Random/."""
    out = os.path.join(output_dir, "Random")
    os.makedirs(out, exist_ok=True)
    for w in workers:
        with open(os.path.join(out, f"worker {w[0]}.txt"), "w") as fout:
            for point in w[1]:
                fout.write(f"{w[0]} {point[0]} {point[1]}\n")


def save_poi_and_cworkers(poi, cworkers, output_dir: str):
    """Write PoI.txt and Cworkers.txt to *output_dir*/Generation/."""
    out = os.path.join(output_dir, "Generation")
    os.makedirs(out, exist_ok=True)

    with open(os.path.join(out, "PoI.txt"), "w") as fout:
        for p in poi:
            fout.write(f"{p[1][0]} {p[1][1]}\n")

    with open(os.path.join(out, "Cworkers.txt"), "w") as fout:
        for cw in cworkers:
            line = " ".join(f"{p[0]},{p[1]}" for p in cw)
            fout.write(line + "\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate WFIV experiment datasets from raw GPS traces."
    )
    parser.add_argument("--input", required=True, help="Path to raw dataset root directory.")
    parser.add_argument("--output", default=".", help="Path to project data/ folder (default: .).")
    parser.add_argument("--num_poi", type=int, default=400, help="Number of PoIs to generate.")
    parser.add_argument(
        "--coverage_radius", type=float, default=150.0,
        help="Coverage radius in metres (default: 150)."
    )
    args = parser.parse_args()

    print(f"Loading raw traces from: {args.input}")
    workers = load_raw_traces(args.input)

    print(f"Generating {args.num_poi} PoIs …")
    poi = generate_poi(workers, args.num_poi)

    print(f"Computing coverage (radius={args.coverage_radius} m) …")
    cworkers = compute_cworkers(workers, poi, args.coverage_radius)

    print(f"Saving to: {args.output}")
    save_workers(workers, args.output)
    save_poi_and_cworkers(poi, cworkers, args.output)

    print("Done.")


if __name__ == "__main__":
    main()
