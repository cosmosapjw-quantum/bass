#!/usr/bin/env python3
"""Numerical equivalence of two same-source code paths, not byte identity/proof."""
import csv,json
from pathlib import Path
from math import isfinite
ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'data'

def read(name):
 with (DATA/name).open(newline='') as f:return list(csv.DictReader(f))

def run():
 a=read('CE1AR_FIXED_Z_BEAMS.csv');b=read('CE1AR_FIXED_Z_REMOTE_BEAMS.csv')
 c=read('CE1AR_FIXED_Z_RESPONSE.csv');d=read('CE1AR_FIXED_Z_REMOTE_RESPONSE.csv')
 if len(a)!=len(b) or len(a)!=5562 or len(c)!=len(d) or len(c)!=1854:
  raise ArithmeticError('original source observer-geometry row mismatch')
 report={}
 for label,old,new,cols in (
  ('beam',a,b,[('u_emit','u_em'),('D_A_over_cTstar','D_A'),('D_A_saunders_over_cTstar','D_A_saunders')]),
  ('response',c,d,[('central_secant_D_A_at_fixed_z','source_secant'),('emitter_clock_response_term','clock_term')])):
  for x,y in zip(old,new):
   ka=(x['GL'],x.get('eps'),x.get('z_target'),x['direction']);kb=(y['GL'],y.get('eps'),y.get('z'),y['direction'])
   if ka!=kb:raise ArithmeticError(f'{label} geometry key mismatch')
  for cx,cy in cols:
   vals=[abs(float(x[cx])-float(y[cy])) for x,y in zip(old,new)]
   peak=max(vals)
   if not isfinite(peak) or peak>(3e-11 if label=='response' else 2e-10):
    raise ArithmeticError(f'{label}.{cx} code-path numerical identity FAIL {peak}')
   report[f'{label}_{cx}_max_absolute_gap']=peak
 output={'schema':'bass.ce1ar.two_source_equal_implementations.v1',
   'same_parent_owner':True,'remote_is_alternate_code_not_distinct_author':True,
   'byte_identical_outputs':False,'numerical_comparison':report,
   'status':'PASS_SCOPED_NUMERICAL_EQUIVALENCE'}
 (DATA/'CE1AR_IMPLEMENTATION_CROSSCHECK.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps(output,indent=2))
 return output
if __name__=='__main__':run()
