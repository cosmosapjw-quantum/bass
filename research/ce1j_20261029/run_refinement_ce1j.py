from pathlib import Path
import json,hashlib,time
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_source_local import run_local_source_rk4
root=Path(__file__).resolve().parent; rows=[]
for f in [1,2,4,8]:
 s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=f,backend='python_oracle')
 start=time.perf_counter();o=run_local_source_rk4(s,backend='python_oracle')
 entry={'refinement':f,'rays':o['rays'], 'ce1g_h':o['ce1g_total'][1], 'ce1h_h':o['ce1h_total'][1], 'ce1i_h':o['ce1i']['total'][1], 'ce1j_h':o['ce1j']['total'][1], 'source_caps':o['per_panel_source_upper'], 'Emax':o['geometry_Emax_unchanged'], 'target_met':o['target_met'], 'elapsed_s':time.perf_counter()-start}
 assert entry['ce1j_h']<entry['ce1i_h']<entry['ce1h_h']<entry['ce1g_h']
 rows.append(entry);print('SWEEP',f,entry['ce1j_h'],entry['target_met'],flush=True)
r=json.loads((root/'CE1J_REF16_REUSE_SHA.json').read_text())
rows.append({'refinement':16,'rays':1536,'ce1g_h':r['ce1g'],'ce1h_h':r['ce1h'],'ce1i_h':r['ce1i'],'ce1j_h':r['ce1j_components']['total'][1], 'source_caps':[p['adopted_source_cap'] for p in r['panels']], 'Emax':r['original_geometry_Emax_upper'], 'target_met':r['target_met'], 'time_residual_origin':'SHA_VERIFIED_INHERITED'})
(root/'CE1J_SWEEP.json').write_text(json.dumps(rows,indent=2)+'\n')
print('DONE')
