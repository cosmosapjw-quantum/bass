"""Strict JSON conversion of NumPy scalars, with no fallback stringification."""
import numpy as np

def json_scalar(value):
    if isinstance(value,np.generic): return value.item()
    raise TypeError(f'Unsupported JSON value type: {type(value).__name__}')
