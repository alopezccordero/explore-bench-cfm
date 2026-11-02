"""State-dependent joint noise cells for exploratory CFM sampling experiments.

This is *not* a trained MoSDOT implementation. It constructs approximate Laguerre
cells in joint Gaussian epsilon space from observable frontier-cluster proposals.
The existing, independently trained per-robot CFM samples each epsilon slice;
there is no guarantee that a slice produces its nominal frontier mode.

The only difference between E1 and E2 should be the update schedule of the bank:
  E1: a bank is made at initial observation and held for the entire episode.
  E2: a bank is rebuilt from the observed map at each joint replan.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
from scipy import ndimage
from scipy.optimize import minimize
from scipy.special import logsumexp, softmax


@dataclass
class NoiseBank:
    # Shape: (K, N, 2) goals and (K, 2*N) normalized Gaussian-space anchors.
    goals: np.ndarray
    anchors: np.ndarray
    probabilities: np.ndarray  # selection distribution (often utility-biased)
    capacities: np.ndarray  # Gaussian-mass quotas for OT cells (uniform in this pilot)
    laguerre_weights: np.ndarray
    observed_mass: np.ndarray
    frontier_count: int

    def membership(self, z: np.ndarray) -> np.ndarray:
        """Laguerre cells: argmin_k ||z - anchor_k||^2 - weight_k."""
        z = np.asarray(z, dtype=float).reshape(-1, self.anchors.shape[1])
        scores = 2.0 * z @ self.anchors.T - (self.anchors ** 2).sum(axis=1)
        scores = scores + self.laguerre_weights[None, :]
        return np.argmax(scores, axis=1)

    def sample(self, rng: np.random.Generator, *, mode=None,
               max_draws=10000) -> tuple[np.ndarray, int, int]:
        """Rejection sample a Gaussian *joint* epsilon in the requested cell.

        The chosen mode is drawn using the bank's planned capacities if omitted.
        Returns (epsilon[N,2], mode_index, number_of_noise_draws).
        """
        if mode is None:
            mode = int(rng.choice(len(self.probabilities), p=self.probabilities))
        n = self.anchors.shape[1] // 2
        if len(self.probabilities) == 1:
            return rng.normal(size=(n, 2)).astype(np.float32), mode, 1
        draws = 0
        while draws < max_draws:
            batch = min(128, max_draws - draws)
            pool = rng.normal(size=(batch, 2*n))
            membership = self.membership(pool)
            draws += batch
            choices = np.flatnonzero(membership == mode)
            if len(choices):
                return pool[choices[0]].reshape(n, 2).astype(np.float32), mode, draws
        raise RuntimeError(f'No samples found for Laguerre mode {mode} after {draws} draws')


def fit_laguerre(anchors: np.ndarray, masses: np.ndarray, rng,
                 bank_size=4096, temperature=0.075) -> tuple[np.ndarray,np.ndarray]:
    """Approximate semi-discrete OT Gaussian cells by Monte-Carlo dual fitting.

    Uses smoothed Laguerre assignments during optimization and hard assignments
    at sampling time. Does NOT claim exact OT capacities, which are recorded.
    """
    anchors = np.asarray(anchors, float)
    masses = np.asarray(masses, float)
    k, dimension = anchors.shape
    if k == 1:
        return np.zeros(1), np.ones(1)
    pool = rng.normal(size=(bank_size, dimension))
    base = 2.0 * pool @ anchors.T - np.sum(anchors**2, axis=1)

    def objective(w):
        vals = (base + w[None, :]) / temperature
        probs = softmax(vals, axis=1)
        val = (temperature * np.mean(logsumexp(vals, axis=1))
               - np.dot(masses, w))
        grad = np.mean(probs, axis=0) - masses
        return float(val), grad

    opt = minimize(objective, np.zeros(k), jac=True, method='L-BFGS-B',
                   options={'maxiter': 150, 'ftol': 1e-10})
    weights = np.asarray(opt.x) - float(np.mean(opt.x))
    observed = np.bincount(np.argmax(base + weights[None, :], axis=1),
                           minlength=k).astype(float) / bank_size
    return weights, observed


def frontier_joint_modes(m: np.ndarray, positions: np.ndarray,
                         fmask: np.ndarray, distance_fn, *, max_clusters=6,
                         max_modes=12, min_cluster=3):
    """Build feasible joint frontier prototypes WITHOUT using ground truth.

    distance_fn(map, position)->grid distance field. Cluster representatives
    are the nearest reachable cells to each robot, not oracle future viewpoints.
    Returns (K,N,2) goal prototypes, unnormalized positive utility weights,
    total frontier cluster count. Modes prefer different clusters when possible.
    """
    labels, count = ndimage.label(fmask, np.ones((3,3), dtype=np.uint8))
    n = len(positions)
    if count == 0:
        return np.empty((0,n,2), np.int32), np.empty(0), 0
    clusters = []
    for lab in range(1, count + 1):
        pts = np.argwhere(labels == lab)
        if len(pts) >= min_cluster:
            clusters.append(pts)
    if not clusters:
        clusters = [np.argwhere(labels == lab) for lab in range(1, count+1)]
    clusters.sort(key=len, reverse=True)
    clusters = clusters[:max_clusters]
    distances = [distance_fn(m, tuple(map(int, pos))) for pos in positions]
    # A frontier's representative is robot-dependent; exclude unreachable assignments.
    reps = np.zeros((n, len(clusters), 2), np.int32)
    utilities = np.zeros((n, len(clusters)), float)
    for i, dist in enumerate(distances):
        for j, points in enumerate(clusters):
            d = dist[points[:,0], points[:,1]]
            valid = np.flatnonzero(np.isfinite(d))
            if not len(valid):
                continue
            b = valid[np.argmin(d[valid])]
            reps[i,j] = points[b]
            utilities[i,j] = len(points) / ((1.0 + d[b]) ** 2)
    # Enumerate only modest candidate sets. Unique frontier assignment when possible.
    assignments = []
    for assignment in product(range(len(clusters)), repeat=n):
        if len(clusters) >= n and len(set(assignment)) != n:
            continue
        score = 0.0
        goals = []
        valid = True
        for i,j in enumerate(assignment):
            if utilities[i,j] <= 0:
                valid = False
                break
            score += np.log(utilities[i,j] + 1e-12)
            goals.append(reps[i,j])
        if valid:
            if len(set(assignment)) < n:
                score -= 2.0 * (n - len(set(assignment)))
            assignments.append((score, np.stack(goals)))
    assignments.sort(key=lambda a: a[0], reverse=True)
    assignments = assignments[:max_modes]
    if not assignments:
        return np.empty((0,n,2), np.int32), np.empty(0), count
    scores = np.array([a[0] for a in assignments])
    # Avoid mode collapse: modestly temper utility scores and retain positive capacities.
    masses = softmax((scores - scores.max()) / max(1.0, float(n)))
    masses = 0.05 / len(scores) + .95 * masses
    return np.stack([a[1] for a in assignments]), masses, count


def build_noise_bank(m, positions, fmask, distance_fn, to_norm_fn,
                     rng, *, max_clusters=6, max_modes=12, bank_size=4096):
    goals, masses, count = frontier_joint_modes(
        m, positions, fmask, distance_fn,
        max_clusters=max_clusters, max_modes=max_modes)
    if len(goals) == 0:
        return None
    pos = np.asarray(positions, dtype=float)
    # Anchors are DIRECTIONS in the normalized CFM source epsilon coordinates,
    # not actual physical end positions and not learned mode supports.
    directions = to_norm_fn(goals.astype(float)) - to_norm_fn(pos[None,:,:])
    norm = np.linalg.norm(directions, axis=2, keepdims=True)
    anchor = (directions / np.maximum(norm, 1e-6)).reshape(len(goals), -1)
    # IMPORTANT: selecting modes with exactly their Gaussian cell capacities would
    # reconstruct the original Gaussian marginal. That would make the intervention
    # a null test of noise partitioning. Use equal-mass cells but select useful
    # joint modes according to a *different* distribution (utility-based), thereby
    # changing which portions of the Gaussian are sampled.
    capacities = np.full(len(goals), 1.0/len(goals))
    weights, observed = fit_laguerre(anchor, capacities, rng, bank_size=bank_size)
    return NoiseBank(goals, anchor, masses, capacities, weights, observed, count)
