"""Dependency-light numerical convention constants shared by all frontends."""
from __future__ import annotations

import numpy as np


SQRT3 = float(np.sqrt(3.0))

EPS3 = np.zeros((3, 3, 3))
for _i in range(3):
    for _j in range(3):
        for _k in range(3):
            EPS3[_i, _j, _k] = (_i - _j) * (_j - _k) * (_k - _i) / 2
