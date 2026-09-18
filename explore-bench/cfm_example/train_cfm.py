"""Step 2: train v(x, t | map) with conditional flow matching.

For each example: x0 = robot position + small noise, x1 = one teacher goal,
x_t = (1 - t) x0 + t x1, and the model learns to predict the velocity x1 - x0.
"""
import argparse

import numpy as np
import torch

from cfm_common import NOISE, VelocityField

p = argparse.ArgumentParser()
p.add_argument('--data', default='data.npz')
p.add_argument('--epochs', type=int, default=200)
p.add_argument('--batch', type=int, default=256)
p.add_argument('--lr', type=float, default=1e-3)
p.add_argument('--seed', type=int, default=0)
p.add_argument('--out', default='cfm.pt')
args = p.parse_args()

torch.manual_seed(args.seed)
d = np.load(args.data)
cond = torch.tensor(d['cond'], dtype=torch.float32)  # (N, 5, 64, 64)
start = torch.tensor(d['start'])                     # (N, 2)
goal = torch.tensor(d['goal'])                       # (N, K, 2)
n, k = goal.shape[:2]
print(f'{n} examples, {k} goal samples each')

model = VelocityField()
opt = torch.optim.Adam(model.parameters(), lr=args.lr)
for epoch in range(1, args.epochs + 1):
    perm = torch.randperm(n)
    total = 0.0
    for b in range(0, n, args.batch):
        idx = perm[b:b + args.batch]
        x1 = goal[idx, torch.randint(k, (len(idx),))]        # one teacher goal per example
        x0 = start[idx] + NOISE * torch.randn(len(idx), 2)   # source: around the robot
        t = torch.rand(len(idx), 1)
        xt = (1 - t) * x0 + t * x1
        loss = ((model(xt, t, cond[idx]) - (x1 - x0)) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
        total += loss.item() * len(idx)
    if epoch == 1 or epoch % 10 == 0 or epoch == args.epochs:
        print(f'epoch {epoch:4d}  loss {total / n:.5f}')

torch.save(model.state_dict(), args.out)
print(f'saved model to {args.out}')
