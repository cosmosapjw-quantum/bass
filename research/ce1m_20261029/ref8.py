import json, time, hashlib
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_source_canonical import run_canonical_panel_source
s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=8,backend='python_oracle')
t=time.perf_counter()
r=run_canonical_panel_source(s,backend='python_oracle')
summary={'refinement':8,'rays':len(s.n),'total_h_upper':r['total_h_upper'],'source_h_upper':r['source_error_upper_h'],'ce1i_h_upper':r['ce1i_total_h_upper'],'time_jump_h_upper':r['time_jump_error_upper_h'],'initial_h_upper':r['initial_error_upper_h'],'target_met':r['target_met'],'Emax':r['original_Emax'],'caps':[x['source_upper'] for x in r['panel_rows']],'elapsed_sec':time.perf_counter()-t,'sha256_source':hashlib.sha256(s.n.tobytes()+s.mass.tobytes()).hexdigest()}
open('/mnt/data/BASS_CE1M_20261029/REF8_FRESH.json','w').write(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
assert summary['target_met']
assert summary['total_h_upper']<1e-5
