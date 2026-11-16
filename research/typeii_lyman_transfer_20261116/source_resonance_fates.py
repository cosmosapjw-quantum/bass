#!/usr/bin/env python3
import json,csv,subprocess
from pathlib import Path
import numpy as np
from line_transfer import ROOT,resonance_fates,check
HERE=Path(__file__).resolve().parent
parent='232c033cb961fc3d4f5a98760ea27c834b8b0b55'
path='research/typeii_cascade_effective_20261116/FULL_GENERATORS.npy'
a=subprocess.check_output(['git','rev-parse',parent+':'+path],cwd=ROOT,text=True).strip();b=subprocess.check_output(['git','hash-object',str(ROOT/path)],text=True).strip();check(a==b,'source generator drift')
Q=np.load(ROOT/path);states=np.genfromtxt(ROOT/'research/typeii_cascade_effective_20261116/SOURCE_TRACE_STATIONARY.csv',delimiter=',',names=True)
geom=np.genfromtxt(HERE/'DIRECTIONAL_LINE_DIAGNOSTICS.csv',delimiter=',',names=True).reshape(358,26)
rows=[];err=0.;defect=0.;probes=[]
for i,q in enumerate(Q):
 f=resonance_fates(q)
 # Independent analytic star topology, exact only for these admitted pathways.
 up=q[3,2];ud=q[5,2];As=q[2,3];Ad=q[2,5];bs=q[6,3];bd=q[6,5];Ag=q[0,2];bp=q[6,2]
 beta_eff=bp+up*bs/(As+bs)+ud*bd/(Ad+bd)
 pred=beta_eff/(Ag+beta_eff);err=max(err,abs(pred-f['ionization_probability'])/max(pred,1e-300));defect=max(defect,f['probability_defect'])
 total_tau=geom['formal_sobolev_tau'][i];deathdiag=total_tau*f['ionization_probability']
 rows.append([states['z_mean'][i],f['reemission_probability'],f['ionization_probability'],f['mean_residence_s'],min(total_tau),max(total_tau),min(deathdiag),max(deathdiag)])
 if abs(states['z_mean'][i]-1100)<1e-6:probes.append({'z_mean':1100.,**f,'analytic_star_beta_eff_s':beta_eff,'formal_tau_total_range':[float(min(total_tau)),float(max(total_tau))],'formal_tau_times_photoionization_fate_range':[float(min(deathdiag)),float(max(deathdiag))]})
check(err<2e-12 and defect<2e-12,'resonance fate independent star')
with (HERE/'RESONANCE_FATES.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['z_mean','p_Lya_reemission','p_ionization','residence_s','formal_tau_total_min','formal_tau_total_max','formal_tau_pion_min','formal_tau_pion_max']);w.writerows(rows)
out={'source_states':len(rows),'parent_generator_blob':a,'star_probability_max_relative_gap':err,'probability_defect_max':defect,'source_probes':probes,'interpretation':'tagged initial 2p excitation, source n<=3 resonant subspace incl3s/3d; ionization exit before Ly-alpha re-emission','not_claimed':'global escape from tau*pion: frequency redistribution, later recombination and line feedback require transport; truncated network is not full high-n HYREC death probability'}
(HERE/'RESONANCE_FATE_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
