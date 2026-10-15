"""C9 independently auditable deterministic tensor-product Stokes reduction.

Each term is evaluated in *two* binary64 multiplications (energy*Stokes then
ray_weight*product) and added in a balanced binary tree with depth ceil(log2N).
Assume IEEE correct rounding of each indicated NumPy multiply/add, no underflow
or overflow, exact supplied finite binary64 inputs, and standard two-multiplication
term evaluation. Against the *exact sum of those binary64 input values*:

  |delta Stokes_k| <= gamma_(2+ceil_log2N)*sum(ray*energy*|Stokes_k|).

Our accepted upper uses an exact Fraction W=sum(ray)*sum(energy), and max abs of
all binary64 Stokes components, then 4*W*M*gamma for trace-norm coherency.

Not a bound for Gaussian weight generation, source/geodesic coefficients,
floating RK4 time integration, observer physics or IEEE exceptions.
"""
from __future__ import annotations
import hashlib,math,sys
from fractions import Fraction as F
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
C7=HERE.parent/"fa03_c7_polarized_batch_20261015"
C8=HERE.parent/"fa03_c8_error_budget_20261015"
sys.path.insert(0,str(C7))
sys.path.insert(0,str(C8))
import stokes_vector as old
import batch_transport as b
import aggregation_roundoff as inherited

U=F(1,2**53)

def gamma(k:int)->F:
    if isinstance(k,bool) or not isinstance(k,int) or k<0 or k*U>=1:
        raise ValueError("nonnegative integer operation count with k*u<1")
    return (k*U)/(1-k*U)

def depth_for(n:int)->int:
    if not isinstance(n,int) or isinstance(n,bool) or n<1:
        raise ValueError("positive number of terms")
    return (n-1).bit_length()

def _validate(Y,ray,energy):
    Y=np.asarray(Y)
    ray=np.asarray(ray)
    energy=np.asarray(energy)
    if Y.dtype!=np.float64 or ray.dtype!=np.float64 or energy.dtype!=np.float64:
        raise TypeError("exact binary64 input contract; no implicit dtype conversion")
    if Y.ndim!=4 or Y.shape[-1]!=4 or ray.shape!=(Y.shape[1],) or energy.shape!=(Y.shape[2],):
        raise ValueError("shape mismatch: Stokes [eps,rays,energy,4]")
    if not Y.size or not np.isfinite(Y).all() or not np.isfinite(ray).all() or not np.isfinite(energy).all():
        raise ValueError("all inputs must be finite and nonempty")
    if (ray<0).any() or (energy<0).any():
        raise ValueError("positive or zero weights")
    return Y,ray,energy

def pairwise_tensor_sum(Y,ray,energy):
    """Pure vectorized 2-multiply/pairwise-add canonical reduction."""
    Y,ray,energy=_validate(Y,ray,energy)
    m,nr,ne,k=Y.shape
    terms=np.empty_like(Y)
    # Exactly TWO independent rounded NumPy multiplications per term.
    np.multiply(Y,energy[None,None,:,None],out=terms)
    np.multiply(terms,ray[None,:,None,None],out=terms)
    flat=terms.reshape(m,nr*ne,k)
    n=flat.shape[1]
    padded=1<<depth_for(n)
    arr=np.zeros((m,padded,4),dtype=np.float64)
    arr[:,:n,:]=flat
    size=padded
    while size>1:
        half=size//2
        # Non-overlapping views on RHS and an explicit new sum array.
        tmp=np.add(arr[:,0:size:2,:],arr[:,1:size:2,:])
        arr[:,:half,:]=tmp
        size=half
    return arr[:,0,:].copy()

def pairwise_parallel_by_epsilon(Y,ray,energy,workers=1):
    """Actual independent-epsilon ThreadPool path; preserve result order.

    Unlike physical ray chunks this parallelizes only final deterministic sums.
    On short 36/144/480-ray cases overhead can outweigh work: not default.
    """
    Y,ray,energy=_validate(Y,ray,energy)
    if isinstance(workers,bool) or not isinstance(workers,int) or not (1<=workers<=8):
        raise ValueError("1<=workers<=8")
    if workers==1 or len(Y)==1:
        return pairwise_tensor_sum(Y,ray,energy)
    with ThreadPoolExecutor(max_workers=min(workers,len(Y))) as executor:
        # No shared writes, exact output order by executor.map.
        parts=list(executor.map(lambda idx:pairwise_tensor_sum(Y[idx:idx+1],ray,energy),
                                range(len(Y))))
    return np.concatenate(parts,axis=0)

def exact_inputs_weight_mass(ray,energy):
    ray=np.asarray(ray);energy=np.asarray(energy)
    # Fraction.from_float enforces exact dyadic interpretation of supplied weights.
    sr=sum((F.from_float(float(x)) for x in ray),F(0))
    se=sum((F.from_float(float(x)) for x in energy),F(0))
    return sr*se

def scalar_bounds(Y,ray,energy):
    """Exact fraction bounds for four Stokes outputs, assuming rounding contract."""
    Y,ray,energy=_validate(Y,ray,energy)
    n=Y.shape[1]*Y.shape[2]
    opcount=2+depth_for(n)
    g=gamma(opcount)
    mass=exact_inputs_weight_mass(ray,energy)
    # bound only floating aggregation, not prior input error or output F reconstruction
    M=max((F.from_float(abs(float(y))) for y in Y.ravel()),default=F(0))
    scalar=M*mass*g
    return {"nterms":n,"padded_depth":depth_for(n),"ops_per_term_upper":opcount,
      "gamma":str(g),"input_weight_mass":str(mass),
      "max_absolute_stokes_input":str(M),
      "each_stokes_absolute_error_bound":str(scalar),
      "coherency_trace_norm_upper_before_reconstruction":str(4*scalar),
      "coherency_trace_norm_upper_decimal":float(4*scalar),
      "weight_generation_error":None,"RK4_roundoff":None,
      "state_source_accuracy":None,"float_matrix_reconstruction_error":None}

