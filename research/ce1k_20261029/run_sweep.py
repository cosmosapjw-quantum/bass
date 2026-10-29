import json,time,os,sys,hashlib
from pathlib import Path
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_tabulated_source_canonical import run_canonical_panel_source
p=Path(__file__).parent/'SWEEP_IN_PROGRESS.json'
result={'project':'BASS','node':'CE1-K','science':'canonical-PR246+source-local-PR247','base_head':'4474f8acb13614ffda7a30524a815976e306efc9','donor_head':'bd94bf270dcbf3bf140ac6cf7a7caf7e72532ac0','target':1e-5,'upper_dag':'9/15','rows':[]}
for ref in [1,2,4,8]:
    t0=time.perf_counter()
    source=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=ref,backend='python_oracle')
    a=run_canonical_panel_source(source,backend='python_oracle')
    row={'refinement':ref,'rays':len(source.n),'total_h_upper':a['total_h_upper'],'ce1i_total_h_upper':a['ce1i_total_h_upper'],'source_h_upper':a['source_error_upper_h'],'time_jump_h_upper':a['time_jump_error_upper_h'],'initial_h_upper':a['initial_error_upper_h'],'source_caps':[z['source_upper'] for z in a['panel_rows']],'geometry_lowers':[z['certified_lower_logscale'] for z in a['panel_rows']],'sha':a['source_and_path_sha256'],'target_met':a['target_met'],'elapsed_seconds':time.perf_counter()-t0}
    result['rows'].append(row)
    p.write_text(json.dumps(result,indent=2))
    print(json.dumps(row),flush=True)