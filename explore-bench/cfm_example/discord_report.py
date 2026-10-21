"""Condense a results csv into something readable on a phone.

    python discord_report.py "<label>" results_ec.csv [more.csv ...]

One line per (method, checkpoint, map) with the mean over seeds, then an overall line per
method. Kept narrow and short on purpose: Discord caps a message at 2000 characters and a
72-row table does not fit, so the rows are means rather than raw runs.

Columns: `s98` is the mean over completed runs only, `cens` charges a non-completion the
full step budget, and `fail` counts them. Read `cens` and `fail` together -- `s98` alone
flatters a method that gives up (mmpf never finished room_with_corner on two seeds, and
its 484 was an average over the other sixteen).

Multi-sampling cut snap substantially with no measurable effect on steps, so snap is a
correlate rather than a target.
"""
import collections
import csv
import statistics as st
import sys


def mean(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key) not in (None, '', 'None')]
    return st.mean(vals) if vals else None


def censored_mean(rows):
    """steps_98 with a non-completion charged the full step budget.

    Skipping blanks silently averages a method over only its successful runs, which is
    how mmpf's 484 was reported next to teachers averaged over all 18 -- it never
    finished room_with_corner on two seeds.
    """
    out = []
    for r in rows:
        if r['steps_98'] in (None, '', 'None'):
            out.append(float(r.get('max_steps') or 2000))
        else:
            out.append(float(r['steps_98']))
    return st.mean(out) if out else None


def fails(rows):
    return sum(1 for r in rows if r['steps_98'] in (None, '', 'None'))


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
            # fold the inference settings into the label, so an arm is identified by what
            # produced it rather than by which file it landed in or what order it ran
            cfg = ''.join(f' {k[0]}{r[k]}' for k in ('nsample', 'exclude', 'euler_steps')
                          if r.get(k) not in (None, '', '1', '0.0', '20'))
            groups[(who + cfg, r['map'])].append(r)
        out.append('```')
        out.append(f'{"method":26s}{"map":18s}{"s98":>6}{"cens":>6}{"fail":>5}{"ovl":>7}{"snap":>6}')
        for (who, mp), v in sorted(groups.items()):
            out.append(f'{who:26.26s}{mp:18.18s}{fmt(mean(v, "steps_98")):>6}'
                       f'{fmt(censored_mean(v)):>6}{fails(v):>5}'
                       f'{fmt(mean(v, "overlap"), 3):>7}{fmt(mean(v, "mean_snap_cells"), 1):>6}')
        # overall per method, plus the spread, because seed variance here is large
        by_who = collections.defaultdict(list)
        for (who, _), v in groups.items():
            by_who[who] += v
        out.append('-' * 69)
        for who, v in sorted(by_who.items()):
            s = [float(r['steps_98']) for r in v if r['steps_98'] not in ('', 'None')]
            sd = f'sd {st.pstdev(s):.0f}' if len(s) > 1 else ''
            out.append(f'{who:26.26s}{"ALL":18s}{fmt(mean(v, "steps_98")):>6}'
                       f'{fmt(censored_mean(v)):>6}{fails(v):>5}'
                       f'{fmt(mean(v, "overlap"), 3):>7}{fmt(mean(v, "mean_snap_cells"), 1):>6}  {sd}')
        out.append('```')
    print('\n'.join(out))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('usage: discord_report.py "<label>" <csv> [<csv> ...]')
    main(sys.argv[1], sys.argv[2:])
