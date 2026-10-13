#!/bin/bash
#SBATCH -J legoesm_smoke
#SBATCH --output=logs/mn5/%x_%j.out
#SBATCH --error=logs/mn5/%x_%j.err
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=20
#SBATCH --gres=gpu:1

# MN5 ACC smoke test: JAX must run on the GPU, then one tiny model build + step.
# Account and queue come from scripts/hpc/hpc submit (from the repo root):
#   scripts/hpc/hpc submit smoke
# Needs: code pushed, venv built by scripts/cluster/mn5/setup_env.sh.
set -euo pipefail

echo "START TIME: $(date)  HOST: $(hostname)"
source "${SLURM_SUBMIT_DIR}/scripts/cluster/mn5/utils.sh"
cd "${SLURM_SUBMIT_DIR}"
nvidia-smi -L

# No silent CPU fallback
export JAX_PLATFORMS=cuda
PY=.venv/bin/python

"${PY}" - <<'EOF'
import jax, jax.numpy as jnp
print(f"jax {jax.__version__} backend={jax.default_backend()} devices={jax.devices()}")
assert jax.default_backend() == "gpu", jax.default_backend()
x = jnp.ones((2048, 2048), dtype=jnp.float32)
s = float((x @ x).sum())
assert s == 2.0**33, s
print(f"GPU matmul OK: sum={s:.0f}")
EOF

JAX_ENABLE_X64=1 "${PY}" -m pytest -p no:cacheprovider tests/test_bcw_latlon_smoke.py

echo "END TIME: $(date)"
