"""
data_generation.py — Download the CRAWDAD ncsu/mobilitymodels dataset and
generate PoI.txt / Cworkers.txt for the WFIV experiments.

Dataset
-------
CRAWDAD ncsu/mobilitymodels (Rhee et al., 2009)
https://ieee-dataport.org/open-access/crawdad-ncsumobilitymodels

The dataset is open-access (CC BY 4.0) but requires a free IEEE DataPort
account to download.  Steps:
  1. Create a free account at https://ieee-dataport.org
  2. Log in and go to the dataset page above
  3. Download  Traces_TimeXY_30sec_txt.tar.gz  (≈ 4 MB)
  4. Place the archive next to this script (in data/) and run:

       python data/data_generation.py

     Or pass the path explicitly:
       python data/data_generation.py --archive /path/to/Traces_TimeXY_30sec_txt.tar.gz

Trace file format (all five locations share the same format)
-------------------------------------------------------------
Three whitespace-separated columns in scientific notation, one row per sample
(sampled every 30 seconds):

    <time_s>   <x_meters>   <y_meters>

Example:
    0.0000000000000000e+000   -3.8420858381879395e+002   -4.6667833828169620e+001

Available location subsets (pass via --location):
    NCSU      – university campus, North Carolina (35 traces)
    KAIST     – university campus, South Korea   (92 traces)
    NewYork   – Manhattan, New York              (39 traces)
    Orlando   – Disney World, Florida            (41 traces)
    Statefair – NC State Fair                    (19 traces)
    all       – merge all locations              (default)

Output formats (identical to what src/functions.py expects)
-----------------------------------------------------------
data/Random/worker <i>.txt
    <worker_id>  <x>  <y>        one waypoint per line

data/Generation/PoI.txt
    <x> <y>                      one PoI per line

data/Generation/Cworkers.txt
    <x1>,<y1> <x2>,<y2> …       one worker per line, space-separated x,y pairs
"""

import os
import re
import math
import random
import secrets
import argparse
import tarfile

import numpy as np


# ---------------------------------------------------------------------------
# 1. Archive extraction
# ---------------------------------------------------------------------------

def extract_archive(archive_path: str, extract_to: str) -> str:
    """
    Extract *archive_path* into *extract_to*.
    Returns the root directory that contains the per-location sub-folders.
    """
    print(f"Extracting {archive_path} …")
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=extract_to)

    # The archive unpacks to a single top-level folder; find it.
    for root, dirs, files in os.walk(extract_to):
        txt_files = [f for f in files if f.endswith(".txt") and
                     not f.lower().startswith("readme")]
        if txt_files:
            # Return the first directory level that actually has .txt trace files
            return root

    raise FileNotFoundError(
        "No trace .txt files found after extracting the archive.\n"
        "Expected the archive to contain files named like NCSU_30sec_001.txt."
    )


# ---------------------------------------------------------------------------
# 2. Trace file parsing   (format: time_s  x_m  y_m, scientific notation)
# ---------------------------------------------------------------------------

