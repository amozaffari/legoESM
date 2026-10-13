---
name: hpc-submit
description: Submit a SLURM batch job on MareNostrum 5 (MN5) from the local machine. Use when asked to run, launch or submit a job, training run or experiment on MN5 or the HPC.
---

# Submit a job on MN5

Follow `scripts/hpc/RULES.md`. Read the settings first (`scripts/hpc/hpc config --raw`):
`project.jobs` (this project's launch scripts with their `usage` and `needs`, from
`scripts/hpc/project.yaml`), `allocations` (accounts, notes) and `preferences.ask_before`.

```bash
scripts/hpc/hpc submit [-A account] [-q queue] [-t time] [-J name] [--dry-run] [JOB | SCRIPT] [ARGS...]
```

- **JOB** is a name under `jobs` in `project.yaml`; **SCRIPT** an sbatch script path (`*.sh`,
  `*.sbatch`). With neither, the project's `default_job` runs. Arguments starting with `-` go after `--`.
  For a script not listed under `jobs`, read its header and `#SBATCH` lines.
- **Account**: `-A`, else the job's `account`, else the project's `account`, else the user's
  `allocations.default`. Accounts not in the user's `allocations.accounts` are refused.
- **Queue** comes from the time limit (`-t`, the job's `time`, else `#SBATCH --time`): the debug
  queue up to `slurm.debug_max_minutes`, else the account's long queue. The debug queue takes
  one job per user; `hpc` refuses a second one.
- Identical jobs (same script and arguments) queued, running or recently completed are refused.
  See RULES.md: never work around that refusal.
- The job runs the MN5 copy of the code: push edits first (`hpc-push`; `hpc submit` warns if
  the launch script differs from the local one). Inputs in the job's `needs` must be on MN5.

Steps (if the user only asked to prepare or check a job, stop after step 1):
1. `scripts/hpc/hpc submit --dry-run ...` and check `JOB=`, `ACCOUNT=`, `QUEUE=`, `TIME=`, `CMD=`.
2. Ask the user first when RULES.md says so (`preferences.ask_before` thresholds, an account
   they did not name).
3. Submit without `--dry-run`. Report `JOBID=`, the command, and `LOG_OUT=` / `LOG_ERR=`
   (relative to the MN5 repo).
4. To follow the job, call `scripts/hpc/hpc wait JOBID` repeatedly until `STATE=` is no longer
   `PENDING`/`RUNNING`. It then prints the exit code, elapsed time and the log tail.
