# Rules for working on MareNostrum 5

Every agent using the hpc skills follows these rules, whichever skill is running and also when
no skill is. Settings come from two files: the user's `~/.config/skills4mn5/user.yaml` (who
they are: SSH, allocations, storage, preferences) and the project's `scripts/hpc/project.yaml`
(remote copy, jobs). `scripts/hpc/hpc config --raw` prints both merged, `project.*` keys being
the project's. Thresholds named here come from `preferences`. The user's `preferences.notes`
are rules too, and win over this file when they conflict.

This file has two parts. Everything above the marker near the end is shared by all projects: it
is maintained in the skills4mn5 repo and replaced by `install.sh`. Rules for this project only
go below the marker.

## Roles

- **The user** owns the MN5 account, the allocations and the decisions. Anything that costs
  allocation hours, takes a lot of storage, cannot be undone, or affects other people needs
  their explicit go-ahead.
- **The agent** (you) does the work on the user's behalf: prepares, checks, runs and reports.
  Everything you run is billed to the user and visible to their group.
- **`scripts/hpc/hpc`** is how you touch MN5. Use it for push, submit, status, wait, cancel,
  pull, remote commands (`run`) and the transfer node (`transfer`); do not call `ssh`, `rsync`,
  `sbatch` or `scancel` directly for those, because that skips its checks.
- **Colleagues** may share the project's MN5 copy, the group scratch and the queues. Leave
  their files and jobs alone.

## Before acting

1. Read the settings (`scripts/hpc/hpc config --raw`): `allocations` (with their notes),
   `storage`, `project.jobs` (usage and needs) and `preferences` (including `notes`).
2. If `hpc` reports `not configured` or a missing settings file, run the `hpc-setup` skill.
3. Prefer a dry run first (`push --dry-run`, `submit --dry-run`) and check its output.

## Nodes

- **Login nodes**: editing, small builds, submitting, reading logs. No heavy computation
  (processes are killed after a few minutes of CPU time).
- **Transfer nodes**: listing, sizes and `dtcp` copy jobs only. No processing.
- **Compute nodes** have no internet access: code, environments, weights and input data must
  be on MN5 before the job starts.

## Code on MN5

- Push only the files a change needs. The whole tree (`push --all`) only when the user asks.
- If a file on MN5 differs in parts you did not change, someone else edited it: compare and ask
  before overwriting.
- Environments, logs, outputs, weights and data are never pushed.

## Allocations and queues

- Charge the account `hpc` picks (the job's `account`, else the project's, else the user's
  `allocations.default`) unless the user names another. Only accounts listed in the user's
  `allocations.accounts` can be used; `hpc` refuses others. Respect each allocation's `note` (what it is for, how many hours are left).
- Ask before charging any account other than the default that the user did not name.
- Short tests go to the debug queue (one job per user at a time); `hpc` picks the queue from
  the time limit.
- Never resubmit an identical job. When `hpc submit` refuses a duplicate, the job exists: follow
  it or use its results. Do not get around the refusal by renaming, changing the queue or
  adding `--force`; `--force` only with the user's explicit go-ahead for that run.

## Ask the user first

- Jobs longer than `ask_before.hours`, on more than `ask_before.nodes` nodes, or more than
  `ask_before.jobs` jobs at once.
- Copying or pulling more than `ask_before.copy_gb` GB.
- Cancelling a job, deleting anything on MN5, `push --all`.
- Writing outside the project's remote copy and the user's `storage` areas.

## Data and storage

- Measure before moving: size of the selection and free space at the destination
  (`bsc_quota`). Propose destinations from `storage` and respect their notes.
- Never copy a whole esarchive variable directory; check how many files are on tape first.

## Following jobs and reporting

- Follow jobs with `hpc wait JOBID` (call it again while the job runs); no polling or sleep
  loops of your own.
- Report what actually happened: host, job id, the exact command, log paths, final state and
  exit code, and the first real error with its output. A failure is reported as a failure.

## Privacy

- Usernames, personal paths and personal account details live only in the user's
  `user.yaml`, outside the repo. `project.yaml` is committed: write its paths with `{user}` and
  storage names (`"{scratch}/git/repo"`), never a literal username. Keep personal values out of
  every committed file: skills, this file, code, docs.

## Keeping the rules current

- When the user states a lasting preference ("always ...", "never ...", "from now on ..."),
  offer to record it: for themselves in `preferences.notes` of their `user.yaml` (applies in
  all their projects); for everyone on this project below the marker in this file; for all
  projects as a proposed change to `scripts/hpc/RULES.md` in the skills4mn5 repo.
- When something goes wrong that a rule would have prevented, propose that rule the same way.
- Keep rules short, concrete and checkable; remove ones that no longer apply.

<!-- project rules below this line: kept by install.sh -->

## Project rules

None yet.
