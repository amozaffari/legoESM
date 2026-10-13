#!/bin/bash
# Build / refresh the legoESM venv (.venv in the repo) on MareNostrum 5.
# Run on MN5ACC4 (the login node with internet), from the repo root, after pushing the code:
#
#   bash scripts/cluster/mn5/setup_env.sh
#
# Installs uv.lock exactly (with the dev extra for pytest), then the CUDA build of the SAME jax
# version the lock pins: the lock carries the CPU jaxlib only. A later `uv sync` removes the
# CUDA plugin again, so jobs use .venv/bin/python (or `uv run --no-sync`).
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"
cd "${SLURM_SUBMIT_DIR}"

UV_VERSION="0.12.19"
PYTHON_VERSION="3.12"

if ! uv --version 2>/dev/null | grep -q "^uv ${UV_VERSION} "; then
    mkdir -p "${LEGOESM_MN5_ROOT}/bin"
    curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" |
        env UV_INSTALL_DIR="${LEGOESM_MN5_ROOT}/bin" UV_NO_MODIFY_PATH=1 sh
fi
uv --version

uv sync --frozen --python "${PYTHON_VERSION}" --extra dev

JAX_VERSION="$(.venv/bin/python -c 'import jax; print(jax.__version__)')"
uv pip install --python .venv/bin/python "jax[cuda12]==${JAX_VERSION}"

# Login nodes have no GPU: this checks imports only, the GPU check is the smoke job
.venv/bin/python - <<'EOF'
import jax, jaxlib, legoesm
import jax_cuda12_plugin  # noqa: F401
print(f"jax {jax.__version__} | jaxlib {jaxlib.__version__} | legoesm {legoesm.__file__}")
EOF
