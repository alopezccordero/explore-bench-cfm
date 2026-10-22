"""Paired analysis of an evaluation grid.

    python analyse.py results_x1.csv [--primary]

Groups runs by the configuration columns run_eval.py now records (ckpt, nsample,
exclude, euler_steps), pairs them by (map, seed), and reports for each contrast the
paired win count, median and mean difference, a 95% interval on the mean difference, an
exact two-sided sign-test p, and a Holm-adjusted p across the family.

Three habits this enforces, each of which already bit this project once:

* Non-completions are charged the run's own max_steps instead of being dropped. Averaging
  only successful runs is how mmpf's 484 came to sit beside teachers averaged over all 18
  when it had never finished room_with_corner on two seeds.
* Configurations come from columns, never from filename or row order. results_eb_sweep.csv
  encoded nsample positionally and one failed run would have shifted every attribution.
* Both the win count and the mean difference are shown. A sign test measures how often a
  method wins, not by how much; a method can win rarely and still be better on average.

With --primary, only the pre-declared comparison is tested, which is the one that does not
need a multiplicity penalty.
"""
import argparse
import collections
import csv
import statistics as st
from math import comb, erf, sqrt

CONFIG = ('ckpt', 'nsample', 'exclude', 'euler_steps')

p = argparse.ArgumentParser()
p.add_argument('csv')
p.add_argument('--primary', action='store_true',
               help='only the declared comparison: exclude 35 vs 0, nsample 1, geodesic')
p.add_argument('--pair', nargs=2, metavar=('A', 'B'),
               help='test exactly this one contrast, naming two configuration labels '
                    'as the summary table prints them')
p.add_argument('--metric', default='steps_98')
args = p.parse_args()

rows = list(csv.DictReader(open(args.csv)))
if not rows:
    raise SystemExit('no rows')


def label(r):
    """Short, unambiguous name. Long labels were truncating the last field away."""
    ck = r.get('ckpt', '').replace('.pt', '').replace('cfm_ea_', '').replace('cfm_', '')
    bits = [ck or r.get('method', '?')]
    for k, tag in (('nsample', 'ns'), ('exclude', 'ex'), ('euler_steps', 'st')):
        v = r.get(k)
        if v not in (None, ''):
            bits.append(f'{tag}{float(v):g}')
    return ' '.join(bits)


def value(r):
    """The metric, with a non-completion charged the full step budget for that run."""
    v = r.get(args.metric)
    if v in (None, '', 'None'):
        return float(r.get('max_steps') or 2000), True
    return float(v), False


groups = collections.defaultdict(dict)
for r in rows:
    groups[label(r)][(r['map'], r['seed'])] = value(r)

print(f'{args.csv}: {len(rows)} runs, {len(groups)} configurations\n')
print(f"{'configuration':30s}{'n':>4}{'mean':>7}{'cens':>7}{'fail':>5}")
for name, d in sorted(groups.items()):
    done = [v for v, c in d.values() if not c]
    cens = [v for v, _ in d.values()]
    nf = sum(1 for _, c in d.values() if c)
    avg = f'{st.mean(done):.0f}' if done else '-'
    print(f'{name:30.30s}{len(d):>4}{avg:>7}{st.mean(cens):>7.0f}{nf:>5}')


def Phi(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def contrast(a, b):
    """b minus a, paired on the keys both share. Negative means b is better."""
    ks = sorted(set(groups[a]) & set(groups[b]))
    d = [groups[b][k][0] - groups[a][k][0] for k in ks]
    w = sum(1 for x in d if x < 0)
    l = sum(1 for x in d if x > 0)
    n = w + l
    pv = (sum(comb(n, i) for i in range(min(w, l) + 1)) / 2 ** n * 2) if n else 1.0
    mu, sd = st.mean(d), (st.pstdev(d) if len(d) > 1 else 0.0)
    se = sd / sqrt(len(d)) if d else 0.0
    return dict(n=len(d), wins=w, of=n, median=st.median(d), mean=mu,
                lo=mu - 1.96 * se, hi=mu + 1.96 * se, p=min(pv, 1.0))


def show(pairs, adjust):
    out = []
    for a, b in pairs:
        if a in groups and b in groups:
            out.append((contrast(a, b), a, b))
    if not out:
        print('\nno comparable pairs found'); return
    print(f"\n{'contrast: B vs A (negative mean = B better)':60s}{'wins':>8}{'mean':>7}"
          f"{'95% CI':>18}{'p':>8}" + (f"{'Holm':>7}" if adjust else ''))
    for c, a, b in sorted(out, key=lambda t: t[0]['p']):
        holm = ''
        if adjust:
            rank = sorted(x[0]['p'] for x in out).index(c['p'])
            holm = f"{min(c['p'] * (len(out) - rank), 1.0):>7.3f}"
        note = '' if c['of'] else '   (no decisive runs: all paired diffs zero)'
        print(f'{b + "  vs  " + a:60.60s}{c["wins"]:>5}/{c["of"]:<2}{c["mean"]:>7.0f}'
              f'  [{c["lo"]:>6.0f},{c["hi"]:>6.0f}]{c["p"]:>8.4f}{holm}{note}')


keys = sorted(groups)
if args.pair:
    missing = [k for k in args.pair if k not in groups]
    if missing:
        raise SystemExit('no such configuration: ' + '; '.join(missing)
                         + '\navailable: ' + ' | '.join(keys))
    print('\n=== single declared contrast (no multiplicity penalty) ===')
    show([tuple(args.pair)], adjust=False)
elif args.primary:
    a = [k for k in keys if k.split()[0].endswith('geodesic')
         and k.split()[1:] == ['ns1', 'ex0', 'st20']]
    b = [k for k in keys if k.split()[0].endswith('geodesic')
         and k.split()[1:] == ['ns1', 'ex35', 'st20']]
    if a and b:
        print('\n=== PRIMARY (declared before running; no multiplicity penalty) ===')
        show([(a[0], b[0])], adjust=False)
    else:
        print('\nprimary pair not present in this file')
else:
    print('\n=== all contrasts differing in exactly one setting ===')
    # Contrast any two configurations differing in exactly one field, the checkpoint
    # included. The old rule demanded a shared ckpt, which silently dropped the one
    # comparison X5 exists to make -- linear vs geodesic on the same data -- and printed
    # 'no comparable pairs found' rather than saying why.
    pairs = [(a, b) for i, a in enumerate(keys) for b in keys[i + 1:]
             if len(a.split()) == len(b.split())
             and sum(x != y for x, y in zip(a.split(), b.split())) == 1]
    show(pairs, adjust=True)
    print('\nHolm is across the contrasts printed here. The pre-declared primary '
          'comparison is exempt; run with --primary for it alone.')
