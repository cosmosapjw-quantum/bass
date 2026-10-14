"""Behavioral test: zero-slope closure must reproduce the frozen grey family."""
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference'))
import fa02
from fa03 import solve_moments

class GreyLimit(unittest.TestCase):
    def test_exact_grey_limit(self):
        actual=solve_moments(.008,.010,steps=64,nr=3,nphi=12)[0]
        expected=fa02.solve_cap(.008,.010,steps=64,nr=3,nphi=12)
        self.assertLess(np.linalg.norm(actual-expected),2e-14)

if __name__=='__main__':unittest.main()
