"""Execute selected preserved H/J scalar kernels in a minimal reference namespace.

This is NOT a production-package import. hierarchy_coeff.py is byte-identical
at the live source pin. H RHS bodies match the DL1 current-body excerpt;
PSTF helper context is the explicitly preserved archival source, not a claim
that the entire current hierarchy/pstf modules were run.
"""
import ast,copy
from pathlib import Path
from functools import lru_cache
from itertools import permutations
from math import factorial,pi,sqrt
import numpy as np
import sympy as sp
from sympy.physics.wigner import gaunt,real_gaunt
ROOT=Path(__file__).resolve().parents[1]

def load_functions(filename,names,ns):
    parsed=ast.parse((ROOT/'vendor'/filename).read_text())
    selected=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names]
    if set(n.name for n in selected)!=set(names):raise RuntimeError('missing preserved function')
    exec(compile(ast.Module(body=selected,type_ignores=[]),filename,'exec'),ns)

H={'np':np,'permutations':permutations,'factorial':factorial,'L_MAX_SUPPORTED':6,
   '_TRACE_BASIS_CACHE':{},'_PSTF_OP_CACHE':{},'SIGMA_SIGNS':dict(A=1.,B=-1.,C=-1.)}
load_functions('archive_hierarchy.py',['_symmetrize','_trace_last_two','_sym_basis','_trace_subspace','pstf_operator','pstf','_contract_one','_contract_two','_outer_sigma','hierarchy_rhs'],H)
J={'np':np,'sp':sp,'lru_cache':lru_cache,'_real_gaunt':real_gaunt,'_cx_gaunt':gaunt,'_DISK':{},'SIGMA_SIGNS':H['SIGMA_SIGNS']}
load_functions('archive_pstf_coeff.py',['_rg_table','_R_op','outer_block','c2_block','c1_block','apply_block'],J)
load_functions('archive_hierarchy_coeff.py',['hierarchy_rhs_coeff'],J)


def Dnorm(l):return float(sp.factorial2(2*l+1))/(4*pi*factorial(l))


def coefficient_reference(c,hub,S,lout=4):
    from polarized_dictionary import stf_basis
    s5=np.einsum('mij,ij->m',stf_basis(),S)
    jc={(l,i):np.array([c.get(('I',l,m),0.) for m in range(-l,l+1)])/sqrt(Dnorm(l)) for l in range(lout+3) for i in range(3)}
    out={}
    for l in range(lout+1):
        v=sqrt(Dnorm(l))*J['hierarchy_rhs_coeff'](jc,hub,s5,l,0)
        out.update({('I',l,m):float(x) for m,x in zip(range(-l,l+1),v)})
    return out


def dense_moments(g,I,lmax=4):
    out={0:float(np.dot(g.w,I))}
    for l in range(1,lmax+1):
        ix='ijklmn'[:l];T=np.einsum('a,'+','.join('a'+v for v in ix)+'->'+ix,g.w*I,*([g.n]*l))
        out[l]=H['pstf'](T)
    return out


def dense_reference(g,I,hub,S):
    mom=dense_moments(g,I,4)
    j={(l,i):v for l,v in mom.items() for i in range(3)}
    return {l:H['hierarchy_rhs'](j,hub,S,l,0) for l in range(3)}
