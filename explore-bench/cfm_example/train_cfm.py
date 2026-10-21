"""Step 2: train v(x, t | map) with conditional flow matching.

For each example: x0 = robot position + small noise, x1 = one teacher goal, and the model
learns the velocity that carries x0 to x1.

The conditional path between them matters. The straight line x_t = (1-t) x0 + t x1 is the
textbook choice, but it assumes the space is convex -- and here it is full of walls. On
data_cpp.npz the segment crosses a wall cell in 63% of examples, and 23% of the average
path is wall or not-known-free, so most of the supervision is at states the robot could
never occupy. The field is then integrated from those states at inference, which is what
the large mean_snap_cells in results.csv is measuring.

So when the dataset carries a `path` array -- the geodesic route through known free space,
stored by collect_data.py --waypoints -- the interpolation follows it and the target is
that route's tangent. Pass --linear to force the straight-line objective on the same data,
which is the controlled comparison for E-A.
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
p.add_argument('--max-arc', type=float, default=0.0,
               help='drop examples whose route is longer than this many cells (0 = all)')
p.add_argument('--linear', action='store_true',
               help='straight-line interpolation even when the data has routes')
args = p.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f'training on {device}')

torch.manual_seed(args.seed) #manual seed for reproducing the results
d = np.load(args.data) # load data

# Optional arc filter, applied in numpy before anything reaches the device, so the big
# condition array is only materialised once.
#
# At K=64 the chords between waypoints are valid for every route under 160 cells, but
# still leave free space on 69.5% of the longer ones (8.2% of data_x4.npz, arcs up to
# 777 cells). Keeping those dilutes the geodesic treatment with examples whose
# interpolation path is no better than a straight line -- which is exactly why the
# earlier K=8 runs found nothing. The filter drops the same examples from both arms, so
# the linear-vs-geodesic comparison stays paired; --max-arc 0 keeps everything.
keep = slice(None)
if args.max_arc > 0 and 'path' in d.files:
    from cfm_common import from_norm
    pc = from_norm(d['path'])
    arc = np.hypot(*(pc[:, 1:] - pc[:, :-1]).transpose(2, 0, 1)).sum(1)
    keep = arc <= args.max_arc
    print(f'arc filter <= {args.max_arc:g} cells: keeping {keep.sum()} of {len(arc)} '
          f'({100 * keep.mean():.1f}%), dropped max arc {arc.max():.0f}')

cond = torch.tensor(d['cond'][keep], dtype=torch.float32).to(device)  # (N, 5, 64, 64) condition tensor
start = torch.tensor(d['start'][keep]).to(device)                     # (N, 2) starting positions of robot
goal = torch.tensor(d['goal'][keep]).to(device)    # (N, K, 2) goal position of robot
path = None
if 'path' in d.files and not args.linear:
    path = torch.tensor(d['path'][keep], dtype=torch.float32).to(device)   # (N, W, 2) route
    print(f'geodesic interpolation along {path.shape[1]} waypoints')
else:
    print('straight-line interpolation' + (' (--linear)' if args.linear else ''))
#n is number of samples (1000), k is goals per sample or (example), 2 is xy coordinate
n, k = goal.shape[:2] #n = samples, k = goals per samples
#k is now 1
print(f'{n} examples, {k} goal samples each')

model = VelocityField().to(device) #initialize neural net, on the same device as the data
opt = torch.optim.Adam(model.parameters(), lr=args.lr) #opt function
for epoch in range(1, args.epochs + 1): #learning loop
    perm = torch.randperm(n).to(device) #train in a randomized order (sapmles) #permutation
    total = 0.0 
    for b in range(0, n, args.batch): #from b=0 to 1000, b+256 each iter
        idx = perm[b:b + args.batch] #store indexes of training examples for current batch
        x1 = goal[idx, 0]        # choose one goal per sample
        eps = NOISE * torch.randn(len(idx), 2, device=device)  # spread of the source
        t = torch.rand(len(idx), 1).to(device)  #generate 256 random numbers from 0 to 1.
        if path is None:
            x0 = start[idx] + eps          # source: around the robot
            xt = (1 - t) * x0 + t * x1     #position at time t.
            target = x1 - x0
        else:
            # Walk the stored route instead of the straight line. With W waypoints at
            # evenly spaced times, t falls in segment j and the conditional velocity is
            # that segment's tangent, scaled by (W-1) because the whole route is covered
            # as t goes 0 -> 1.
            route = path[idx]                                   # (B, W, 2)
            w = route.shape[1]
            u = t.squeeze(1) * (w - 1)
            j = u.long().clamp(max=w - 2)
            frac = (u - j.to(u.dtype)).unsqueeze(1)
            rows = torch.arange(len(idx), device=device)
            a, b2 = route[rows, j], route[rows, j + 1]
            # the (1-t) eps term keeps x0 = route start + noise and x1 = route end, so the
            # source and target distributions are untouched and only the path differs
            xt = a + frac * (b2 - a) + (1 - t) * eps
            target = (w - 1) * (b2 - a) - eps

        pred = model(xt, t, cond[idx])

        loss = ((pred - target) ** 2).mean()
        #x1 - x0 is the displacement. since it goes from t0 to t1 it represents the velocity.
        #calculate the model loss manually - MSE
        #inputs of net

        #current position, current time, conditions (5 X 64 X 64) and output is vx and vy. 
        opt.zero_grad()
        loss.backward()
        opt.step()
        total += loss.item() * len(idx)
    if epoch == 1 or epoch % 10 == 0 or epoch == args.epochs:
        print(f'epoch {epoch:4d}  loss {total / n:.5f}')


# save on the CPU so a checkpoint trained on a GPU node still loads anywhere
torch.save({k: v.cpu() for k, v in model.state_dict().items()}, args.out)
print(f'saved model to {args.out}')
