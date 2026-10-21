"""Verify the raw A* routes in a collected dataset.

    python verify_routes.py data_x4.npz

Checks, in order of how badly a failure would matter:

1. CSR integrity     -- offsets/lengths index raw_path exactly, no gaps or overlaps
2. Endpoints         -- every route starts at `start` and ends at `goal`
3. Connectivity      -- consecutive cells are 4-neighbours, so the route is walkable
4. Free space        -- every route cell is free on the ground-truth map
5. Resample fidelity -- re-resampling the raw route reproduces the stored `path`
6. Chord validity    -- for several K, how often the straight segments *between*
                        waypoints leave free space

Check 6 is the one that matters for training. `train_cfm.py` interpolates linearly between
stored waypoints, so a route can be perfectly valid cell-by-cell while the chords the
trainer actually samples cut through walls. In data_x3.npz (K=8) that happened on 27.8% of
examples -- barely better than the 31.6% of plain straight lines it was meant to replace,
which is why the geodesic result never reproduced. With raw_path on disk this is measurable
for any K without re-collecting, and K becomes a training-time choice.
"""
import sys

import numpy as np
from PIL import Image

from cfm_common import FREE, from_norm, map_path, to_norm

STEP4 = {(1, 0), (-1, 0), (0, 1), (0, -1)}


def resample(path, k):
    """Same arc-length resampling collect_data.py uses, so check 5 is a real comparison."""
    p = np.asarray(path, float)
    if len(p) < 2:
        return np.repeat(p.reshape(1, 2), k, axis=0)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*(p[1:] - p[:-1]).T))])
    at = np.linspace(0.0, s[-1], k)
    return np.stack([np.interp(at, s, p[:, 0]), np.interp(at, s, p[:, 1])], axis=1)


def chord_leaves_free(pts, free):
    """Does any straight segment between consecutive waypoints leave free space?"""
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(int(np.hypot(*(b - a))) * 2, 2)
        q = np.rint(a + np.linspace(0, 1, n)[:, None] * (b - a)).astype(int)
        if not free[q[:, 0], q[:, 1]].all():
            return True
    return False


def main(path):
    d = np.load(path, allow_pickle=True)
    need = ('raw_path', 'raw_path_offsets', 'raw_path_lengths')
    missing = [k for k in need if k not in d.files]
    if missing:
        print(f'FAIL  {path} has no raw routes (missing {", ".join(missing)}).')
        print('      Re-collect with a collect_data.py that stores them.')
        return 1

    raw, off, ln = d['raw_path'], d['raw_path_offsets'], d['raw_path_lengths']
    start, goal, stored = d['start'], d['goal'][:, 0], d.get('path')
    n = len(start)
    fails = []
    print(f'{path}: {n} examples, {len(raw)} route cells '
          f'({raw.nbytes / 1e6:.1f} MB), K={stored.shape[1] if stored is not None else "-"}')

    # 1. CSR integrity
    ok = (len(off) == n and len(ln) == n
          and bool((off[1:] == off[:-1] + ln[:-1]).all())
          and int(off[-1] + ln[-1]) == len(raw) and int(off[0]) == 0)
    print(f'1. CSR integrity          {"OK" if ok else "FAIL"}  '
          f'lengths min {ln.min()} mean {ln.mean():.0f} max {ln.max()}')
    if not ok:
        fails.append('csr')

    routes = [raw[off[i]:off[i] + ln[i]].astype(int) for i in range(n)]

    # 2. endpoints
    s_cells, g_cells = from_norm(start), from_norm(goal)
    bad_s = sum(1 for i, r in enumerate(routes) if not (r[0] == s_cells[i]).all())
    bad_g = sum(1 for i, r in enumerate(routes) if not (r[-1] == g_cells[i]).all())
    print(f'2. endpoints              {"OK" if not (bad_s or bad_g) else "FAIL"}  '
          f'{bad_s} start mismatches, {bad_g} goal mismatches')
    if bad_s or bad_g:
        fails.append('endpoints')

    # 3. 4-connectivity
    bad_c = 0
    for r in routes:
        if len(r) > 1:
            d4 = np.diff(r, axis=0)
            if not all(tuple(x) in STEP4 for x in d4):
                bad_c += 1
    print(f'3. 4-connectivity         {"OK" if not bad_c else "FAIL"}  '
          f'{bad_c} routes with a non-adjacent step')
    if bad_c:
        fails.append('connectivity')

    # map each example to its map, through its episode
    names = list(d['map_names'])
    ep = d['episodes']
    ep_map = {int(r[0]): int(r[1]) for r in ep}
    emap = np.array([ep_map[int(e)] for e in d['meta'][:, 0]])
    frees = {mi: (np.array(Image.open(map_path(nm))) == FREE) for mi, nm in enumerate(names)}

    # 4. every route cell is free on the ground truth
    bad_f = 0
    for i, r in enumerate(routes):
        f = frees[emap[i]]
        if not f[r[:, 0], r[:, 1]].all():
            bad_f += 1
    print(f'4. cells in free space    {"OK" if not bad_f else "FAIL"}  '
          f'{bad_f} routes touch a non-free cell')
    if bad_f:
        fails.append('freespace')

    # 5. the stored waypoints are what resampling the raw route gives
    if stored is not None:
        k = stored.shape[1]
        err = max(float(np.abs(to_norm(resample(r, k)) - stored[i]).max())
                  for i, r in enumerate(routes))
        ok5 = err < 1e-4
        print(f'5. resample fidelity      {"OK" if ok5 else "FAIL"}  '
              f'max deviation {err:.2e} (normalised units)')
        if not ok5:
            fails.append('resample')

    # 6. chord validity across K -- the number that matters for training
    arc = np.array([np.hypot(*np.diff(r, axis=0).T).sum() if len(r) > 1 else 0.0
                    for r in routes])
    print('\n6. chord validity: share of examples where a segment between waypoints '
          'leaves free space')
    ks = [8, 16, 32, 64, 128]
    if stored is not None and stored.shape[1] not in ks:
        ks.append(int(stored.shape[1]))
    print(f'   {"K":>5}{"spacing":>10}{"invalid":>9}   by route length '
          f'(<40 / 40-80 / 80-160 / 160+)')
    buckets = [(0, 40), (40, 80), (80, 160), (160, 10 ** 9)]
    for k in sorted(ks):
        flags = np.array([chord_leaves_free(resample(r, k), frees[emap[i]])
                          for i, r in enumerate(routes)])
        per = ' / '.join(
            f'{100 * flags[(arc >= lo) & (arc < hi)].mean():4.1f}%'
            if ((arc >= lo) & (arc < hi)).any() else '   - '
            for lo, hi in buckets)
        print(f'   {k:>5}{arc.mean() / max(k - 1, 1):>9.1f}c{100 * flags.mean():>8.1f}%   {per}')

    # the straight line, for contrast: this is what the objective used before
    lin = np.array([chord_leaves_free(np.stack([s_cells[i], g_cells[i]]).astype(float),
                                      frees[emap[i]]) for i in range(n)])
    print(f'   {"line":>5}{"-":>10}{100 * lin.mean():>8.1f}%   (straight start->goal, '
          f'the pre-geodesic objective)')

    print(f'\narc length: mean {arc.mean():.1f}  median {np.median(arc):.1f}  '
          f'max {arc.max():.1f} cells;  {100 * (arc > 160).mean():.1f}% exceed 160 cells')
    print('\n' + ('VERIFICATION PASSED' if not fails
                  else 'VERIFICATION FAILED: ' + ', '.join(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'data_x4.npz'))
