"""Condense a results csv into something readable on a phone.

    python discord_report.py "<label>" results_ec.csv [more.csv ...]

One line per (method, checkpoint, map) with the mean over seeds, then an overall line per
method. Kept narrow and short on purpose: Discord caps a message at 2000 characters and a
72-row table does not fit, so the rows are means rather than raw runs.

`steps_98` is the headline (simulator steps to 98% coverage, lower is better), `ovl` is
the paper's overlap definition, and `snap` is how far the flow landed from a real frontier
-- blank for non-learned methods, and the strongest predictor of steps there is.
"""
import collections
import csv
import statistics as st
import sys


def mean(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key) not in (None, '', 'None')]
    return st.mean(vals) if vals else None


def fmt(v, nd=0):
    return '  -  ' if v is None else f'{v:.{nd}f}'


def main(label, paths):
    out = [f'**{label}**']
    for path in paths:
        try:
            rows = list(csv.DictReader(open(path)))
        except OSError:
            out.append(f'`{path}` missing')
            continue
        if not rows:
            out.append(f'`{path}` empty')
            continue
        out.append(f'`{path}` - {len(rows)} runs')
        groups = collections.defaultdict(list)
        for r in rows:
            who = r['method'] + (f"/{r['ckpt'].replace('.pt', '')}" if r.get('ckpt') else '')
            groups[(who, r['map'])].append(r)
        out.append('```')
        out.append(f'{"method":22s}{"map":20s}{"s90":>6}{"s98":>7}{"ovl":>7}{"snap":>7}')
        for (who, mp), v in sorted(groups.items()):
            out.append(f'{who:22.22s}{mp:20.20s}{fmt(mean(v, "steps_90")):>6}'
                       f'{fmt(mean(v, "steps_98")):>7}{fmt(mean(v, "overlap"), 3):>7}'
                       f'{fmt(mean(v, "mean_snap_cells"), 1):>7}')
        # overall per method, plus the spread, because seed variance here is large
        by_who = collections.defaultdict(list)
        for (who, _), v in groups.items():
            by_who[who] += v
        out.append('-' * 69)
        for who, v in sorted(by_who.items()):
            s = [float(r['steps_98']) for r in v if r['steps_98'] not in ('', 'None')]
            sd = f'sd {st.pstdev(s):.0f}' if len(s) > 1 else ''
            out.append(f'{who:22.22s}{"ALL":20s}{fmt(mean(v, "steps_90")):>6}'
                       f'{fmt(mean(v, "steps_98")):>7}{fmt(mean(v, "overlap"), 3):>7}'
                       f'{fmt(mean(v, "mean_snap_cells"), 1):>7}  {sd}')
        out.append('```')
    print('\n'.join(out))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('usage: discord_report.py "<label>" <csv> [<csv> ...]')
    main(sys.argv[1], sys.argv[2:])
