"""E2: does the student still improve with more data, or has it saturated?

Trains the same model on nested subsets of one dataset and reports, for each size, the
endpoint error on held-out examples -- how far the integrated flow lands from the goal the
teacher chose. That number is the offline twin of `mean_snap_cells` in results.csv, which
tracks exploration performance closely: snap 30 went with ~845 steps, snap 13.7 with 397.

Read the last column, not the loss. Training loss falls monotonically by memorising the
training split and says nothing about whether collecting more episodes would pay.
"""
import argparse

import numpy as np
import torch

from cfm_common import NOISE, VelocityField, from_norm

p = argparse.ArgumentParser()
p.add_argument('--data', default='data_cpp.npz')
p.add_argument('--fractions', type=float, nargs='+', default=[0.1, 0.25, 0.5, 1.0])
p.add_argument('--epochs', type=int, default=200)
p.add_argument('--batch', type=int, default=256)
p.add_argument('--lr', type=float, default=1e-3)
p.add_argument('--val', type=float, default=0.2, help='held-out share, fixed across fractions')
p.add_argument('--seed', type=int, default=0)
p.add_argument('--out', default='scaling_curve.csv')
args = p.parse_args()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
d = np.load(args.data)
cond = torch.tensor(d['cond'], dtype=torch.float32)
start = torch.tensor(d['start'])
goal = torch.tensor(d['goal'])[:, 0]
n = len(cond)

# One fixed validation split for every fraction, so the curve compares like with like.
rng = np.random.default_rng(args.seed)
perm = rng.permutation(n)
val, pool = perm[:int(args.val * n)], perm[int(args.val * n):]
print(f'{args.data}: {n} examples -> {len(pool)} train pool, {len(val)} held out, on {device}')


def endpoint_error(model, idx):
    """Cells between where the flow lands and the goal the teacher picked."""
    model.eval()
    out = []
    with torch.no_grad():
        for b in range(0, len(idx), 512):
            i = idx[b:b + 512]
            c, s = cond[i].to(device), start[i].to(device)
            x = s + NOISE * torch.randn(len(i), 2, generator=torch.Generator().manual_seed(0)).to(device)
            for k in range(20):
                x = x + model(x, torch.full((len(i), 1), k / 20, device=device), c) / 20
            out.append(np.hypot(*(from_norm(x.cpu().numpy()) - from_norm(goal[i].numpy())).T))
    model.train()
    return float(np.concatenate(out).mean())


rows = []
for frac in args.fractions:
    sub = pool[:max(args.batch, int(frac * len(pool)))]
    torch.manual_seed(args.seed)
    model = VelocityField().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    for epoch in range(args.epochs):
        order = sub[torch.randperm(len(sub)).numpy()]
        for b in range(0, len(order), args.batch):
            i = order[b:b + args.batch]
            c = cond[i].to(device)
            x1 = goal[i].to(device)
            x0 = start[i].to(device) + NOISE * torch.randn(len(i), 2, device=device)
            t = torch.rand(len(i), 1, device=device)
            loss = ((model((1 - t) * x0 + t * x1, t, c) - (x1 - x0)) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
    tr, va = endpoint_error(model, sub[:len(val)]), endpoint_error(model, val)
    rows.append((len(sub), loss.item(), tr, va))
    print(f'  n={len(sub):6d}  loss {loss.item():.5f}  train err {tr:6.2f}  held-out err {va:6.2f} cells')

with open(args.out, 'w') as f:
    f.write('n_train,final_loss,train_err_cells,heldout_err_cells\n')
    for r in rows:
        f.write(f'{r[0]},{r[1]:.6f},{r[2]:.3f},{r[3]:.3f}\n')

d0, d1 = rows[-2][3], rows[-1][3]
print(f'\nheld-out error over the last doubling: {d0:.2f} -> {d1:.2f} cells '
      f'({100 * (d0 - d1) / max(d0, 1e-9):+.0f}%)')
print('still falling -> collecting more episodes pays; flat -> the limit is the model or '
      'the distribution shift between teacher states and student rollouts, not data volume.')
print(f'wrote {args.out}')
