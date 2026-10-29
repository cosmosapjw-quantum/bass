"""CE1-P native BASS Rust comoving-frame stress/Jacobian differential check.

Scientific scope: positive frozen 6-cell massless collisionless Bianchi-I
with the current stored exact binary64 rays and their admissible rebindings.
Rust uses Frame.apply/det/step from BASS's original `kinetic/comoving.rs`.
Rust is *binary64*, not an MPFR certificate. The frozen CE1-M numerical error
bound cannot be promoted/replaced by this test.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys
import struct
import math
import random

import numpy as np
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation

BASE = Path(__file__).resolve().parents[2]
EXEC = Path(os.environ.get('CE1P_RUST_EXECUTABLE', str(BASE/'research/ce1p_20261029/ce1p_rust_binary')))
REF8_SOURCE_SHA = (
    '9d46624cdb747a5760eda945d5effeb17f0619ade2b7198ee1700903123455ba:'
    'c421e8148af743ea44bbb565f32a44090e18299e0e0b15f20eee37fb0a232211'
)

def digest(arr):
    return hashlib.sha256(np.asarray(arr, dtype='<f8').tobytes(order='C')).hexdigest()


def words(arr):
    a=np.asarray(arr,dtype='<f8').ravel()
    return [str(int(x)) for x in a.view('<u8')]


def rust_eval(ell, mass, n):
    mass=np.asarray(mass,dtype='<f8')
    n=np.asarray(n,dtype='<f8')
    assert mass.ndim==1 and n.shape==(len(mass),3)
    msg=' '.join([str(len(mass)), *words(ell)])+'\n'
    msg+='\n'.join(' '.join([words([m])[0], *words(q)]) for m,q in zip(mass,n))+'\n'
    p=subprocess.run([str(EXEC)],input=msg,text=True,capture_output=True,timeout=10)
    if p.returncode:
        raise RuntimeError('Rust rejected input: '+p.stderr.strip())
    h=p.stdout.strip().split()
    assert len(h)==13,h
    vals=np.array([struct.unpack('>d',int(w,16).to_bytes(8,'big'))[0] for w in h])
    return vals[0],vals[1:4],vals[4:].reshape(3,3)


def python_jacobian(ell,mass,n):
    ell=np.asarray(ell,dtype=float)
    m=np.exp(-ell)
    a=np.asarray(n)*m
    a2=a*a
    r=np.sqrt(a2.sum(axis=1))
    volume=np.prod(m)
    p=volume*np.sum((mass/r)[:,None]*a2,axis=0)
    rij=volume*np.einsum('q,qi,qj->ij',mass/(r*r*r),a2,a2)
    j=rij-p[:,None]*(1+2*np.eye(3))
    e=volume*np.dot(mass,r)
    return float(e),p,j


def check_bad_inputs():
    s=TabulatedRadiation([0,1],[0,1],[[.9]],backend='python_oracle')
    tests=[(-1.0,s.n[0]),(float('nan'),s.n[0]),(1.0,[0.,0.,0.]),
           (1.0,[float('inf'),0.,0.])]
    for mass,n in tests:
        try:rust_eval([0,0,0],[mass],[n])
        except RuntimeError:pass
        else:raise AssertionError(f'bad source permitted: {mass}, {n}')
    print('CE1P_NATIVE_REJECTS_BAD_RAYS_4_PASS')


def run():
    assert EXEC.is_file(),f'Native BASS Rust executable missing: {EXEC}'
    cp=subprocess.run([str(EXEC),'--self-test'],check=True,capture_output=True,text=True,timeout=10)
    assert 'CE1P_RUST_SELFTEST_4_PASS' in cp.stdout,cp.stdout
    check_bad_inputs()
    rng=np.random.default_rng(20261029)
    receipt={'schema':'bass.ce1p.rust_comoving_differential.v1',
        'rust_source':'BASS _rustcore/src/kinetic/comoving.rs Frame.apply/Frame.det/Frame.step',
        'rust_backend':'native_binary64_not_MPFR192_certificate',
        'states_checked':0,'source_settings':0,'rays_checked':[],
        'max_abs_energy_gap':0.,'max_abs_pressure_gap':0.,'max_abs_jacobian_gap':0.,
        'max_massless_trace_gap':0.,'max_jacobian_rowsum_gap':0.,
        'source_sha256_ref8':None,
        'upper_dag':'9/15','ce1':'PARTIAL','production_ready':False,
        'merge_ready':False,'formal_abi_proof':False}
    for ref in (1,2,4,8):
        s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],
              [[.1,.25,.05],[.2,.15,.15]],refinement=ref,backend='python_oracle')
        initial_hash=digest(s.n)+':'+digest(s.mass)
        if ref==8:
            assert initial_hash==REF8_SOURCE_SHA,(initial_hash,REF8_SOURCE_SHA)
            receipt['source_sha256_ref8']=initial_hash
        receipt['rays_checked'].append(len(s.mass))
        settings=[(s.mass,s.n),
                  (s.mass.copy()*1.005,s.n.copy()),
                  (s.mass.copy(),s.n.copy()*1.002)]
        for k in range(3):
            ell=np.array([0.0,0.0,0.0]) if k==0 else rng.uniform(0.005,0.07,3)
            settings.append((s.mass.copy()*(1.0+rng.uniform(-.003,.003,len(s.mass))),
                             s.n.copy()*(1+rng.uniform(-.002,.002,s.n.shape))))
        receipt['source_settings']+=len(settings)
        for i,(mass,n) in enumerate(settings):
            for ell in [[0.,0.,0.],[0.018,0.026,0.011],[0.061,0.041,0.072],
                        rng.uniform(0.002,0.078,3).tolist()]:
                ee,pp,jj=rust_eval(ell,mass,n)
                ep,py,jp=python_jacobian(ell,mass,n)
                # The existing CE1-P script compares original source.moments
                # whenever the ray/mass arrays are untouched.
                if i==0:
                    e0,p0=s.moments(np.array(ell,float))
                    np.testing.assert_allclose([ee,*pp],[e0,*p0],rtol=2e-12,atol=3e-14)
                np.testing.assert_allclose([ee,*pp],[ep,*py],rtol=2e-12,atol=3e-14)
                np.testing.assert_allclose(jj,jp,rtol=2e-12,atol=3e-14)
                en_gap=abs(ee-ep);p_gap=max(abs(pp-py));j_gap=max(abs(jj-jp).ravel())
                trace_gap=abs(ee-sum(pp));row_gap=max(abs(jj.sum(axis=1)+4*pp))
                receipt['max_abs_energy_gap']=max(receipt['max_abs_energy_gap'],en_gap)
                receipt['max_abs_pressure_gap']=max(receipt['max_abs_pressure_gap'],p_gap)
                receipt['max_abs_jacobian_gap']=max(receipt['max_abs_jacobian_gap'],j_gap)
                receipt['max_massless_trace_gap']=max(receipt['max_massless_trace_gap'],trace_gap)
                receipt['max_jacobian_rowsum_gap']=max(receipt['max_jacobian_rowsum_gap'],row_gap)
                assert trace_gap<2e-13,(ref,i,ell,trace_gap)
                assert row_gap<2e-13,(ref,i,ell,row_gap)
                receipt['states_checked']+=1
        # Hold physical cells fixed, allow admitted positive numerical ray/mass rebinding.
        assert digest(s.n)+':'+digest(s.mass)==initial_hash
    print(json.dumps(receipt,sort_keys=True,indent=2))
    assert receipt['rays_checked']==[6,24,96,384]
    assert receipt['states_checked']==4*6*4
    assert receipt['max_abs_jacobian_gap']<3e-14
    assert receipt['max_massless_trace_gap']<2e-13
    assert receipt['max_jacobian_rowsum_gap']<2e-13
    print('CE1P_RUST_BASS_COMOVING_STRESS_AND_JACOBIAN_DIFF_PASS')
    return receipt

if __name__=='__main__':
    run()
