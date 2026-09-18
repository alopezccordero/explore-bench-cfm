# Conditional flow matching on Explore-Bench Level-0

A minimal example of training a flow-matching goal sampler in the Explore-Bench grid
simulator and comparing it with the benchmark's `cost` method. Nothing in
`../Explore-Bench` is modified.

Run everything from this folder:

```powershell
cd "C:\Users\alope\Desktop\UTRGV\fall 2026\research\explore-bench\cfm_example"

# 1. Collect training data on the 5 training maps (about 15 minutes)
python collect_data.py

# 2. Train (a few minutes on CPU)
python train_cfm.py

# 3. Evaluate on a test map. Same --seed = same start positions for every method.
python run_eval.py --method cfm     --map room --seed 0
python run_eval.py --method teacher --map room --seed 0
python run_eval.py --method cost    --map room --seed 0   # slow: about 1 s per step
```

Each `run_eval.py` call appends one row to `results.csv`.

| File | What it does |
|---|---|
| `cfm_common.py` | Environment wrapper, frontier and distance helpers, teacher, model, sampler |
| `collect_data.py` | Runs the teacher on training maps and saves (map image, robot position, goal samples) |
| `train_cfm.py` | Conditional flow matching training loop |
| `run_eval.py` | Runs `cost`, `teacher` or `cfm` on one map and records team metrics |

Training maps: `corridor_asym`, `corridor_sym`, `room_2`, `room_3`, `room_with_corridor`.
Test maps: the six blueprints (`loop`, `corridor`, `corner`, `room`, `loop_with_corridor`,
`room_with_corner`). The blueprints also appear in the benchmark's own training folder,
so they are excluded from training here.
