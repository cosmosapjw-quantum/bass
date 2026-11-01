#!/usr/bin/env python3
"""Independent axis-only check: no import of ce1ar_fixed_z or its optics."""
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

SOURCE_HASH='98bd1ed2909abfc5e47da12003354d6a3c75bee8ef0ecc13144b1a4c110a1207'

def audit(source, output):
 if hashlib.sha256(source.read_bytes()).hexdigest()!=SOURCE_HASH:
  raise ArithmeticError('referee requires immutable S2 ancestor CSV bytes')
 with source.open(newline='') as f:raw=list(csv.DictReader(f))
 with output.open(newline='') as f:stored=list(csv.DictReader(f))
 if len(raw)!=16842 or len(stored)!=5562:raise ArithmeticError('unexpected source or physics row count')
 failures=[];maximum=0.;maxroot=0.;checks=0
 for gl in (8,16,24):
  for ep in (-.035,0.,.035):
   owner=[]
   for axis in 'xyz':
    rr=sorted([r for r in raw if int(r['GL'])==gl and float(r['eps'])==(ep if ep else -.035) and r['dir']==axis],key=lambda v:float(v['u']))
    if len(rr)!=401:raise ArithmeticError('parent axis missing')
    t=np.array([float(r['u']) for r in rr])
    ell=np.array([-float(r['ln_R_base'])-(float(r['delta_ln_R']) if ep else 0.) for r in rr])
    owner.append(PchipInterpolator(t,ell,extrapolate=False))
   obs=np.array([float(x(.08)) for x in owner])
   for z in (.005,.01,.015,.02,.025,.03):
    for ia,axis in enumerate('xyz'):
     ue=brentq(lambda t:float(owner[ia](t))-obs[ia]+math.log1p(z),0,.08,xtol=5e-15)
     a0=np.exp([float(owner[i](ue))-obs[i] for i in range(3)])
     integrate=[]
     for j in range(3):
      if j==ia:continue
      val,_=quad(lambda t:math.exp(float(owner[ia](t)-obs[ia])-2*float(owner[j](t)-obs[j])),ue,.08,epsabs=1e-13,epsrel=1e-13,limit=200)
      integrate.append(val)
     distance=math.sqrt(a0[(ia+1)%3]*a0[(ia+2)%3]*integrate[0]*integrate[1])
     rr=[r for r in stored if int(r['GL'])==gl and float(r['eps'])==ep and float(r['z_target'])==z and r['direction']==axis]
     if len(rr)!=1:raise ArithmeticError('ambiguous new physics row')
     v=rr[0];gap=abs(float(v['D_A_over_cTstar'])-distance)
     rootgap=abs(float(v['u_emit'])-ue)
     maximum=max(maximum,gap);maxroot=max(maxroot,rootgap)
     if gap>3e-11 or rootgap>3e-12:failures.append([gl,ep,z,axis,gap,rootgap])
     checks+=1
 # A deliberately swapped physical axis must not silently retain the x ray distance.
 x=[r for r in stored if int(r['GL'])==24 and float(r['eps'])==0 and float(r['z_target'])==.02 and r['direction']=='x'][0]
 y=[r for r in stored if int(r['GL'])==24 and float(r['eps'])==0 and float(r['z_target'])==.02 and r['direction']=='y'][0]
 negative_gap=abs(float(x['D_A_over_cTstar'])-float(y['D_A_over_cTstar']))
 if negative_gap<1e-4:failures.append('axis corruption not detectable')
 report={'schema':'bass.ce1ar.same_author_independent_axis_quad.v1','source_sha256':SOURCE_HASH,
   'axis_rows_checked':checks,'max_absolute_DA_gap':maximum,'max_absolute_emission_clock_gap':maxroot,
   'corrupted_axis_negative_gap':negative_gap,'negative_test_detected':negative_gap>1e-4,
   'failures':failures,'status':'PASS_SCOPED_SAME_AUTHOR_AXIS_ONLY' if not failures else 'FAIL',
   'not_distinct_author':True,'not_continuum_error_certificate':True}
 if failures: raise ArithmeticError(json.dumps(report))
 return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--beams',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();result=audit(a.input,a.beams);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