def parse_trace_file(file_path: str) -> list:
    """
    Parse one trace file.

    Returns
    -------
    list of (x, y) float tuples, in time order.
    Rows with fewer than 3 columns or non-numeric values are skipped.
    """
    waypoints = []
    with open(file_path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                x = float(parts[1])
                y = float(parts[2])
                waypoints.append((x, y))
            except ValueError:
                continue
    return waypoints


def load_traces(trace_root: str, location: str = "all") -> list:
    """
    Load all trace files from *trace_root*, optionally filtered by *location*.

    Parameters
    ----------
    trace_root : str
        Directory returned by extract_archive().
    location : str
        One of 'NCSU', 'KAIST', 'NewYork', 'Orlando', 'Statefair', or 'all'.

    Returns
    -------
    list of [worker_index, [(x, y), …]]
    """
    LOCATIONS = ["NCSU", "KAIST", "NewYork", "Orlando", "Statefair"]

    if location.lower() == "all":
        selected = LOCATIONS
    else:
        # Case-insensitive match
        match = next((l for l in LOCATIONS if l.lower() == location.lower()), None)
        if match is None:
            raise ValueError(
                f"Unknown location '{location}'. "
                f"Choose from: {', '.join(LOCATIONS)}, all"
            )
        selected = [match]

    workers = []
    worker_idx = 0

    for loc in selected:
        loc_dir = os.path.join(trace_root, loc)
        if not os.path.isdir(loc_dir):
            # Some archives flatten everything into one directory
            loc_dir = trace_root

        txt_files = sorted(
            f for f in os.listdir(loc_dir)
            if f.endswith(".txt") and loc.lower() in f.lower()
        )
        if not txt_files and loc_dir == trace_root:
            # Flat archive: pick all txt files
            txt_files = sorted(
                f for f in os.listdir(trace_root) if f.endswith(".txt")
            )

        for fname in txt_files:
            fpath = os.path.join(loc_dir, fname)
            wps = parse_trace_file(fpath)
            if len(wps) >= 2:          # need at least 2 points for path geometry
                workers.append([worker_idx, wps])
                worker_idx += 1

    print(f"Loaded {len(workers)} valid worker trace(s) "
          f"(location={'all' if location.lower() == 'all' else location}).")
    return workers


# ---------------------------------------------------------------------------
# 3. Worker file output
# ---------------------------------------------------------------------------

def save_workers(workers: list, output_dir: str):
    """Write one  worker <i>.txt  per worker to *output_dir*/Random/."""
    out = os.path.join(output_dir, "Random")
    os.makedirs(out, exist_ok=True)
    for w in workers:
        wid, moves = w[0], w[1]
        with open(os.path.join(out, f"worker {wid}.txt"), "w") as fh:
            for (x, y) in moves:
                fh.write(f"{wid} {x} {y}\n")
    print(f"Saved {len(workers)} worker file(s) → {out}/")


# ---------------------------------------------------------------------------
# 4. PoI generation  (mirrors GeneratePoI in src/functions.py)
# ---------------------------------------------------------------------------

def _reorganise(workers: list) -> list:
    """[[id, [(x,y),…]],…]  →  [[xs, ys],…]"""
    return [[[p[0] for p in w[1]], [p[1] for p in w[1]]] for w in workers]


def _interpolate(w, i, myx, k, l):
    """Linear interpolation: given axis-k value myx at segment i, return axis-l value."""
    slope = 0.0
    if w[k][i + 1] != w[k][i]:
        slope = (w[l][i + 1] - w[l][i]) / (w[k][i + 1] - w[k][i])
    return slope * (myx - w[k][i]) + w[l][i], slope


def generate_poi(workers: list, num_poi: int = 400) -> list:
    """
    Generate *num_poi* Points of Interest lying on worker trajectories.
    Mirrors GeneratePoI() in src/functions.py exactly.

    Returns
    -------
    list of [index, [x, y]]
    """
    ws = _reorganise(workers)
    points = []

    for j in range(num_poi):
        w_idx = secrets.randbelow(len(ws))
        w = ws[w_idx]

        max_x, min_x = max(w[0]), min(w[0])
        max_y, min_y = max(w[1]), min(w[1])

        # Primary axis = the one with greater range
        if (max_y - min_y) > (max_x - min_x):
            k, l = 1, 0
            pmax, pmin = max_y, min_y
        else:
            k, l = 0, 1
            pmax, pmin = max_x, min_x

        myx = random.uniform(pmin, pmax)

        # Collect all y-values where the trajectory crosses myx
        list_of_y = []
        for i in range(len(w[k]) - 1):
            a, b = w[k][i], w[k][i + 1]
            if (a <= myx < b) or (b <= myx < a):
                myy, _ = _interpolate(w, i, myx, k, l)
                list_of_y.append(myy)

        if not list_of_y:
            list_of_y = [w[l][0]]

        myy = float(np.random.choice(list_of_y))

        if k == 0:
            points.append([j, [myx, myy]])
        else:
            points.append([j, [myy, myx]])

    return points


# ---------------------------------------------------------------------------
# 5. Cworkers computation  (mirrors ComputeCworkers / workerContainThePoint)
# ---------------------------------------------------------------------------

_COVERAGE_DIST = 50.0    # metres — same threshold as src/functions.py


def _covers(w, myx: float, myy: float) -> bool:
    """True if worker trajectory *w* passes within _COVERAGE_DIST of (myx, myy)."""
    xs, ys = w[0], w[1]
    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]
        if (a <= myx < b) or (b <= myx < a):
            myy_path, slope = _interpolate(w, i, myx, 0, 1)
            dist = abs(slope * myx - myy + (ys[i] - slope * xs[i])) / math.sqrt(slope ** 2 + 1)
            if dist <= _COVERAGE_DIST:
                return True
    return False


