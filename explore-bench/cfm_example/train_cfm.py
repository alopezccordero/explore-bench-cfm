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

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f'training on {device}')

torch.manual_seed(args.seed) #manual seed for reproducing the results
d = np.load(args.data) # load data 
cond = torch.tensor(d['cond'], dtype=torch.float32).to(device)  # (N, 5, 64, 64) condition tensor
start = torch.tensor(d['start']).to(device)                     # (N, 2) starting positions of robot
goal = torch.tensor(d['goal']).to(device)          # (N, K, 2) goal position of robot
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
        x0 = start[idx] + NOISE * torch.randn(len(idx), 2, device=device)   # source: around the robot add noise to robot pos
        t = torch.rand(len(idx), 1).to(device)  #generate 256 random numbers from 0 to 1.
        xt = (1 - t) * x0 + t * x1 #position at time t. 

        pred = model(xt, t, cond[idx]) 

        loss = ((pred - (x1 - x0)) ** 2).mean() 
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
