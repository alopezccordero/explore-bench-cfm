"""Per-map paired comparison of two configurations, with honest small-sample statistics.

    python analyse_by_map.py results_x6.csv --contrast mtsp 'x5_linear ex35'
    python analyse_by_map.py results_x6.csv --table

`analyse.py` pools all 60 (map, seed) pairs, which answers "is B better overall". This
answers "on which maps", which is a different question and a much weaker one: each map has
only 10 seeds, so the exact sign test cannot return a two-sided p below 2/2^10 = 0.0020
even when B wins all ten. Per-map claims are therefore reported but marked, and the
Holm correction runs across the six maps so that "it helped on corridor" is not read off
six independent chances to find something.

Three tests, because they fail differently:

* paired t interval  -- uses the magnitudes, assumes roughly symmetric differences, and at
  n=10 its interval is wide. Reported with the t critical value, not 1.96, which would
  understate it by 16%.
* Wilcoxon signed-rank -- uses the ranks of the magnitudes. More power than the sign test,
  no normality assumption, but needs n >= 6 to say anything and ties cost it power.
* exact sign test -- uses only the directions. Weakest, assumption-free, and the one to
  quote when the differences are wildly skewed, which censored step counts are.

A non-completion is charged its run's own max_steps rather than dropped. Averaging only
the runs that finished is how mmpf's 484 once came to sit beside teachers averaged over
every run.
"""
import argparse
import collections
import csv
import statistics as st

import numpy as np
from scipy import stats

MAPS = ['loop', 'corridor', 'corner', 'room', 'loop_with_corridor', 'room_with_corner']


def label(r):
    """Method, or checkpoint plus exclusion for a student row."""
    ck = r.get('ckpt', '').replace('.pt', '').replace('cfm_', '')
    if not ck:
        return r['method']
    ex = r.get('exclude', '')
    return f"{ck} ex{float(ex):g}" if ex not in ('', None) else ck


def load(path, metric):
    rows = list(csv.DictReader(open(path)))
    g = collections.defaultdict(dict)
    cens = collections.defaultdict(int)
    for r in rows:
        v = r.get(metric)
        if v in ('', None, 'None'):
            v, c = float(r.get('max_steps') or 2000), 1
        else:
            v, c = float(v), 0
        g[label(r)][(r['map'], int(r['seed']))] = v
        cens[label(r)] += c
    return g, cens


def tests(d):
    """Paired summary of one list of differences (B minus A). Negative mean = B better."""
    n = len(d)
    out = dict(n=n, mean=st.mean(d), median=st.median(d),
               wins=sum(1 for x in d if x < 0), losses=sum(1 for x in d if x > 0))
    sd = st.stdev(d) if n > 1 else 0.0
    if n > 1 and sd > 0:
        tcrit = stats.t.ppf(0.975, n - 1)
        se = sd / np.sqrt(n)
        out['lo'], out['hi'] = out['mean'] - tcrit * se, out['mean'] + tcrit * se
    else:
        out['lo'] = out['hi'] = out['mean']
    # Wilcoxon needs at least one non-zero difference and a few pairs to be meaningful
    nz = [x for x in d if x != 0]
    if len(nz) >= 6:
        out['wilcoxon'] = float(stats.wilcoxon(d, zero_method='wilcox').pvalue)
    else:
        out['wilcoxon'] = float('nan')
    k, m = out['wins'], out['wins'] + out['losses']
    out['sign'] = float(stats.binomtest(k, m, 0.5).pvalue) if m else 1.0
    return out


def holm(ps):
    """Holm-adjusted p-values, returned in the original order."""
    idx = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(idx):
        run = max(run, ps[i] * (len(ps) - rank))
        adj[i] = min(run, 1.0)
    return adj


