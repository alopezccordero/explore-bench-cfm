"""Planner schedule test with a mock CFM + mock map. Not a benchmark smoke test."""
import contextlib
import importlib
import sys
import types
import unittest

import numpy as np
import torch


class PlannerScheduleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake=types.ModuleType('cfm_common')
        fake.GoalEnv=object
        fake.NOISE=.10
        fake.UNKNOWN=0
        fake.VelocityField=object
        fake.build_condition=lambda m,pos,mates:np.zeros((5,64,64),np.float32)
        fake.cell=lambda x:tuple(int(y) for y in x)
        fake.coverage=lambda env:0
        fake.frontier_mask=lambda m:m.astype(bool)
        fake.from_norm=lambda x:np.asarray(x)*24
        fake.to_norm=lambda x:np.asarray(x)/24
        fake.map_path=lambda name:name
        fake.quiet=contextlib.nullcontext
        def dist(m, pos):
            y,x=np.indices(m.shape)
            return np.abs(y-pos[0])+np.abs(x-pos[1])
        fake.geodesic_dist=dist
        cls.old=sys.modules.get('cfm_common')
        sys.modules['cfm_common']=fake
        cls.mod=importlib.import_module('run_noise_experiment')

    @classmethod
    def tearDownClass(cls):
        if cls.old is None:
            sys.modules.pop('cfm_common',None)
        else:
            sys.modules['cfm_common']=cls.old
        sys.modules.pop('run_noise_experiment',None)

    def test_static_bank_stays_frozen_but_online_updates(self):
        class Env:
            def __init__(self):
                self.agent_pos=np.array([[7,7],[8,7]])
                self.complete_map=np.zeros((24,24),np.uint8)
                self.complete_map[2:5,2:5]=1
                self.complete_map[15:18,17:20]=1
        class Model:
            def __call__(self,x,t,cond):
                return torch.zeros_like(x)
        e1=Env();e2=Env()
        opts=dict(seed=101,flow_steps=1,bank_size=512,max_clusters=6,
                  max_modes=6,exclusion=0)
        static=self.mod.NoisePlanner(Model(),variant='static',**opts)
        online=self.mod.NoisePlanner(Model(),variant='online',**opts)
        static.initialize(e1);online.initialize(e2)
        self.assertEqual(static.bank_builds,1)
        self.assertEqual(online.bank_builds,0)
        for env in [e1,e2]:
            env.complete_map[15:18,17:20]=0
            env.complete_map[3:6,18:21]=1
        static.plan(e1,e1.complete_map.astype(bool))
        online.plan(e2,e2.complete_map.astype(bool))
        self.assertEqual(static.bank_builds,1)
        self.assertEqual(online.bank_builds,1)
        online.plan(e2,e2.complete_map.astype(bool))
        self.assertEqual(online.bank_builds,2)

if __name__=='__main__':
    unittest.main()
