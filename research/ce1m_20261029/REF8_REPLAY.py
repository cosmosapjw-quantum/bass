"""CE1-M frozen ref8 exact-source/path numeric replay, no production claim."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
import numpy as np
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_tabulated_source_canonical import certify_canonical_panel_source


def digest(a):
    return hashlib.sha256(np.asarray(a).tobytes()).hexdigest()


def run():
    source=TabulatedRadiation([0,.5,1],[0,.25,.75,1],
        [[.1,.25,.05],[.2,.15,.15]],refinement=8,backend='python_oracle')
    path=rk4_path(source,source.initial_state(),.08,4,backend='python_oracle')
    start=time.perf_counter()
    out=certify_canonical_panel_source(source,path)
    receipt={
        'refinement':8,'rays':len(source.mass),
        'source_sha256':digest(source.n)+':'+digest(source.mass),
        'path_sha256':digest(path.states)+':'+digest(path.coefficients)+':'+digest(path.times),
        'h_bound':out['total_h_upper'],
        'source_h_bound':out['source_error_upper_h'],
        'previous_ce1i_h_bound':out['ce1i_total_h_upper'],
        'target_h':out['target_h'],'target_met':out['target_met'],
        'initial_h_bound':out['initial_error_upper_h'],
        'time_jump_h_bound':out['time_jump_error_upper_h'],
        'panel_m':[x['certified_lower_logscale'] for x in out['panel_rows']],
        'panel_eta':[x['source_upper'] for x in out['panel_rows']],
        'elapsed_seconds':time.perf_counter()-start,
        'production_ready':False,'upper_dag':'9/15'
    }
    assert receipt['source_sha256']==(
        '9d46624cdb747a5760eda945d5effeb17f0619ade2b7198ee1700903123455ba:'
        'c421e8148af743ea44bbb565f32a44090e18299e0e0b15f20eee37fb0a232211')
    assert receipt['path_sha256']==(
        'f877fdfdaf1b70b7a5f3f6cf886811f41ab8df1d9d80c1933cdbead018847c11:'
        '2ee96a50407161abd2ca8c0ea6a02917ac5273dfab837c78e846bd83a3983615:'
        '85b560f90a994c59b320e6ad4256f7909f796eb1c697f9260ff47707d3dafd3e')
    assert receipt['target_met'] and receipt['h_bound']<1e-5
    assert receipt['h_bound']<=receipt['previous_ce1i_h_bound']
    assert abs(receipt['h_bound']-9.411551484445186e-6)<2e-15
    print(json.dumps(receipt,indent=2,sort_keys=True))
    print('CE1M_REF8_CORRECT_PHYSICAL_LOCK_AND_SOURCE_SCOPED_PASS')
    return receipt


if __name__=='__main__':
    run()