def exact_dyadic_tensor_sum(Y,ray,energy):
    """Slow auditor only: exact result using Fraction for the binary64 inputs."""
    Y,ray,energy=_validate(Y,ray,energy)
    out=[[F(0) for _ in range(4)] for _ in range(len(Y))]
    exray=[F.from_float(float(x)) for x in ray]
    exenergy=[F.from_float(float(x)) for x in energy]
    for i,wi in enumerate(exray):
        for j,wj in enumerate(exenergy):
            v=wi*wj
            for a in range(len(Y)):
                for k in range(4):
                    out[a][k]+=v*F.from_float(float(Y[a,i,j,k]))
    return out

def pairwise_exact_gap(Y,ray,energy):
    out=pairwise_tensor_sum(Y,ray,energy)
    exact=exact_dyadic_tensor_sum(Y,ray,energy)
    differences=[[abs(F.from_float(float(out[a,k]))-exact[a][k]) for k in range(4)]
                 for a in range(len(out))]
    maxcomp=max((v for row in differences for v in row),default=F(0))
    info=scalar_bounds(Y,ray,energy)
    assert maxcomp<=F(info["each_stokes_absolute_error_bound"]), "PAIRWISE_CERTIFICATE_BROKEN"
    return {"max_stokes_error_exact_dyadic":str(maxcomp),"max_stokes_error_decimal":float(maxcomp),
            "scalar_upper_exact":info["each_stokes_absolute_error_bound"],
            "bound_covers_actual_executed_float":True}

def triple_product_witness():
    # Found independently with deterministic seed; all entries are positive
    # and within a physically relevant sub-unit range (scale powers of two).
    a=1.8824541426379982/2
    b_=1.081368138353021/2
    s=1.2888211787477557/4
    exact=F.from_float(a)*F.from_float(b_)*F.from_float(s)
    observed=F.from_float((a*b_)*s)
    err=abs(observed-exact)/exact
    assert err>gamma(1) and err<=gamma(2)
    return {"ray_weight":a,"energy_weight":b_,"stokes_sample":s,
            "relative_rounding_error":str(err),
            "relative_rounding_error_over_unit_u":float(err/U),
            "incorrect_old_gamma_1":str(gamma(1)),
            "corrected_2_multiply_gamma_2":str(gamma(2)),
            "old_claim_refuted":True}

def _solve_per_ray(eps,ell,energy,steps):
    """Same frozen FA03 operator, with per-ray Stokes preserved until reduction."""
    data=b.fa02.setup(ell,.008,.01)
    Y=np.zeros((len(eps),len(ell),len(energy),4),np.float64)
    h=.5/steps
    previous=old._stokes_coefficient(.5,data,eps,energy)
    for j in range(steps):
        x=.5+j*h
        mid=old._stokes_coefficient(x+h/2,data,eps,energy)
        next_=old._stokes_coefficient(x+h,data,eps,energy)
        a=old._rhs(Y,previous)
        z=old._rhs(Y+h*a/2,mid)
        c=old._rhs(Y+h*z/2,mid)
        d=old._rhs(Y+h*c,next_)
        Y=Y+h*(a+2*z+2*c+d)/6
        previous=next_
    return Y

def actual_fa03_reduction(eps=(-.1,0.,.1), *,nr=3,nphi=12,steps=64,ne=4,
                          mode="pairwise", return_inputs=False):
    b.verify()
    es=np.atleast_1d(np.asarray(eps,np.float64))
    if es.ndim!=1 or not len(es) or not np.isfinite(es).all() or np.max(abs(es))>.1:
        raise ValueError("epsilon must be finite |eps|<=.1")
    if not isinstance(steps,int) or steps<1 or not isinstance(ne,int) or ne<2:
        raise ValueError("positive time steps, ne>=2")
    ell,ray=b._prepared_rays(nr,nphi)
    nodes,ew=leggauss(ne)
    energy=1+.02*nodes
    ew=(ew/2).astype(np.float64)
    Y=_solve_per_ray(es,ell,energy,steps)
    if mode=="pairwise":
        result=pairwise_tensor_sum(Y,ray,ew)
    elif mode=="numpy_einsum":
        result=np.einsum("n,e,mnek->mk",ray,ew,Y,optimize=True)
    elif mode=="math_fsum":
        # Slow (auditor only); the two product roundings remain.
        terms=(Y*ew[None,None,:,None])*ray[None,:,None,None]
        flat=terms.reshape(len(Y),len(ray)*len(ew),4)
        result=np.array([[math.fsum(flat[i,:,k]) for k in range(4)]
                         for i in range(len(Y))],np.float64)
    else:raise ValueError("unknown explicit reduction mode")
    return (result,Y,ray,ew) if return_inputs else result

if __name__=="__main__":
    import json
    a,Y,w,e=actual_fa03_reduction(return_inputs=True)
    print(json.dumps({"old_gamma1_witness":triple_product_witness(),
                       "real_FA03_pairwise_stokes":a.tolist(),
                       "small_source_exact_arithmetic_check":pairwise_exact_gap(Y,w,e)},indent=2))
