# Python project

An installable Python package for the canonical assignment: analysis of Polish JST-level data
covering population, alcohol-selling concessions, and fire service (PSP) events — with
basic stats, correlation hypotheses, data-quality checks, a CLI using `argparse`, unit
tests, and profiling output.

> **No hardcoded data paths.** All inputs are provided via CLI arguments or library functions.

## Quick start

```bash
# from the repo root
python -m venv .venv && source .venv/bin/activate  # PowerShell: .venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .

# Run tests
pytest

# Show CLI help
jstrisk --help
```

### Example CLI run

```bash
jstrisk   --psp /path/to/psp_dir_or_file   --alcohol /path/to/alcohol_dir_or_file   --population /path/to/population_dir_or_file   --jst-area /path/to/jst_area_dir_or_file   --output /path/to/results.json   --save-merged /path/to/merged.csv   --profile-out /path/to/profile.txt
```

The CLI will:
- Ingest CSV/XLSX files from each path (directory or file).
- Normalize and merge data at JST level (default 7-digit TERYT-like codes, hyphens stripped).
- Calculate basic stats (min/mean/max) per dataset and overall.
- Evaluate correlation hypotheses:
  - Population vs fire events,
  - Population vs alcohol outlets,
  - Alcohol outlets vs fire events,
  - **Your extra:** fire events per 1,000 residents vs alcohol outlets per 1,000 residents.
- Report inconsistencies (missing codes/years, duplicates, negative values, mismatches).
- Quantify dropped rows during merges.
- Optionally dump a profiling report via `cProfile`.

## Library usage (Python)

```python
from jstrisk.analysis import run_analysis
res, merged = run_analysis(
    psp_path="/path/to/psp",
    alcohol_path="/path/to/alcohol",
    population_path="/path/to/pop",
    jst_area_path="/path/to/area",
    jst_code_length=7,
)
print(res.keys())
merged.to_csv("merged.csv", index=False)
```

## Notebook

See `notebooks/demo.ipynb` for a minimal, runnable demonstration of the library and a quick chart.

## Data identification & merging

You must identify the *specific* files from public sources (PSP, GUS/stat.gov.pl, dane.gov.pl)
that contain:
- **PSP events** (counts by JST and year),
- **Population** (counts by JST and year),
- **Alcohol concessions** (counts by JST and year),
- **JST area** (km² by JST, possibly static over years).

The package expects tables containing at least `JST code` (code), `year`, and the respective
metric column (events/outlets/population/area). Column names are auto-detected in PL/EN variants,
or you may rename them prior to ingestion.

### Assumptions about codes
We normalize codes by dropping non-digits and truncating to `jst_code_length` (default **7**) to
approximate gmina-level TERYT. You can override with `--jst-code-length` or provide a mapping file.
See `jstrisk.clean_merge.unify_jst_codes`.

## Profiling

- Example profiler output: `docs/profiling_example.txt`
- Run your own profiling by passing `--profile-out` to the CLI.
- See `docs/profiling.md` for interpreting hotspots and potential bottlenecks (I/O, parsing, joins).

## Quality & style

- `flake8`/`pylint` hints in `setup.cfg`
- `pytest` unit tests
- PEP8 naming and short, focused functions

## License

MIT
