"""Shared pieces for the conditional flow matching (CFM) example on Explore-Bench Level-0.

The flow lives in *goal space*: it pushes a point from the robot's position to an
exploration goal (a frontier cell). The robot still drives there with A* through
GridEnv.step_for_cost(), so movement, sensing and metrics are the benchmark's own.

The network and its helpers are in grid_simulator/cfm_policy.py, which GridEnv.py also
uses for `python GridEnv.py cfm ...`, so a trained cfm.pt works in both places.
"""
import contextlib
import io
import os
import sys
import warnings

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, '..', 'Explore-Bench')
sys.path.insert(0, os.path.join(REPO, 'grid_simulator'))

import matplotlib
# Headless by default: GridEnv still draws each step, but no window opens.
# run_eval.py --show sets SHOW_GRID=1 to open the simulator window instead.
if os.environ.get('SHOW_GRID') != '1':
    matplotlib.use('Agg')
warnings.filterwarnings('ignore', message='FigureCanvasAgg is non-interactive')
from GridEnv import GridEnv  # noqa: E402
from cfm_policy import (FREE, NOISE, SIZE, UNKNOWN, WALL, VelocityField,  # noqa: E402,F401
                        build_condition, choose_goal, frontier_mask, from_norm, geodesic_dist,
                        load_model, sample_goals, to_norm)

DATASETS = os.path.join(REPO, 'onpolicy', 'onpolicy', 'envs', 'GridEnv', 'datasets')
BLUEPRINTS = os.path.join(REPO, 'exploration_benchmark', 'blueprints')
# The six blueprints are pixel copies of maps in DATASETS (and room_1 is within
# 238 px of room.pgm), so training uses only maps that are not test maps.
TRAIN_MAPS = ['corridor_asym', 'corridor_sym', 'room_2', 'room_3', 'room_with_corridor']
TEST_MAPS = ['loop', 'corridor', 'corner', 'room', 'loop_with_corridor', 'room_with_corner']

SENSOR_CELLS = 35   # 3.5 m sensor range / 0.1 m cells


# ---------------------------------------------------------------- environment

class GoalEnv(GridEnv):
    """GridEnv that takes goals from goal_fn and keeps each goal until it is used up.

    step_for_cost() gets its goals only from get_goal_for_cost(), so overriding that
    one method swaps the decision-making while everything else stays the benchmark's.
    A goal is replaced when the robot reaches it or it stops being a frontier.
    """

    def __init__(self, *args, goal_fn=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.goal_fn = goal_fn
        self.goals = None
        self.snap_dists = []

    def get_goal_for_cost(self):
        if self.goals is None:
            self.goals = [None] * self.num_agents
        fmask = frontier_mask(self.complete_map)
        for i in range(self.num_agents):
            pos, _ = robot_and_mates(self, i)
            g = self.goals[i]
            if g is None or g == pos or not fmask[g]:
                g = self.goal_fn(self, i, fmask)
                self.goals[i] = pos if g is None else cell(g)
        return np.array(self.goals)


def map_path(name):
    folder = BLUEPRINTS if name in TEST_MAPS else DATASETS
    return os.path.join(folder, name + '.pgm')


def make_env(name, num_agents, goal_fn=None):
    """goal_fn=None gives the original `cost` method."""
    if goal_fn is None:
        env = GridEnv(0.1, 3.5, num_agents, 1000, map_path(name), visualization=True)
    else:
        env = GoalEnv(0.1, 3.5, num_agents, 1000, map_path(name), visualization=True, goal_fn=goal_fn)
    with quiet():
        env.reset_for_traditional()
    return env


@contextlib.contextmanager
def quiet():
    """Hide GridEnv's per-step prints."""
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def coverage(env):
    return np.sum(env.complete_map != UNKNOWN) / env.total_cell_size


def cell(p):
    return (int(p[0]), int(p[1]))


def robot_and_mates(env, i):
    cells = [cell(p) for p in env.agent_pos]
    return cells[i], [c for j, c in enumerate(cells) if j != i]


# ---------------------------------------------------------------- teacher (target distribution)

def teacher_clusters(m, fmask, pos, mates, beta=2.0, min_size=3):
    """Frontier clusters and the teacher's probability of picking each one.

    weight = (cluster size / (walking distance + 1)) ** beta, so big, close frontiers
    are preferred, then discounted near teammates so the robots spread out.
    """
    lab, n = ndimage.label(fmask, structure=np.ones((3, 3)))
    if n == 0:
        return None, None
    ids = np.arange(1, n + 1)
    size = np.asarray(ndimage.sum(fmask, lab, ids))
    near = np.asarray(ndimage.minimum(geodesic_dist(m, pos), lab, ids))
    w = (size / (near + 1.0)) ** beta
    w[(size < min_size) | ~np.isfinite(near)] = 0.0
    if mates:
        centre = np.array(ndimage.center_of_mass(fmask, lab, ids))
        for q in mates:
            d2 = ((centre - np.array(q)) ** 2).sum(1)
            w *= 1.0 - np.exp(-d2 / (2.0 * SENSOR_CELLS ** 2))
    if w.sum() <= 0:  # everything filtered out: any reachable cluster
        w = np.isfinite(near).astype(float)
        if w.sum() <= 0:
            return None, None
    return lab, w / w.sum()


def teacher_sample(m, fmask, pos, mates, k, rng):
    """k goal cells drawn from the teacher distribution, or None if nothing is left."""
    lab, p = teacher_clusters(m, fmask, pos, mates)
    if lab is None:
        return None
    out = []
    for c in rng.choice(len(p), size=k, p=p):
        cells = np.argwhere(lab == c + 1)
        out.append(cells[rng.integers(len(cells))])
    return np.array(out)


def teacher_goal_fn(rng):
    def fn(env, i, fmask):
        pos, mates = robot_and_mates(env, i)
        s = teacher_sample(env.complete_map, fmask, pos, mates, 1, rng)
        return None if s is None else s[0]
    return fn


# ---------------------------------------------------------------- model

def cfm_goal_fn(model, gen=None):
    def fn(env, i, fmask):
        pos, mates = robot_and_mates(env, i)
        goal, snap = choose_goal(model, env.complete_map, pos, mates, gen=gen)
        if goal is not None:
            env.snap_dists.append(snap)  # how far the flow landed from a real frontier cell
        return goal
    return fn
