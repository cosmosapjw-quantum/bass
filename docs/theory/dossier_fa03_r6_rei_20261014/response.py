"""Read-only common-coordinate analysis with exact rational arithmetic.

CSV numeric tokens are decoded as binary64 then lifted exactly to Fractions.
Results describe the resulting piecewise-linear stored reference, not the true ODE.
Unknown nodal/curvature errors remain None. This module never launches a solver.
"""
from __future__ import annotations
import bisect,csv,math
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Mapping,Sequence

WEIGHTS = {
    'linear': tuple(F(x,6) for x in (1,-8,0,8,-1)),
    'quadratic': tuple(F(x,6) for x in (-1,16,-30,16,-1)),
    'cubic': tuple(F(x,3) for x in (-2,4,0,-4,2)),
}
ORDER=('minus','half_minus','zero','half_plus','plus')

def binary64(token: str|float|int) -> F:
    x=float(token)
    if not math.isfinite(x):raise ValueError('nonfinite numeric token')
    return F.from_float(x)

def bracket(axis: Sequence[F], target: F) -> tuple[int,int]:
    if len(axis)<1 or any(b<=a for a,b in zip(axis,axis[1:])):
        raise ValueError('axis must be nonempty and strictly increasing')
    if target<axis[0] or target>axis[-1]:raise ValueError('target outside stored coverage')
    i=bisect.bisect_left(axis,target)
    return (i,i) if axis[i]==target else (i-1,i)

@dataclass(frozen=True)
class Curve:
    coordinate: str
    axis: tuple[F,...]
    values: tuple[Mapping[str,F],...]
    source: str

    def __post_init__(self):
        if len(self.axis)!=len(self.values):raise ValueError('axis/state length mismatch')
        bracket(self.axis,self.axis[0] if self.axis else F(0))
        keys=set(self.values[0])
        if any(set(row)!=keys for row in self.values):raise ValueError('inconsistent value columns')

@dataclass(frozen=True)
class Sample:
    coordinate: str
    target: F
    indices: tuple[int,int]
    weights: tuple[F,F]
    values: Mapping[str,F]
    span: F
    exact_node: bool

def load_native(path: str|Path,coordinate: str,columns: Sequence[str]) -> Curve:
    if coordinate not in ('a','time_s'):raise ValueError('only a or time_s comparisons are supported')
    with Path(path).open(newline='') as f:rows=list(csv.DictReader(f))
    if not rows:raise ValueError('empty native data')
    if coordinate not in rows[0] or any(c not in rows[0] for c in columns):
        raise ValueError('required native column missing')
    axis=tuple(binary64(row[coordinate]) for row in rows)
    bracket(axis,axis[0])
    vals=tuple({c:binary64(row[c]) for c in columns} for row in rows)
    return Curve(coordinate,axis,vals,str(path))

def sample(curve: Curve,target: F) -> Sample:
    if not isinstance(target,F):raise TypeError('exact Fraction target required')
    if target<curve.axis[0] or target>curve.axis[-1]:raise ValueError('target outside stored coverage')
    j=bisect.bisect_left(curve.axis,target)
    i=j if curve.axis[j]==target else j-1
    if i==j:return Sample(curve.coordinate,target,(i,j),(F(1),F(0)),curve.values[i],F(0),True)
    h=curve.axis[j]-curve.axis[i];theta=(target-curve.axis[i])/h;w=(1-theta,theta)
    vals={k:w[0]*curve.values[i][k]+w[1]*curve.values[j][k] for k in curve.values[i]}
    return Sample(curve.coordinate,target,(i,j),w,vals,h,False)

def node_plus_interpolation_radius(point: Sample,node_radii: Sequence[F|None],curvature: F|None) -> F|None:
    """Conditional true-curve bound. Curvature is in the SELECTED coordinate."""
    if len(node_radii)!=2:raise ValueError('two endpoint radii required')
    if curvature is not None and curvature<0:raise ValueError('negative curvature bound')
    total=F(0)
    for w,e in zip(point.weights,node_radii):
        if e is not None and e<0:raise ValueError('negative nodal radius')
        if w and e is None:return None
        if w:total+=w*e
    if point.exact_node:return total
    if curvature is None:return None
    return total+curvature*point.span**2*point.weights[0]*point.weights[1]/2

def scaled_contrasts(values: Mapping[str,F]) -> dict[str,F]:
    if set(values)!=set(ORDER):raise ValueError('the exact five signed case names are required')
    return {name:sum((w*values[key] for w,key in zip(row,ORDER)),F(0)) for name,row in WEIGHTS.items()}

def contrast_radii(errors: Mapping[str,F|None]) -> dict[str,F|None]:
    if set(errors)!=set(ORDER):raise ValueError('the exact five signed case names are required')
    if any(e is not None and e<0 for e in errors.values()):raise ValueError('negative error radius')
    out={}
    for name,row in WEIGHTS.items():
        out[name]=None if any(w and errors[k] is None for w,k in zip(row,ORDER)) else sum((abs(w)*errors[k] for w,k in zip(row,ORDER) if w),F(0))
    return out

def classify(delta: F,error: F|None,floor: F) -> str:
    if floor<0 or error is not None and error<0:raise ValueError('negative error/floor')
    if abs(delta)<=floor:return 'BELOW_RESPONSE_FLOOR'
    if error is None:return 'UNRESOLVED_UNKNOWN_NUMERICAL_ERROR'
    return 'RESOLVED_NUMERICAL_ONLY' if error<=abs(delta)/10 else 'UNRESOLVED_NUMERICAL_ERROR'

def encode(x):
    if isinstance(x,F):return {'numerator':x.numerator,'denominator':x.denominator,'approx':float(x)}
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x
