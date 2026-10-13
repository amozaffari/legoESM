"""Unit tests for the Phase-5 experiment harness scripts
(``scripts/experiment/{init_experiment,lego_detect_machine}.py``).
"""
from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.tier0

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXP_DIR = _REPO_ROOT / "scripts" / "experiment"


@pytest.fixture(scope="module")
def mod():
    if str(_EXP_DIR) not in sys.path:
        sys.path.insert(0, str(_EXP_DIR))
    return (
        importlib.import_module("init_experiment"),
        importlib.import_module("lego_detect_machine"),
    )


# --- lego_detect_machine ----------------------------------------------------

def test_resolve_machine_matches_macbook(mod):
    _, detect = mod
    prof = detect.resolve_machine("Juliens-MacBook-Pro.local")
    assert prof["name"] == "macbook"
    assert prof["jax_platforms"] == "cpu"  # Metal broken -> CPU


def test_resolve_machine_matches_levante(mod):
    _, detect = mod
    prof = detect.resolve_machine("levante1.levante.dkrz.de")
    assert prof["name"] == "levante-gpu"
    assert prof["scheduler"] == "slurm"


@pytest.mark.parametrize("host", ["as01r1b01", "alogin1"])
def test_resolve_machine_matches_mn5_acc(mod, host):
    _, detect = mod
    prof = detect.resolve_machine(host)
    assert prof["name"] == "mn5-acc"
    assert prof["scheduler"] == "slurm"
    assert prof["jax_platforms"] == "cuda"


def test_resolve_machine_falls_back_to_default(mod):
    _, detect = mod
    prof = detect.resolve_machine("some-unknown-cluster-node-42")
    assert prof["name"] == "default"


# --- init_experiment helpers ------------------------------------------------

def test_coerce_types(mod):
    init, _ = mod
    assert init._coerce("true") is True and init._coerce("False") is False
    assert init._coerce("96") == 96 and isinstance(init._coerce("96"), int)
    assert init._coerce("1e6") == 1e6
    assert init._coerce("none") is None
    assert init._coerce("kpp") == "kpp"


def test_parse_overrides_requires_equals(mod):
    init, _ = mod
    assert init._parse_overrides(["grid.resolution=96"]) == [("grid.resolution", 96)]
    with pytest.raises(SystemExit):
        init._parse_overrides(["grid.resolution"])


def test_template_path_unknown_raises(mod):
    init, _ = mod
    with pytest.raises(SystemExit):
        init._template_path("nope/does_not_exist")


# --- init_experiment end-to-end --------------------------------------------

def test_init_writes_runnable_dir(mod, tmp_path, capsys):
    init, _ = mod
    out = tmp_path / "hs"
    rc = init.main(["3d_idealized/held_suarez", "--name", "hs",
                    "--output-dir", str(out), "--machine", "default"])
    assert rc == 0
    assert (out / "config.yaml").exists()
    assert (out / "run.sh").exists()
    assert (out / "run.yaml").exists()
    run_sh = (out / "run.sh").read_text()
    assert "legoesm run config.yaml" in run_sh
    assert "JAX_PLATFORMS=cpu" in run_sh
    manifest = out / "output" / "held_suarez" / "run_manifest.json"
    assert f"legoesm reproduce {manifest} --check" in capsys.readouterr().out


def test_init_applies_overrides(mod, tmp_path):
    init, _ = mod
    from legoesm.config import Config
    out = tmp_path / "hshi"
    init.main(["3d_idealized/held_suarez", "--name", "hshi", "--output-dir", str(out),
               "--machine", "default", "-o", "grid.resolution=96"])
    cfg = Config.from_yaml(str(out / "config.yaml"))
    assert cfg.get("grid.resolution") == 96


def test_init_bad_override_fails_fast_no_dir(mod, tmp_path):
    init, _ = mod
    out = tmp_path / "bad"
    with pytest.raises(SystemExit):
        init.main(["3d_idealized/held_suarez", "--name", "bad", "--output-dir", str(out),
                   "--machine", "default", "-o", "grid.resolution=-5"])
    assert not out.exists()


