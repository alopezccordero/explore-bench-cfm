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



torch.manual_seed(args.seed) #manual seed for reproducing the results 
d = np.load(args.data) # load data 
cond = torch.tensor(d['cond'], dtype=torch.float32)  # (N, 5, 64, 64) condition tensor
start = torch.tensor(d['start'])                     # (N, 2) starting positions of robot
goal = torch.tensor(d['goal'])                       # (N, K, 2) goal position of robot
#n is number of samples (1000), k is goals per sample or (example), 2 is xy coordinate
n, k = goal.shape[:2] #n = samples, k = goals per samples
#k is now 1
print(f'{n} examples, {k} goal samples each')

model = VelocityField() #initialize neural net 
opt = torch.optim.Adam(model.parameters(), lr=args.lr) #opt function
for epoch in range(1, args.epochs + 1): #learning loop
    perm = torch.randperm(n) #train in a randomized order (sapmles) #permutation
    total = 0.0 
    for b in range(0, n, args.batch): #from b=0 to 1000, b+256 each iter
        idx = perm[b:b + args.batch] #store indexes of training examples for current batch
        x1 = goal[idx, 0]        # choose one goal per sample    
        x0 = start[idx] + NOISE * torch.randn(len(idx), 2)   # source: around the robot add noise to robot pos
        t = torch.rand(len(idx), 1)  #generate 256 random numbers from 0 to 1.
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


torch.save(model.state_dict(), args.out)
print(f'saved model to {args.out}')
