---
name: hpc-push
description: Sync local code changes to the project's copy on MareNostrum 5 (MN5). Use before submitting a job that needs local edits, or when asked to push/sync/upload code to MN5 or the HPC.
---

# Push code to MN5

Follow `scripts/hpc/RULES.md`; `scripts/hpc/hpc config --raw` shows the settings.

1. See what differs from the MN5 copy (compares contents, transfers nothing):
   `scripts/hpc/hpc push --dry-run PATH...`
   Lines starting `<f` are files that would be sent; `+++++++` means new on MN5.
2. If a file you are about to push also differs in parts you did not change, compare first
   (`scripts/hpc/hpc run 'cat PATH'`) and ask the user.
3. Push: `scripts/hpc/hpc push PATH...` (files or directories, relative to the repo root).

`scripts/hpc/hpc push --all` (whole tree) only when the user asks; run it with `--dry-run`
first and show them the list. `push_exclude` in `scripts/hpc/project.yaml` lists what is never pushed.

Report the host used (`HOST=`) and the files transferred.