def test_init_refuses_nonempty_output(mod, tmp_path):
    init, _ = mod
    out = tmp_path / "occupied"
    out.mkdir()
    (out / "stuff.txt").write_text("x")
    with pytest.raises(SystemExit):
        init.main(["3d_idealized/held_suarez", "--name", "x", "--output-dir", str(out),
                   "--machine", "default"])


# --- SLURM launcher ---------------------------------------------------------

def _first_command_index(lines):
    return next(i for i, ln in enumerate(lines)
                if ln.strip() and not ln.startswith("#"))


@pytest.mark.parametrize("machine", ["levante-gpu", "mn5-acc"])
def test_slurm_directives_precede_first_command(mod, machine):
    """sbatch ignores #SBATCH lines after the first command."""
    init, detect = mod
    lines = init.render_run_sh(detect.load_machine(machine),
                               run_cmd="legoesm run config.yaml").splitlines()
    sbatch = [i for i, ln in enumerate(lines) if ln.startswith("#SBATCH")]
    assert sbatch, "no #SBATCH directives rendered"
    assert max(sbatch) < _first_command_index(lines)


def test_mn5_acc_run_sh_directives(mod):
    init, detect = mod
    sh = init.render_run_sh(detect.load_machine("mn5-acc"),
                            run_cmd="legoesm run config.yaml")
    for d in ("#SBATCH --nodes=1", "#SBATCH --gres=gpu:1",
              "#SBATCH --cpus-per-task=20", "#SBATCH --time=01:00:00",
              "#SBATCH --output=logs/mn5/%x_%j.out"):
        assert d in sh
    # account and qos come from the submit command, never the profile
    assert "--account" not in sh and "--qos" not in sh and "--partition" not in sh
    assert "export JAX_PLATFORMS=cuda" in sh


def _run_spooled(init, tmp_path, command_field, *, submit_dir):
    """Run a rendered SLURM run.sh the way slurmd does: a copy in a spool dir,
    with a fake `scontrol` reporting ``command_field`` as the submitted path."""
    bundle = tmp_path / "runs" / "exp"
    bundle.mkdir(parents=True)
    sh = init.render_run_sh({"scheduler": "slurm", "jax_platforms": "cpu"},
                            run_cmd="pwd -P")
    (bundle / "run.sh").write_text(sh)
    spool = tmp_path / "spool"
    spool.mkdir()
    shutil.copy(bundle / "run.sh", spool / "slurm_script")
    fakebin = tmp_path / "bin"
    fakebin.mkdir()
    (fakebin / "scontrol").write_text(
        "#!/bin/sh\n"
        "echo 'JobId=1 JobName=legoesm'\n"
        f"echo '   Command={command_field}'\n"
        "echo '   WorkDir=/nowhere'\n")
    (fakebin / "scontrol").chmod(0o755)
    env = dict(os.environ, SLURM_JOB_ID="1", SLURM_SUBMIT_DIR=str(submit_dir),
               PATH=f"{fakebin}{os.pathsep}{os.environ['PATH']}")
    res = subprocess.run(["bash", str(spool / "slurm_script")], cwd=submit_dir,
                         env=env, capture_output=True, text=True)
    return bundle.resolve(), res


def test_slurm_run_sh_cds_to_submitted_bundle_absolute(mod, tmp_path):
    init, _ = mod
    bundle = tmp_path / "runs" / "exp"
    real, res = _run_spooled(init, tmp_path, f"{bundle}/run.sh", submit_dir=tmp_path)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip().splitlines()[-1] == str(real)


def test_slurm_run_sh_cds_to_submitted_bundle_relative(mod, tmp_path):
    init, _ = mod
    real, res = _run_spooled(init, tmp_path, "runs/exp/run.sh", submit_dir=tmp_path)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip().splitlines()[-1] == str(real)


def test_slurm_run_sh_fails_loudly_when_script_unknown(mod, tmp_path):
    init, _ = mod
    _, res = _run_spooled(init, tmp_path, "/does/not/exist/run.sh", submit_dir=tmp_path)
    assert res.returncode != 0
    assert "cannot locate the submitted script" in res.stderr
