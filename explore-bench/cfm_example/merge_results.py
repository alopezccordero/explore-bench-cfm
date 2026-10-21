"""Concatenate the per-seed csvs an array job writes.

    python merge_results.py results_x1_seed*.csv > results_x1.csv

Each array task writes its own file because run_eval.py appends, and twenty tasks sharing
one path would interleave rows. Headers must match across inputs; a mismatch means the
files came from different code versions and merging them would misalign columns, so this
refuses rather than guessing.
"""
import csv
import sys


def main(paths):
    header = None
    rows = []
    for p in paths:
        with open(p, newline='') as f:
            r = csv.reader(f)
            h = next(r, None)
            if h is None:
                print(f'{p}: empty, skipped', file=sys.stderr)
                continue
            if header is None:
                header = h
            elif h != header:
                sys.exit(f'{p}: header differs from {paths[0]}.\n  got      {h}\n'
                         f'  expected {header}\nThese came from different code versions; '
                         f'merging them would misalign columns.')
            n = 0
            for row in r:
                rows.append(row)
                n += 1
            print(f'{p}: {n} rows', file=sys.stderr)
    if header is None:
        sys.exit('no rows found')
    w = csv.writer(sys.stdout, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
    print(f'merged {len(rows)} rows from {len(paths)} files', file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: merge_results.py <csv> [<csv> ...]')
    main(sys.argv[1:])
