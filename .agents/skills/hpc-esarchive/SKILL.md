---
name: hpc-esarchive
description: Search the BSC Earth Sciences data archive (esarchive) on the MN5 transfer node for datasets such as ERA5, and plan dtcp copies to MN5 scratch. Use when asked where a dataset is on MN5/BSC, what period or variables it covers, or to copy archive data.
---

# Search the BSC-ES esarchive

Follow `scripts/hpc/RULES.md`; destinations for copies are the user's `storage` areas
(`scripts/hpc/hpc config` lists them as `STORAGE=`).

The archive (`/gpfs/archive/bsc32/esarchive/`) is mounted only on the MN5 **transfer nodes**.
Run every command there with:

```bash
scripts/hpc/hpc transfer 'COMMAND'
```

Read `references/esarchive.md` (next to this file) before searching: archive layout, CMOR-style
variable names, search commands, tape (HSM) pitfalls and how to copy with `dtcp`.

Rules:
- Transfer nodes are for moving data only: listing, sizes and `dtcp` copy jobs. No processing.
- Prefer `ls | grep` over `find`; if `find` is needed, bound it (`timeout 120 find ... -maxdepth 3`).
- Measure the size of any selection and check how many files are on tape before proposing a
  copy; never copy a whole variable directory. Propose a destination from `storage`, check its
  free space (`bsc_quota`) and ask the user before submitting copy jobs.

For each dataset found, report: full path, variable/level naming, grid, time resolution, first
and last month, file count and size, gaps or known issues. With no specific request, summarise
the top-level layout and the ERA5 product.

If `hpc` reports `not configured: ssh.transfer_host`, run the `hpc-setup` skill first.
