"""Paired T95 evaluation with map-cluster bootstrap for structured-noise experiments.

Primary (predeclared): online vs static. Secondary: static vs independent.
Fails count at the cap, and failures are always reported. No claimed
significance if map/seed matching is incomplete; no hidden dropped runs.
"""
import argparse
import collections
import csv
import random
import statistics

p=argparse.ArgumentParser()
p.add_argument('csv')
p.add_argument('--bootstrap', type=int, default=5000)
p.add_argument('--seed', type=int, default=2026)
a=p.parse_args()
rows=list(csv.DictReader(open(a.csv,newline='')))
by_variant=collections.defaultdict(dict)
configs={}
for r in rows:
    variant=r['variant']; key=(r['map'],int(r['seed']))
    cfg=tuple(r[k] for k in ('robots','ckpt','replan_period','flow_steps',
                            'bank_size','exclusion_cells','step_seconds'))
    if variant in configs and configs[variant]!=cfg:
        raise SystemExit(f'mismatched config within {variant}: {cfg}')
    configs[variant]=cfg
    if key in by_variant[variant]:
        raise SystemExit(f'duplicate run: {variant}, {key}')
    by_variant[variant][key]=r
if len(set(configs.values()))!=1:
    raise SystemExit(f'Variants do not share settings: {configs}')

for method in sorted(by_variant):
    r=list(by_variant[method].values())
    values=[float(x['time_to_95_percent_coverage']) for x in r]
    fail=sum(int(x['capped']) for x in r)
    print(f'{method:14} n={len(r):3} mean capped T95={statistics.mean(values):8.2f} '
          f'failures={fail} mean planning s={statistics.mean(float(x["planning_seconds"]) for x in r):.2f}')


def contrast(better, reference):
    A=by_variant.get(reference,{})
    B=by_variant.get(better,{})
    common=sorted(set(A)&set(B))
    if not common:
        print(f'{better} vs {reference}: NO PAIRED RESULTS')
        return
    if len(common)!=len(A) or len(common)!=len(B):
        print(f'WARNING: only {len(common)} matched runs; unmatched runs ignored for contrast')
    diffs={k:float(B[k]['time_to_95_percent_coverage'])-
             float(A[k]['time_to_95_percent_coverage']) for k in common}
    values=list(diffs.values())
    maps=sorted(set(m for m,s in common))
    permap={m:[x for (mm,s),x in diffs.items() if mm==m] for m in maps}
    rng=random.Random(a.seed)
    boot=[]
    for _ in range(a.bootstrap):
        chosen=[rng.choice(maps) for _ in maps]
        values_b=[]
        for m in chosen:
            values_b += [rng.choice(permap[m]) for _ in permap[m]]
        boot.append(statistics.mean(values_b))
    boot.sort()
    lo=boot[int(.025*(len(boot)-1))]
    hi=boot[int(.975*(len(boot)-1))]
    print(f'\n{better} - {reference} (negative = {better} faster)')
    print(f'paired n={len(common)}, maps={len(maps)}; '
          f'mean ΔT95={statistics.mean(values):.2f} s, '
          f'cluster bootstrap 95% interval [{lo:.2f}, {hi:.2f}]')
    for m in maps:
        print(f'  {m:22} n={len(permap[m]):2} mean Δ={statistics.mean(permap[m]):8.2f}')
    return

contrast('online','static')  # single primary contrast
contrast('static','independent')  # secondary feasibility contrast