def compute_cworkers(workers: list, poi: list) -> list:
    """
    For each worker, return the list of PoI coordinates it can cover.
    Mirrors ComputeCworkers() in src/functions.py.

    Returns
    -------
    list of lists:  cworkers[w] = [[x, y], …]
    """
    ws = _reorganise(workers)
    cworkers = [[] for _ in range(len(ws))]
    total = len(poi)

    for idx, point in enumerate(poi):
        if idx % max(1, total // 10) == 0:
            print(f"  Coverage: {idx}/{total} PoIs …", end="\r", flush=True)
        myx, myy = point[1][0], point[1][1]
        for w_idx, w in enumerate(ws):
            if _covers(w, myx, myy):
                cworkers[w_idx].append([myx, myy])

    print(f"  Coverage: {total}/{total} PoIs done.   ")
    return cworkers


# ---------------------------------------------------------------------------
# 6. PoI / Cworkers file output
# ---------------------------------------------------------------------------

def save_poi_and_cworkers(poi: list, cworkers: list, output_dir: str):
    """Write PoI.txt and Cworkers.txt to *output_dir*/Generation/."""
    out = os.path.join(output_dir, "Generation")
    os.makedirs(out, exist_ok=True)

    poi_path = os.path.join(out, "PoI.txt")
    with open(poi_path, "w") as fh:
        for p in poi:
            fh.write(f"{p[1][0]} {p[1][1]} \n")
    print(f"PoI.txt      → {poi_path}  ({len(poi)} points)")

    cw_path = os.path.join(out, "Cworkers.txt")
    with open(cw_path, "w") as fh:
        for cw in cworkers:
            line = " ".join(f"{p[0]},{p[1]}" for p in cw)
            fh.write(line + "\n")
    print(f"Cworkers.txt → {cw_path}  ({len(cworkers)} workers)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate WFIV datasets from the CRAWDAD ncsu/mobilitymodels archive.\n"
            "Download Traces_TimeXY_30sec_txt.tar.gz from:\n"
            "  https://ieee-dataport.org/open-access/crawdad-ncsumobilitymodels\n"
            "(free IEEE DataPort account required)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--archive",
        default=os.path.join(os.path.dirname(__file__),
                             "Traces_TimeXY_30sec_txt.tar.gz"),
        help="Path to the downloaded archive (default: data/Traces_TimeXY_30sec_txt.tar.gz).",
    )
    parser.add_argument(
        "--output",
        default=os.path.dirname(__file__),
        help="Root data/ folder where Random/ and Generation/ are written (default: data/).",
    )
    parser.add_argument(
        "--location",
        default="NCSU",
        choices=["NCSU", "KAIST", "NewYork", "Orlando", "Statefair", "all"],
        help="Which location subset to use (default: NCSU).",
    )
    parser.add_argument(
        "--num_poi", type=int, default=400,
        help="Number of PoIs to generate (default: 400).",
    )
    parser.add_argument(
        "--extract_dir", default=None,
        help="Where to extract the archive (default: same folder as --archive).",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.archive):
        parser.error(
            f"Archive not found: {args.archive}\n\n"
            "  1. Go to https://ieee-dataport.org/open-access/crawdad-ncsumobilitymodels\n"
            "  2. Create a free IEEE DataPort account and log in\n"
            "  3. Download  Traces_TimeXY_30sec_txt.tar.gz\n"
            f"  4. Place it at  {args.archive}  and re-run this script."
        )

    extract_to = args.extract_dir or os.path.dirname(os.path.abspath(args.archive))
    trace_root = extract_archive(args.archive, extract_to)

    print(f"Loading traces (location={args.location}) …")
    workers = load_traces(trace_root, args.location)

    print(f"Generating {args.num_poi} PoIs …")
    poi = generate_poi(workers, args.num_poi)

    print("Computing Cworkers …")
    cworkers = compute_cworkers(workers, poi)

    print("Saving worker files …")
    save_workers(workers, args.output)

    print("Saving PoI.txt and Cworkers.txt …")
    save_poi_and_cworkers(poi, cworkers, args.output)

    covered = sum(1 for cw in cworkers if cw)
    print(f"\nDone — workers: {len(workers)}, PoIs: {len(poi)}, "
          f"workers covering ≥1 PoI: {covered}/{len(cworkers)}")


if __name__ == "__main__":
    main()
