#!/bin/bash
# Shared environment for legoESM on MareNostrum 5; sourced by every MN5 script.
# Jobs are submitted from the repo root, so $SLURM_SUBMIT_DIR is the repo root; outside SLURM it
# is derived from this file's location.

: "${SLURM_SUBMIT_DIR:=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
export SLURM_SUBMIT_DIR

# Large, regenerable artefacts live outside the repo, on the EuroHPC scratch:
#   bin/       uv binary   python/  uv-managed CPython   uv-cache/  wheel cache
: "${LEGOESM_MN5_ROOT:=/gpfs/scratch/ehpc819/${USER}/legoesm_mn5}"
export LEGOESM_MN5_ROOT

export PATH="${LEGOESM_MN5_ROOT}/bin:${PATH}"
export UV_CACHE_DIR="${LEGOESM_MN5_ROOT}/uv-cache"
export UV_PYTHON_INSTALL_DIR="${LEGOESM_MN5_ROOT}/python"
export UV_PYTHON_PREFERENCE=only-managed
# Cache and venv sit on different GPFS filesets: hardlinks are impossible
export UV_LINK_MODE=copy

# Compute nodes have no internet
if [ -n "${SLURM_JOB_ID:-}" ]; then
    export UV_OFFLINE=1
    export UV_PYTHON_DOWNLOADS=never
fi
