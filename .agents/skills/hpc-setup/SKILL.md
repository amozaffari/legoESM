---
name: hpc-setup
description: Configure the MareNostrum 5 (MN5) HPC skills - the user's settings (SSH aliases, username, allocations, storage, preferences in ~/.config/skills4mn5/user.yaml) and this project's settings (remote copy, logs, launch scripts in scripts/hpc/project.yaml) - and test the connection. Use when asked to set up or configure the hpc skills, add an allocation, storage area or job, or when scripts/hpc/hpc reports a missing settings file or "not configured".
---

# Set up the MN5 skills

Two files, two owners:

| File | Holds | Where | Written |
|---|---|---|---|
| `user.yaml` | username, SSH aliases, allocations, storage areas, preferences | `~/.config/skills4mn5/user.yaml`, never committed | once per person and machine |
| `project.yaml` | name, remote copy, logs dir, push excludes, launch scripts, usual account | `scripts/hpc/project.yaml`, committed | once per project, shared |

Templates sit next to the script: `scripts/hpc/user.example.yaml`, `project.example.yaml`.
Keep both files in their plain YAML style (2-space indentation; no tabs, no lists of maps, no `|`
blocks; quote times and values starting with `*` or `{`).

1. **Check the install.** `scripts/hpc/hpc` must exist in this repo. If it does not, tell the
   user to run `install.sh` from their skills4mn5 checkout (`/path/to/skills4mn5/install.sh .`)
   and stop.
2. **Current state:** `scripts/hpc/hpc config`. It names missing files and prints `MISSING=` and
   `PROBLEM=` lines. Do only the part that is missing or that the user asked for. Old settings
   files from earlier versions (`scripts/hpc/hpc.env`, `hpc.local.env`, `config.yaml`) are no
   longer read: take their values over, then offer to delete those files.

## User settings (`user.yaml`)

3. **SSH.** Look for MN5 entries in `~/.ssh/config` (`grep -n -i -B1 -A4 'bsc.es' ~/.ssh/config`).
   If there are none, show the user the template in the skills4mn5 README (login nodes
   `alogin1/2.bsc.es` for ACC, `glogin1/2.bsc.es` for GPP, `transfer1..4.bsc.es`) and let them
   add it; do not edit `~/.ssh/config` without their go-ahead. Key-based login must work without
   a password prompt (`hpc` uses `BatchMode=yes`).
4. **Ask** (one round, with the guesses you can make): MN5 username; login and transfer
   aliases; every account they may charge, each with `type` (`department` or `ehpc`) and a
   `note` (what it is for, hours or end date), and their default; their storage areas on MN5
   with short names (`scratch`, `projects`, `ehpc_scratch`, ...) and notes; the `ask_before`
   thresholds; standing rules for `preferences.notes`. Storage paths can use `{user}`.
5. **Write** `~/.config/skills4mn5/user.yaml` from the template (`mkdir -p` the directory).

## Project settings (`project.yaml`)

6. **If `scripts/hpc/project.yaml` exists** (a colleague set the project up), do not rewrite
   it: check `hpc config` resolves its `remote_repo` with this user's storage names. If their
   copy lives elsewhere, put the difference in their `user.yaml` under
   `projects.<name>.<key>` (e.g. `remote_repo`, `account`) instead of editing the project file.
7. **Otherwise, create it:**
   - `name`: short project name (usually the repo name).
   - `remote_repo`: where the project lives on MN5, written with the user's storage names
     (`"{scratch}/git/<repo>"`), never a literal username or personal path.
   - `jobs`: one entry per launch script. Find candidates with
     `grep -l '^#SBATCH' -r --include='*.sh' --include='*.sbatch' .`; for each, fill `script`,
     a `usage` line from its header and `needs` (inputs that must be on MN5). Pick a
     `default_job` if there is an obvious one. `#SBATCH --output` lines give `logs_dir`.
   - `push_exclude`: the template's list plus the project's data or output directories.
   - `account`: only if the project normally charges a specific allocation.
   Tell the user to commit `scripts/hpc/project.yaml`.
8. Run `scripts/hpc/hpc config` again until there is no `MISSING=` or `PROBLEM=`.

## Test and finish

9. **Test:**
   - `scripts/hpc/hpc host` must print `HOST=`.
   - `scripts/hpc/hpc run 'pwd'` must print the remote repo path. If the directory does not
     exist yet, offer to create it (`ssh <alias> mkdir -p <path>`) and then
     `scripts/hpc/hpc push --all --dry-run` to show what a first push would send.
   - If a transfer host is set: `scripts/hpc/hpc transfer 'ls /gpfs/archive/bsc32/esarchive | head'`.
   - For each job: `scripts/hpc/hpc submit --dry-run JOB ...` shows the account and queue.
10. **Make the rules always apply (optional).** The skills read `scripts/hpc/RULES.md`
    themselves; to have it apply in every session, offer to add `@scripts/hpc/RULES.md` to the
    project's `CLAUDE.md` (Claude Code) and "Follow scripts/hpc/RULES.md when working with
    MareNostrum 5" to `AGENTS.md`.
11. **Permissions (optional, Claude Code).** Offer to allow the read-only commands in
    `.claude/settings.json` so status checks do not prompt every time:
    `Bash(scripts/hpc/hpc status*)`, `Bash(scripts/hpc/hpc wait *)`, `Bash(scripts/hpc/hpc host)`,
    `Bash(scripts/hpc/hpc config*)`, `Bash(scripts/hpc/hpc --readonly *)`,
    `Bash(scripts/hpc/hpc push --dry-run *)`, `Bash(scripts/hpc/hpc submit --dry-run *)`.

Finish with a short table of what was set (per file) and the skills now usable: `hpc-push`,
`hpc-submit`, `hpc-status`, `hpc-pull`, `hpc-esarchive`.
