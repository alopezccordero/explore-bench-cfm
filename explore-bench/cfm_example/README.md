# Conditional flow matching on Explore-Bench Level-0

A minimal example of training a flow-matching goal sampler in the Explore-Bench grid
simulator and comparing it with the benchmark's `cost` method. Nothing in
`../Explore-Bench` is modified.

Run everything from this folder:

```powershell
cd "C:\Users\alope\Desktop\UTRGV\fall 2026\research\explore-bench\cfm_example"

# 1. Collect training data on the 5 training maps (about 15 minutes)
python collect_data.py --method mmpf       # or cost, mtsp, milp_cpp

# 2. Train (a few minutes on CPU)
python train_cfm.py

# 3. Evaluate on a test map. Same --seed = same start positions for every method.
python run_eval.py --method cfm      --map room --seed 0
python run_eval.py --method teacher  --map room --seed 0
python run_eval.py --method cost     --map room --seed 0   # the benchmark's cost method
python run_eval.py --method mmpf     --map room --seed 0   # the benchmark's potential-field method
python run_eval.py --method mtsp     --map room --seed 0   # privileged, upper bound
python run_eval.py --method milp_cpp --map room --seed 0   # privileged, upper bound
```

Each `run_eval.py` call appends one row to `results.csv`.

## Teachers

`--method` picks who generates the goals. The first two see only the robots' own partial
map; the last two cheat.

| Method | Sees | What it solves |
|---|---|---|
| `mmpf` | partial map | GridEnv's potential field |
| `cost` | partial map | GridEnv's nearest frontier cluster |
| `mtsp` | **ground truth** | multi-depot open mTSP / VRP over the frontier clusters, exact MILP |
| `milp_cpp` | **ground truth** | coverage path planning as a min-cost viewpoint set cover, exact MILP |

`mtsp` and `milp_cpp` live in `cfm_teachers.py`. Both take their travel costs from A*
(`Astar.AStar`, the benchmark's own planner) run on `env.gt_map`, so a corridor that is
still unexplored is free to walk through, and both score a candidate goal with the
simulator's real sensor model, so they know exactly how much unknown area it will reveal.
Both are solved with HiGHS through `scipy.optimize.milp` — no extra dependency.

The point is the asymmetry. Whatever the teacher used to decide, the example written to
`data.npz` is still `build_condition(...)` of the **partial** team map, so the flow model
is trained to reproduce a decision it could not have computed from its own input, and at
evaluation time has to reproduce it without the ground truth. That is the privileged /
learning-by-cheating setup: use `mtsp` or `milp_cpp` rows in `results.csv` as the ceiling
the student is chasing, not as a baseline it should match.

Goals are chosen on `frontier_mask` (free cells touching unknown) — the same support the
student samples on — so for these two the snap-to-frontier distance is 0.

Knobs (both scripts): `--max-nodes` frontier clusters kept as MILP nodes, ranked by true
information gain; `--replan N` to re-solve every N steps as well as when a robot uses up
its goal; `--goal-tol` how far a goal may recede with its frontier before the MILP is
re-solved; `--cpp-balance` the weight of the makespan term in `milp_cpp`.

### Measured, `--robots 2 --seed 0`

| map | method | steps to 90% | steps to 98% | total path | overlap |
|---|---|---|---|---|---|
| room | cost | 428 | 460 | 920 | 0.423 |
| room | mmpf | 352 | 405 | 810 | 0.249 |
| room | `mtsp` | 358 | 406 | 812 | 0.173 |
| room | `milp_cpp` | **301** | **351** | **702** | 0.100 |
| corner | cost | 776 | 1287 | 2574 | 0.999 |
| corner | mmpf | 600 | 1046 | 1052 | **0.041** |
| corner | `mtsp` | 373 | 605 | 1210 | 0.408 |
| corner | `milp_cpp` | 373 | **516** | 1032 | 0.172 |

The margin is small on `room` and roughly 2x on `corner`, so the privileged teachers are
worth imitating mainly where coordination matters. `milp_cpp` beats `mtsp` on both maps:
mTSP minimises travel over clusters it has already been handed, and only sees information
gain through the `--max-nodes` pre-filter, whereas the set cover optimises coverage itself.

`--replan` matters more than it looks (`mtsp` / `milp_cpp` steps to 98% on `room`):
`1` -> 414 / 367 but 3-4x the wall clock, `10` -> **406** / **351**, `25` -> 442 / 385.
10 is the default: a plan built on a 25-step-old map aims at stale frontiers, and solving
every step costs far more time than it saves.

| File | What it does |
|---|---|
| `cfm_common.py` | Environment wrapper, frontier and distance helpers, sampling teacher, model, sampler |
| `cfm_teachers.py` | The two privileged MILP teachers (`mtsp`, `milp_cpp`) |
| `collect_data.py` | Runs a teacher on training maps and saves (map image, robot position, goal samples) |
| `train_cfm.py` | Conditional flow matching training loop |
| `run_eval.py` | Runs one method on one map and records team metrics |

Training maps: `corridor_asym`, `corridor_sym`, `room_2`, `room_3`, `room_with_corridor`.
Test maps: the six blueprints (`loop`, `corridor`, `corner`, `room`, `loop_with_corridor`,
`room_with_corner`). The blueprints also appear in the benchmark's own training folder,
so they are excluded from training here.
