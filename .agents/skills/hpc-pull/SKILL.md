---
name: hpc-pull
description: Copy logs (and optionally wandb offline runs) from the project's copy on MareNostrum 5 (MN5) back to the local machine. Use when asked to pull, fetch or download results or logs from MN5.
---

# Pull results from MN5

Follow `scripts/hpc/RULES.md`; `scripts/hpc/hpc config --raw` shows the settings.

```bash
scripts/hpc/hpc pull          # logs only (default; logs_dir in project.yaml)
scripts/hpc/hpc pull wandb    # wandb offline runs only (wandb_dir)
scripts/hpc/hpc pull all      # both
```

It prints `LATEST_LOG=` (the newest `.out` file, local path); show its last lines. After pulling
wandb runs, tell the user to upload them with `wandb sync --sync-all ./wandb`.

Other outputs (checkpoints, model outputs, Zarr/NetCDF files) can be tens of GB. Check the size
first (`scripts/hpc/hpc run 'du -sh PATH'`); above `preferences.ask_before.copy_gb` ask before
copying. Then copy only that path with `rsync -az` from the host `hpc` printed as `HOST=`.
