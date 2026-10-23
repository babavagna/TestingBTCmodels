import argparse
import json
import sys
from pathlib import Path

from btc_lab.data import DataError, download, load_verified
from btc_lab.runner import run_all
from btc_lab.strategies import ROOT, load_catalog


def main():
    parser = argparse.ArgumentParser(description='Bitcoin Strategy Lab: real prices, honest comparisons.')
    sub = parser.add_subparsers(dest='command', required=True)
    dl = sub.add_parser('download', help='Download official Binance spot monthly prices and verify their checksums.')
    dl.add_argument('--start', default='2020-01', help='First month, inclusive (YYYY-MM).')
    dl.add_argument('--end', default='2026-09', help='Last month, inclusive (YYYY-MM).')
    run = sub.add_parser('run', help='Compare all installed strategies on the same verified prices.')
    run.add_argument('--gap-policy', choices=['pause', 'strict'], default='pause', help='Pause signals and reset indicators after gaps, or refuse any gaps.')
    run.add_argument('--start', help='Optional first UTC date (YYYY-MM-DD).')
    run.add_argument('--end', help='Optional last UTC date, inclusive (YYYY-MM-DD).')
    sub.add_parser('strategies', help='List the strategies and immutable original GitHub sources.')
    sub.add_parser('robustness', help='Run chronological leakage, walk-forward and sensitivity diagnostics; never claim an already seen test is untouched.')
    sub.add_parser('audit', help='Show actual coverage and gaps; does not trade or invent missing prices.')
    args = parser.parse_args()
    try:
        if args.command == 'download':
            report = download(ROOT, args.start, args.end)
            print(f"Saved {report['rows']:,} verified candles; {report['missing_hours']:,} requested hours missing.")
        elif args.command == 'run':
            summary, run = run_all(ROOT, args.start, args.end, gap_policy=args.gap_policy)
            print(summary[['strategy', 'return_pct', 'max_drawdown_pct', 'trades']].to_string(index=False))
            print(f"Real data only: {run['first_candle']} through {run['last_candle']}. See reports/run.json.")
        elif args.command == 'robustness':
            from btc_lab.robustness import run_audit
            _, report = run_audit(ROOT)
            print('Audit completed. No genuinely unseen ranks are eligible: 2025/2026 were previously inspected.')
            print(report['execution_counts'])
            print('Read reports/audit/REPORT.md.')
        elif args.command == 'strategies':
            for s in load_catalog():
                print(f"{s['id']}: {s['title']}\n  {s['source_url']}")
        else:
            candles, manifest = load_verified(ROOT)
            print(json.dumps({k: v for k, v in manifest.items() if k not in ('months', 'missing_timestamps')}, indent=2))
            groups = (candles.index.to_series().diff() != __import__('pandas').Timedelta(hours=1)).cumsum()
            print('Continuous ranges (each needs more than 201 candles):')
            for _, group in candles.groupby(groups):
                print(f'{group.index[0].isoformat()} through {group.index[-1].isoformat()}: {len(group)} candles')
    except (DataError, ValueError, OSError) as exc:
        print(f'Cannot complete this step: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