def contrast_report(g, a, b, metric):
    print(f'\n{"=" * 92}\n{b}  vs  {a}   (negative = {b} is better, {metric})\n{"=" * 92}')
    keys = sorted(set(g[a]) & set(g[b]))
    if not keys:
        raise SystemExit(f'no shared (map, seed) pairs between {a!r} and {b!r}')

    rows, ps = [], []
    for m in MAPS:
        d = [g[b][k] - g[a][k] for k in keys if k[0] == m]
        if d:
            t = tests(d)
            rows.append((m, t))
            ps.append(t['wilcoxon'] if t['wilcoxon'] == t['wilcoxon'] else t['sign'])
    adj = holm(ps)

    print(f'{"map":20}{"n":>3}{"win":>5}{"mean":>8}{"median":>8}'
          f'{"95% CI (t)":>18}{"wilcox":>9}{"sign":>8}{"Holm":>8}')
    for (m, t), h in zip(rows, adj):
        w = f"{t['wins']}/{t['wins'] + t['losses']}"
        print(f'{m:20}{t["n"]:>3}{w:>5}{t["mean"]:>8.0f}{t["median"]:>8.0f}'
              f'{f"[{t['lo']:.0f}, {t['hi']:.0f}]":>18}'
              f'{t["wilcoxon"]:>9.4f}{t["sign"]:>8.4f}{h:>8.3f}')

    allt = tests([g[b][k] - g[a][k] for k in keys])
    w = f"{allt['wins']}/{allt['wins'] + allt['losses']}"
    print(f'{"-" * 92}')
    print(f'{"POOLED":20}{allt["n"]:>3}{w:>5}{allt["mean"]:>8.0f}{allt["median"]:>8.0f}'
          f'{f"[{allt['lo']:.0f}, {allt['hi']:.0f}]":>18}'
          f'{allt["wilcoxon"]:>9.4f}{allt["sign"]:>8.4f}{"":>8}')

    sig = [m for (m, t), h in zip(rows, adj) if h < 0.05]
    helped = [m for m, t in rows if t['mean'] < 0]
    print(f'\n  statistically supported per map (Holm < 0.05): '
          f'{", ".join(sig) if sig else "none"}')
    print(f'  descriptively better on: {", ".join(helped) if helped else "none"}  '
          f'(direction only, no test passed on the rest)')
    print(f'  pooled over all {allt["n"]} pairs: {allt["mean"]:+.0f} steps, '
          f'Wilcoxon p={allt["wilcoxon"]:.4f}, sign p={allt["sign"]:.4f}')
    if min(ps) > 0.0019:
        print('  note: at 10 seeds the exact sign test bottoms out at p=0.0020, so a '
              'per-map\n        null result here is weak evidence of no effect, not '
              'evidence of none.')


def table(g, cens, metric):
    names = [n for n in g if len(g[n]) >= 60]
    names.sort(key=lambda n: st.mean(list(g[n].values())))
    print(f'\n{metric}, censored at each run\'s max_steps, mean of 10 seeds per map\n')
    print(f'{"configuration":24}' + ''.join(f'{m[:13]:>14}' for m in MAPS)
          + f'{"ALL":>8}{"fail":>6}')
    for n in names:
        line = f'{n:24}'
        for m in MAPS:
            v = [x for k, x in g[n].items() if k[0] == m]
            line += f'{st.mean(v):>14.0f}' if v else f'{"-":>14}'
        line += f'{st.mean(list(g[n].values())):>8.0f}{cens[n]:>6}'
        print(line)
    print(f'\n  best per map:')
    for m in MAPS:
        best = min(names, key=lambda n: st.mean([x for k, x in g[n].items() if k[0] == m]))
        v = st.mean([x for k, x in g[best].items() if k[0] == m])
        print(f'    {m:22}{best:24}{v:.0f}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('csv')
    p.add_argument('--metric', default='steps_98')
    p.add_argument('--contrast', nargs=2, action='append', metavar=('A', 'B'),
                   help='repeatable; omit for --table only')
    p.add_argument('--table', action='store_true', help='per-map matrix of every config')
    a = p.parse_args()

    g, cens = load(a.csv, a.metric)
    if a.table or not a.contrast:
        table(g, cens, a.metric)
    for x, y in (a.contrast or []):
        for n in (x, y):
            if n not in g:
                raise SystemExit(f'no such configuration: {n!r}\n'
                                 f'available: {" | ".join(sorted(g))}')
        contrast_report(g, x, y, a.metric)


if __name__ == '__main__':
    main()
