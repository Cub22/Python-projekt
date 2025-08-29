# Profiling notes

This project uses Python's built-in `cProfile` (enabled via `--profile-out`) to profile the CLI end-to-end.
The heaviest operations typically are:

1. **File I/O and parsing**: CSV/XLSX decoding in pandas.
2. **Merging**: inner joins on `(jst_code, year)`.
3. **Vectorized math**: per-capita metrics and correlation computations.

### Interpreting output

- `cumulative time` pinpoints functions that *dominate total runtime*.
- Focus on file parses (`read_csv`, `read_excel`) and the `merge_all` function for large datasets.

### Ideas for optimization (not required)

- Provide explicit `dtype`/`usecols` in readers.
- Convert `jst_code` and `year` to categoricals before merging.
- Avoid repeated normalizations in iterative runs (cache intermediate Parquet files).
- Use `pyarrow` engine (optional) for faster CSV/Excel parsing when available.
