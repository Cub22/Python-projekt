from __future__ import annotations
import argparse
import cProfile
import pstats
from .analysis import run_analysis
from .report import write_report
from .logging_utils import get_logger

def build_parser():
    p = argparse.ArgumentParser(description="JST risk analytics (canonical assignment)")
    p.add_argument("--psp", required=True, help="File or directory with PSP events data (CSV/XLSX)")
    p.add_argument("--alcohol", required=True, help="File or directory with alcohol concessions data (CSV/XLSX)")
    p.add_argument("--population", required=True, help="File or directory with population data (CSV/XLSX)")
    p.add_argument("--jst-area", required=False, help="File or directory with JST area data (CSV/XLSX)")
    p.add_argument("--jst-code-length", type=int, default=7, help="Length of normalized JST code (default: 7)")
    p.add_argument("--output", required=True, help="Path to JSON file with analysis results")
    p.add_argument("--save-merged", help="Optional path to save merged dataset as CSV")
    p.add_argument("--profile-out", help="Optional path to save cProfile stats (human-readable)")
    return p

def _profiled(fn, profile_out: str, *args, **kwargs):
    pr = cProfile.Profile()
    pr.enable()
    result = fn(*args, **kwargs)
    pr.disable()
    with open(profile_out, "w", encoding="utf-8") as f:
        ps = pstats.Stats(pr, stream=f).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats(60)  # top 60 lines
    return result

def main():
    parser = build_parser()
    args = parser.parse_args()
    log = get_logger()

    run = run_analysis
    if args.profile_out:
        summary, merged = _profiled(
            run, args.profile_out,
            args.psp, args.alcohol, args.population, args.jst_area, args.jst_code_length
        )
        log.info("Saved profiling report to %s", args.profile_out)
    else:
        summary, merged = run(args.psp, args.alcohol, args.population, args.jst_area, args.jst_code_length)

    write_report(summary, merged, args.output, args.save_merged)
    log.info("Analysis complete. Results at %s", args.output)
    if args.save_merged:
        log.info("Merged CSV saved to %s", args.save_merged)

if __name__ == "__main__":
    main()
