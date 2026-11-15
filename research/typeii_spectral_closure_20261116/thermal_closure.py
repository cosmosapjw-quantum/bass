"""Fixed-composition scalar energy equation with a general Compton target.
C=K_proper/(Gamma H), J=Q_proper/(Gamma H), A=2+2L/3.
This does not change native photon propagation or photoionization inputs.
"""
import math
def validate(C,J,A,target):
 if not all(math.isfinite(float(x)) for x in (C,J,A,target)) or C<0 or target<=0:raise ValueError('invalid thermal coefficients')
def rhs(T,C,J,A,target):
 validate(C,J,A,target)
 if not math.isfinite(float(T)) or T<0:raise ValueError('invalid matter temperature')
 return -A*T+C*(target-T)+J
def tracking(C,J,A,target,r):
 validate(C,J,A,target)
 if not math.isfinite(float(r)) or C+A+r<=0:raise ValueError('invalid tracking denominator')
 return (C*target+J)/(C+A+r)
def implicit(T,C,J,A,target,dt):
 validate(C,J,A,target)
 if not math.isfinite(float(dt)) or dt<=0 or 1+dt*(A+C)<=0:raise ValueError('invalid implicit step')
 if not math.isfinite(float(T)) or T<0:raise ValueError('invalid matter temperature')
 return (T+dt*(C*target+J))/(1+dt*(A+C))
