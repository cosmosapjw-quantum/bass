"""Fair scoped source-matched table lookup benchmark, actual owner Rust vs NumPy.

One-time setup of the owner AxbiBackground and Python DOP853 is excluded from
the query medians and reported separately. Cross-language algorithmic speed is
not an EoR full-run speedup.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,tempfile,time,statistics
from pathlib import Path
import numpy as np

from axbi_provider import Background,Family,_read_lock
from rust_parity import read_owner

HERE=Path(__file__).resolve().parent
def run(repo:Path,target:Path,out:Path):
    if out.exists():raise FileExistsError(out)
    c=_read_lock();C=c['cosmology'];K=c['clock']
    src,head=read_owner(repo)
    cases=[(q,"PhysicalDensityFixed") for q in [0,.005,-.005,.01,-.01]]+[(.01,"SameHDiagnostic")]
    times=[]
    t0=time.perf_counter()
    sources=[Background(Family(q,family)) for q,family in cases]
    init_py=time.perf_counter()-t0
    for obj in sources:obj.table(501)
    checks=[]
    for _ in range(5):
        s=time.perf_counter()
        p=[obj.table(501) for obj in sources]
        times.append(time.perf_counter()-s)
        checks.append(sum(np.sum(a['proper_elapsed_s'])*1e-16+
                          np.sum(a['b'])+
                          np.sum(a['H_mean_per_s'])*1e15 for a in p))
    if not all(abs(x/checks[0]-1)<1e-14 for x in checks):
        raise ArithmeticError('UNSTABLE_FAST_BACKGROUND_REPEAT')
    with tempfile.TemporaryDirectory(prefix="bass_rei_bg_source_benchmark_") as tmp:
        root=Path(tmp);(root/'src').mkdir()
        (root/'Cargo.toml').write_text('[package]\nname="rei_bg_source_benchmark"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nrei_microphysics={path="'+src.as_posix()+'"}\n')
        (root/'src/main.rs').write_bytes((HERE/'rust_bridge/src/bench.rs').read_bytes())
        env=os.environ.copy()
        env['CARGO_TARGET_DIR']=str(target.resolve())
        env['CARGO_NET_OFFLINE']='true'
        args=['cargo','run','--release','--offline','--manifest-path',str(root/'Cargo.toml'),'--',
           str(C['H0_per_s']),str(C['Omega_m']),str(C['Omega_r']),str(C['Omega_lambda']),
           str(K['a_ref']),str(K['a_end']),'4096']
        r=subprocess.run(args,env=env,text=True,capture_output=True)
        if r.returncode!=0:raise RuntimeError(r.stderr[-1800:])
    rust=json.loads(r.stdout)
    if rust['n_cases']!=6 or rust['n_points_per_case']!=501:
        raise ValueError('RUST_BENCHMARK_SCHEMA_MISMATCH')
    outdata={'schema':'bass.rei.bg.authoritative_reference_vs_optimized_tensor.v1',
     'source_head':head,'source_rust_module':'AxbiBackground.point_at_scale',
     'same_physical_input':c,'owner_Rust_Simpson':rust,
     'python_optimized_DOP853':{'n_cases':6,'n_nodes':501,
        'median_vectorized_wall_s':statistics.median(times),
        'samples_wall_s':times,
        'one_time_build_all_s':init_py,
        'checksum_algebra_match_only':checks},
     'query_only_speedup':rust['median_wall_s']/statistics.median(times),
     'comparability':'Both same AX03 physical q signed cases and same 501 log scale nodes; Rust 4096-panel direct Simpson/point, Python pre-integrated DOP853 dense output; compare numerical parity separately (30 points and high precision); not identical computational algorithm or native coupled science speed',
     'owner_write_count':0,'owner_solver_started':0}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(outdata,indent=2)+'\n')
    print(json.dumps({k:v for k,v in outdata.items() if k!='same_physical_input'},indent=2)[:4200])
    return outdata

if __name__=='__main__':
    pa=argparse.ArgumentParser()
    pa.add_argument('--rei-repo',type=Path,required=True)
    pa.add_argument('--build-target',type=Path,required=True)
    pa.add_argument('--output',type=Path,required=True)
    v=pa.parse_args();run(v.rei_repo,v.build_target,v.output)
