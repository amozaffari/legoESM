---
name: hpc-status
description: Check SLURM job status on MareNostrum 5 (MN5) and show the tail of a job's log. Use when asked how a job is doing, whether it finished or failed, or to see the MN5 queue or logs.
---

# Check jobs on MN5

Follow `scripts/hpc/RULES.md`; `scripts/hpc/hpc config --raw` shows the settings.

```bash
scripts/hpc/hpc status              # your queue + tail of the newest log
scripts/hpc/hpc status JOBID        # queue + sacct for the job + tail of its .out and .err
scripts/hpc/hpc status --all        # also every job of the last 24 h
scripts/hpc/hpc status JOBID -n 200 # more log lines
scripts/hpc/hpc wait JOBID          # block until the job ends (bounded; call again if not)
```

For a job id, `hpc` reads the log path SLURM recorded for the job (works for finished jobs too),
else looks under the project's `logs_dir` (and one level below). Other files can be read with
`scripts/hpc/hpc run 'tail -n 50 PATH'` (paths relative to the MN5 repo).

Report the job state and exit code, elapsed time, and what the log shows (progress, the first
real error). Common failures: `ModuleNotFoundError` or download attempts (compute nodes are
offline: something was not installed or staged), CUDA out of memory, a missing input file,
`TIMEOUT` (raise `-t` or checkpoint more often). Cancelling (`scripts/hpc/hpc cancel JOBID`)
needs the user's go-ahead.
