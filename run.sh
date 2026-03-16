#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# run.sh – Launch the algorithm comparison experiment with MPI
# ---------------------------------------------------------------------------
# Usage:
#   bash run.sh [num_processes]
#
# Examples:
#   bash run.sh          # defaults to 10 processes
#   bash run.sh 4        # 4 independent simulations
# ---------------------------------------------------------------------------

set -euo pipefail

NUM_PROCS=${1:-10}

# Change to the project root (directory containing this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================="
echo "  WFIV – Coverage-Aware Task Allocation"
echo "  Processes : $NUM_PROCS"
echo "  Config    : config.py"
echo "================================================="

mpirun -n "$NUM_PROCS" python main.py

echo "================================================="
echo "  Done. Results written to results/"
echo "================================================="
