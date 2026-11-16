#!/usr/bin/env python3
"""Separate time/grid/angle error, evolving-source effect and band truncation."""
import json,hashlib
import numpy as np
from redistribution import HERE,check

def outcomes(r):return np.array([r['surviving'],r['red_drift']+r['red_diffusion'],r['blue_drift']+r['blue_diffusion'],r['ionized']])
def main():
 first=json.loads((HERE/'TRANSIENT_CAMPAIGN.json').read_text())['cases'];extra=json.loads((HERE/'TARGETED_REFINEMENT.json').read_text());rows=first+extra
 check(len(rows)==23 and len({r['label'] for r in rows})==23,'source campaign incomplete')
 data={r['label']:r for r in rows}
 for r in rows:
  check(abs(sum(outcomes(r))-1)<2e-8,'source packet total')
  check(r['max_number_budget_abs_gap']<2e-8 and r['max_normal_radiation_energy_ledger_relative_gap']<5e-8,'source numerical acceptance')
  check(r['max_occupation_one_initial_photon_per_m3']<1e-8,'source dilute assumption')
 def difference(a,b):
  x=outcomes(data[a])-outcomes(data[b]);return {'a':a,'b':b,'delta_surviving_red_blue_ionized':x.tolist(),'max_abs_delta':float(max(abs(x)))}
 refinements=[difference(a,b) for a,b in [('time80','time160'),('time160','time320'),('time320','time640'),('time640','time1280'),('freq40','time320'),('time320','freq160'),('time640','fine640'),('angle12','time320'),('time320','angle72')]]
 check(all(refinements[i+1]['max_abs_delta']<refinements[i]['max_abs_delta'] for i in range(3)),'time refinement is not improving')
 differences=[difference(a,b) for a,b in [('frozen','time320'),('frozen640','time640'),('source1700_frozen','source1700'),('source1700_frozen640','source1700_640'),('no_recoil','time320'),('no_diffusion','time320'),('no_ionization','time320'),('band40','time320'),('band80','time320')]]
 paired1100=(outcomes(data['frozen640'])-outcomes(data['time640']))-(outcomes(data['frozen'])-outcomes(data['time320']))
 paired1700=(outcomes(data['source1700_frozen640'])-outcomes(data['source1700_640']))-(outcomes(data['source1700_frozen'])-outcomes(data['source1700']))
 records=[]
 for r in rows:
  files=[HERE/'outputs'/(r['label']+s) for s in ('.json','.csv','_final_N.npy')]
  records.append({'label':r['label'],'outcome_order':'surviving, red finite-band exit, blue finite-band exit, tagged true ionization','outcomes':outcomes(r).tolist(),'settings':{k:r[k] for k in ('z_initial','halfwidth_initial_Doppler','frequency_cells','angular_directions','time_steps','frozen_matter','recoil','frequency_diffusion','angular_redistribution','true_ionization')},'mean_censored_residence_tauH':r['mean_censored_residence_tauH'],'files_sha256':{str(f.relative_to(HERE)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}})
 out={'actual_source_cases':len(rows),'records':records,'time_frequency_angular_refinements':refinements,'model_source_boundary_differences':differences,'paired_frozen_effect_stepchange_z1100':paired1100.tolist(),'paired_frozen_effect_stepchange_z1700':paired1700.tolist(),'max_number_budget_abs_gap':max(r['max_number_budget_abs_gap'] for r in rows),'max_normal_energy_ledger_relative_gap':max(r['max_normal_radiation_energy_ledger_relative_gap'] for r in rows),'max_packet_occupation':max(r['max_occupation_one_initial_photon_per_m3'] for r in rows),'max_angular_roundoff_clipped_mass':max(r['angular_roundoff_clipped_mass'] for r in rows),'normalization':'one initial photon per reference normal-comoving m3, linear rescaling permitted while occupation remains dilute','precision_admission':'measured grid/time differences only, no rigorous global error bound or global escape','model_admission':'factorized leading FP frequency+dipole angle, not full angle-frequency correlated redistribution'}
 (HERE/'TRANSIENT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
 print('REFINEMENTS',json.dumps(refinements,indent=2));print('PAIRED_SOURCE_EFFECTS',paired1100,paired1700)
 print('MAX_BUDGETS',out['max_number_budget_abs_gap'],out['max_normal_energy_ledger_relative_gap'])
 for name in ('time1280','fine640','band40','band80','source1700_640','source1700_frozen640','source1392','source800'):print('RESULT',name,outcomes(data[name]))
if __name__=='__main__':main()
