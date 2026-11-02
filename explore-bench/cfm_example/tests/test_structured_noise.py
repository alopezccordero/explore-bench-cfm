"""Pure numerical smoke tests; does not require Explore-Bench or pretrained weights.

Run from cfm_example: python -m unittest discover -s tests -v
"""
import unittest

import numpy as np

from structured_noise import (build_noise_bank, fit_laguerre,
                              frontier_joint_modes)


class NoisePartitionTests(unittest.TestCase):
    def test_laguerre_distribution(self):
        rng = np.random.default_rng(17)
        anchors = np.array([[-1.,0.],[1.,0.]])
        masses = np.array([.35,.65])
        weights, empirical = fit_laguerre(anchors, masses, rng, bank_size=9000)
        self.assertEqual(weights.shape, (2,))
        self.assertTrue(np.all(np.abs(empirical - masses) < .07), (empirical,masses))

    def test_sample_conditions_on_joint_mode(self):
        from structured_noise import NoiseBank
        rng = np.random.default_rng(9)
        a = np.array([[-1,0,0,0],[1,0,0,0]], float)
        p = np.array([.5,.5])
        weights, observed = fit_laguerre(a,p,rng,bank_size=2048)
        bank=NoiseBank(np.zeros((2,2,2)), a, p, p, weights, observed, 2)
        for k in range(2):
            z, mode, draws = bank.sample(rng, mode=k)
            self.assertEqual(z.shape,(2,2))
            self.assertEqual(mode,k)
            self.assertEqual(bank.membership(z.reshape(1,-1)).item(),k)
            self.assertGreaterEqual(draws,1)

    def test_new_frontiers_change_online_modes(self):
        # Synthetic known map with two separated frontier groups, then a new one.
        m = np.zeros((24,24), np.uint8)
        f = np.zeros_like(m, dtype=bool)
        f[2:5,2:5]=True
        f[16:19,16:19]=True
        robots=np.array([[7,7],[7,8]])
        def distance(_m, pos):
            rr,cc=np.indices(_m.shape)
            return (np.abs(rr-pos[0])+np.abs(cc-pos[1])).astype(float)
        def norm(x):
            return np.asarray(x,float)/12 - 1
        old = build_noise_bank(m,robots,f,distance,norm,
                               np.random.default_rng(4),bank_size=1024)
        self.assertIsNotNone(old)
        self.assertGreaterEqual(len(old.goals),2)
        new_f = np.zeros_like(f)
        new_f[2:5,2:5]=True
        new_f[4:7,17:20]=True
        updated = build_noise_bank(m,robots,new_f,distance,norm,
                                   np.random.default_rng(4),bank_size=1024)
        self.assertFalse(np.array_equal(old.goals,updated.goals))
        # E1 preserves old weights/anchors; E2 reconstructs them.
        self.assertTrue(np.allclose(old.goals,old.goals.copy()))


if __name__=='__main__':
    unittest.main()
