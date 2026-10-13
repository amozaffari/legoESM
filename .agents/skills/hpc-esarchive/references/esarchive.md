# esarchive reference

Run the commands below on the transfer node: `scripts/hpc/hpc transfer 'COMMAND'`.

## The transfer nodes

- `transfer1.bsc.es` … `transfer4.bsc.es`; the only nodes where `/gpfs/archive` is mounted.
- No internet access: downloads have to happen elsewhere.
- No CPU-time limit (unlike the 300 s limit on the login nodes). They see `/gpfs/scratch/...`,
  so they can read the archive and write straight to scratch.
- BSC's batch copy tools are on PATH: `dtcp`, `dtrsync` (large copies, submitted as transfer
  jobs; prefer them over plain `cp` for TB-scale moves).

## Archive layout

Top level is by data kind, then centre / product:

```
esarchive/
  recon/<centre>/<product>/        reanalyses, e.g. recon/ecmwf/era5, era5land, era5_oper, era5eda
  exp/ ...                          model experiments
  obs/ ...                          observations
```

Within a product (ERA5 as the example) data are grouped by **time resolution**, then one directory
per **variable (and level)**, then **one NetCDF file per month**:

```
recon/ecmwf/era5/
  1hourly/<var><level>-r1440x721cds/<var><level>_<YYYYMM>.nc   e.g. 1hourly/g500-r1440x721cds/g500_202001.nc
  6hourly/<var><level>-r1440x721cds/...                      e.g. 6hourly/hus500-r1440x721cds/hus500_202001.nc
  daily_mean/, monthly_mean/, constant/, docs/, README files
```

- `r1440x721` = the regular 0.25° grid (721 latitudes incl. both poles, 1440 longitudes).
  `cds` = downloaded from the Copernicus Climate Data Store.
- Variable names follow CMOR-style short names, not ERA5 short names: `tas` (2 m temperature),
  `psl` (mean sea level pressure), `ps` (surface pressure), `uas`/`vas` (10 m wind), `tdps`
  (2 m dewpoint), `ts` (skin temperature), `prw` (total column water vapour), `clwvi` (total
  column condensed water), `ta`/`ua`/`va`/`hus`/`hur` (pressure-level temperature, wind, specific
  and relative humidity), `g` (geopotential, m² s⁻²), `w` (vertical velocity, Pa s⁻¹),
  `swvl1..4` (soil moisture layers).
- **Coverage differs per variable**: always check the first and last file of each directory you
  plan to use (`ls <dir> | head -1; ls <dir> | tail -1`) rather than assuming a common end date.
- Directories can contain job logs (`dtcp_*.out`, `*.err`) and old copies (`*_old`); ignore them.
- Read `README.txt` / `docs/known_issues.txt` in a product directory before relying on it.

## How to search

Prefer `ls` with `grep` over `find` on the archive (it is large and slow to walk):

```bash
# products under a centre
ls -d /gpfs/archive/bsc32/esarchive/recon/ecmwf/*/
# variables at one time resolution, with level counts
ls /gpfs/archive/bsc32/esarchive/recon/ecmwf/era5/1hourly | sed -E "s/[0-9]+-r1440x721cds//" | sort | uniq -c
# levels available for one variable
ls /gpfs/archive/bsc32/esarchive/recon/ecmwf/era5/1hourly | grep -E "^ta[0-9]+-" | sed -E "s/ta([0-9]+)-.*/\1/" | sort -n
# coverage and size of one variable
d=/gpfs/archive/bsc32/esarchive/recon/ecmwf/era5/1hourly/tas-r1440x721cds; ls $d | head -1; ls $d | tail -1; ls $d | wc -l; du -sh $d
```

To look inside a file (variables, dimensions, time axis), read only its header, e.g. with a
Python environment of yours on scratch that has xarray:
`<venv>/bin/python -c "import xarray as xr; print(xr.open_dataset('<file>'))"`. Anything more
than reading metadata belongs in a batch job on the copied data.

If `find` is unavoidable, bound it: `timeout 120 find <dir> -maxdepth 3 -iname "*<name>*"`.

## Copying data out: dtcp jobs only

**Transfer nodes are for data movement only: no computation on them** (no Python processing,
no format conversion, no long-running scripts). Listing, `du`/`stat` for sizes and submitting
copy jobs is fine. Anything that processes the data runs afterwards in a normal MN5 batch job on
the copy.

Always **measure the size before copying** and report it to the user, with the destination and
the free space there (`bsc_quota`; group scratch areas are often close to full). Copy only the
months/levels needed, never a whole esarchive variable directory (they go back to 1940 and are
TB-scale).

```bash
# size of a selection (no copy)
ls /gpfs/archive/bsc32/esarchive/recon/ecmwf/era5/1hourly/tas-r1440x721cds/tas_2023*.nc | xargs stat -c %s | awk '{s+=$1} END {print s/1e9 " GB"}'
```

`dtcp` = `cp` submitted as a job on the transfer cluster (`archive` partition, default limit 18 h):

```bash
dtcp [--blocking] [--time=HH:MM:SS] <cp options> SOURCE... DEST
dtcp -n -t /dest/dir file1.nc file2.nc ...   # many files into one dir; -n = never overwrite
dtq                       # list your transfer jobs (squeue-like)
dtcancel <jobid>          # cancel one
```

- `dtcp` writes `dtcp_<jobid>.out` (one `'src' -> 'dest'` line per file) and `.err` into the
  **current directory**: `cd` to a logs folder first.
- The destination directory must exist (`mkdir -p` it first).
- With `-n`, resubmitting the same command only copies files still missing.
- Related tools in `/gpfs/apps/TRANSFER/DT/bin/`: `dtrsync`, `dtmv`, `dtrm`, `dtmkdir`, `dttar`,
  `dtchecksum`.
- **Tape (HSM).** `/gpfs/archive` moves old files to tape. Such files still list with their full
  size and readable permissions, but reading them fails with `cp: error reading ...: Permission
  denied`, leaving a partial copy. Check before copying:
  `/gpfs/apps/TRANSFER/DT/bin/hsmFileState <file>` prints `migrated` (on tape) or `resident`.
  A regular user usually cannot recall migrated files owned by someone else: the recall has to
  be requested from BSC support / the esarchive maintainers, and a large selection can be mostly
  on tape. Count migrated files in a selection before submitting copies and tell the user.
- When building a file list in a shell chain, a final failing `ls` (month not in the archive)
  makes `$(...)` return non-zero and stops an `&&` chain: append `; true` inside the substitution.

## Report back

For each dataset found: full path, variable/level naming, grid, time resolution, first and last
month, file count and size, the share of files on tape, and any gaps or known issues. When the
user wants data copied, propose a destination on their scratch, estimate the volume and check
free space first.
