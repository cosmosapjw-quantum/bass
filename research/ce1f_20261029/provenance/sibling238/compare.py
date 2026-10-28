"""Pinned same-exact-input sibling CE1-F implementation comparison."""
import importlib.util,json,sys,hashlib
from fractions import Fraction
from pathlib import Path
import numpy as np
import bianchi.nonperturbative.einstein_tabulated_source as own

here=Path(__file__).resolve().parent
name='bianchi.nonperturbative._sibling_ce1f_0286dd0'
spec=importlib.util.spec_from_file_location(name,here/'einstein_tabulated_source.py')
other=importlib.util.module_from_spec(spec);sys.modules[name]=other;spec.loader.exec_module(other)
mu=[0.,.5,1.];phi=[0.,.25,.75,1.];energy=[[.1,.25,.05],[.2,.15,.15]]
exact=lambda a:str(Fraction.from_float(float(a)))
rows=[]
for f in [1,2,4,8]:
 a=own.TabulatedRadiation(mu,phi,energy,refinement=f,backend='python_oracle')
 b=other.TabulatedRadiation(tuple(map(exact,mu)),tuple(map(exact,phi)),tuple(tuple(map(exact,row)) for row in energy),refinement=f,backend='python_oracle')
 ca=own.certified_tabulated_pressure(a,[.08]*3)
 cb=other.certified_tabulated_pressure(b,[0]*3,[.08]*3)
 ga=own.certified_tabulated_geometry(a,end=.08);gb=other.certified_tabulated_geometry(b,end=.08)
 rng=np.random.default_rng(239238)
 gaps=[max(abs(a.moments(e)[1]-b.moments(e)[1])) for e in rng.uniform(0,.08,(16,3))]
 rows.append(dict(refinement=f,max_float_pressure_difference=float(max(gaps)),own_pressure_bound=ca['bound_max'],sibling_pressure_bound=cb['max_pressure_upper'],own_geometry_h_bound=ga['geometry_h_upper'],sibling_geometry_h_bound=gb['geometry_h_upper'],same_continuum_energy=a.continuum_energy==b.exact_energy))
 assert all(r['same_continuum_energy'] for r in rows)
 assert max(gaps)<2e-15
print(json.dumps(rows,indent=2))
(here/'SAME_INPUT_COMPARISON.json').write_text(json.dumps(dict(own_pr=239,own_head='d4c491799d16501c2f7c200832d8f2fadb72f3c1',sibling_pr=238,sibling_head='0286dd0a97f512a2dc6f431e462e64bd65267047',sibling_sha256=hashlib.sha256((here/'einstein_tabulated_source.py').read_bytes()).hexdigest(),rows=rows,scope='same binary-rational physical input, distinct source implementations; numerical agreement is not a universal certificate proof'),indent=2))
