"""Only inverse-dependent data refresh after the independently confirmed C9 fix."""
import csv
import hashlib
import json
import numpy as np
from locked_bridge import ROOT, ROUNDTRIP_TOL, load_actual_inputs, Units, C, to_packets, state_boost, fixed_grid_inverse

out=ROOT/'artifacts'
grid,f,diag=load_actual_inputs()
units=Units(8*np.pi*6.67430e-11/C**4,1e20,5.45e-27)
old_validation=json.loads((out/'VALIDATION.json').read_text())
(out/'PRE_C9_REPAIR'/'VALIDATION.json').write_text(json.dumps(old_validation,indent=2)+'\n')
rows=list(csv.DictReader((out/'BOOST_COVARIANCE.csv').open()))
(out/'PRE_C9_REPAIR'/'BOOST_COVARIANCE.csv').write_bytes((out/'BOOST_COVARIANCE.csv').read_bytes())
changes=[]
for row in rows:
    occupation=f if row['scenario'].startswith('actual') else f*(1+.4*grid.directions[:,0]+.3*(3*grid.directions[:,2]**2-1)/2)[None,:]
    beta=np.array([float(row[key]) for key in ('beta_x','beta_y','beta_z')])
    returned=state_boost(state_boost(to_packets(grid,occupation,units),beta),-beta)
    error=float(np.max(np.abs(fixed_grid_inverse(returned,grid)/occupation-1)))
    assert error<=ROUNDTRIP_TOL
    old=float(row['inverse_positive_f_relative'])
    row['inverse_positive_f_relative']=error
    changes.append(dict(scenario=row['scenario'],boost_chart=row['boost_chart'],beta_magnitude=row['beta_magnitude'],old=old,new=error))
with (out/'BOOST_COVARIANCE.csv').open('w',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
fback=fixed_grid_inverse(to_packets(grid,f,units),grid)
actual_error=float(np.max(np.abs(fback/f-1)))
assert actual_error<=ROUNDTRIP_TOL
summary=json.loads(json.dumps(old_validation))
summary['bridge']['max_positive_f_roundtrip_relative']=actual_error
summary['covariance']['max_inverse_f_relative']=max(float(x['inverse_positive_f_relative']) for x in rows)
summary['C9_targeted_repair']='Inverse validates labels/k without fake f=1; reverses forward scaling. Only inverse error fields refreshed; N/T, mutation data and plotted data unchanged.'
(out/'VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
receipt=dict(status='PASS',scope='36 inverse-boost errors plus actual original-frame inverse',
             rows=changes,actual_roundtrip=actual_error,max_inverse=summary['covariance']['max_inverse_f_relative'],
             forward_N_T_data_unchanged=True,figure_plotted_values_unchanged=True,
             figure_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ('LOCKED_CELL_BRIDGE.png','LOCKED_CELL_BRIDGE.pdf')})
(out/'C9_AFFECTED_CHECKS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({key:receipt[key] for key in ('status','scope','actual_roundtrip','max_inverse','forward_N_T_data_unchanged','figure_plotted_values_unchanged')},indent=2))
