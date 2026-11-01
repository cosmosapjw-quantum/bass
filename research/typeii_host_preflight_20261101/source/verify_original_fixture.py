"""BASS Type-II 401-sample nonproduction physical chart/host contract validator.

If --require-original: read exact GitHub main fixture file and verify source Git blob.
Otherwise: independently regenerate the prescribed 401 RK4 background samples;
label this LOCAL_FORMULA_REDERIVATION, never byte-identical owner-fixture proof.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
SQ3=math.sqrt(3.0)
ROOT=Path(__file__).resolve().parents[1]
SOURCE_LOCK=json.loads((ROOT/'SOURCE_LOCK.json').read_text())
FIXTURE=Path('compiler/validation/typeii_fixture_canonical.json')
GAMMA=1.3
INITIAL=(.2375,0.,-.11295198246134101,.865,.05)

class BadPhysicalState(ValueError): pass

def gauss_omega(x):
    sp,sm,s13,n1,v=x
    return 1.0-sp*sp-sm*sm-s13*s13-n1*n1/12.0

def source_rhs(x,gamma=GAMMA):
    """Independent analytic 5-state identity, source `class_a_tilted` aligned invariant slice."""
    sp,sm,s13,n1,v=x
    omega=gauss_omega(x);v2=v*v
    gp=1+(gamma-1)*v2;gm=1-(gamma-1)*v2
    sigma2=sp*sp+sm*sm+s13*s13
    qdec=2*sigma2+.5*((3*gamma-2)+(2-gamma)*v2)*omega/gp
    sig22=sp+SQ3*sm
    t=((3*gamma-4)*(1-v2)+(2-gamma)*sig22*v2)/gm
    return (-(2-qdec)*sp+n1*n1/3+gamma*omega*v2/(2*gp)-3*s13*s13,
        -(2-qdec)*sm+SQ3*gamma*omega*v2/(2*gp)+SQ3*s13*s13,
        s13*(-(2-qdec)+3*sp-SQ3*sm),
        (qdec-4*sp)*n1,
        v*(t-sig22))

def rk4_fixture():
    t=[];states=[];y=INITIAL
    for j in range(401):
        t.append(j*.0005);states.append(y)
        if j==400:break
        dt=.0005;f1=source_rhs(y)
        f2=source_rhs(tuple(a+dt*b/2 for a,b in zip(y,f1)))
        f3=source_rhs(tuple(a+dt*b/2 for a,b in zip(y,f2)))
        f4=source_rhs(tuple(a+dt*b for a,b in zip(y,f3)))
        y=tuple(a+dt*(b+2*c+2*d+e)/6 for a,b,c,d,e in zip(y,f1,f2,f3,f4))
    return t,states

def from_four(sp,sm,n1,v,gamma=GAMMA):
    if not all(math.isfinite(q) for q in (sp,sm,n1,v,gamma)):
        raise BadPhysicalState('NONFINITE')
    if not 0<gamma<2:raise BadPhysicalState('GAMMA_OUTSIDE')
    if not n1>0:raise BadPhysicalState('TYPE_I_BOUNDARY')
    if not abs(v)<1:raise BadPhysicalState('TACHYONIC')
    budget=1-sp*sp-sm*sm-n1*n1/12
    if budget<=0:raise BadPhysicalState('NEGATIVE_BUDGET')
    gp=1+(gamma-1)*v*v
    beta=3*gamma**2*v*v/(n1*n1*gp*gp)
    omega=2*budget/(1+math.sqrt(1+4*beta*budget))
    sigma13=-SQ3*gamma*omega*v/(n1*gp)
    return omega,sigma13,beta

def metric_mock(s):
    sp,sm,s13,n1,v=s
    return {'shear5':[-2*sp,sp+SQ3*sm,0.0,SQ3*s13,0.0],
            'n6':[n1,0.0,0.0,0.0,0.0,0.0],
            'a3':[0.0]*3,'v3':[0.0,v,0.0],'omega':gauss_omega(s),
            'gamma':GAMMA,'norm':'BASS_WE','time':'HUBBLE_EFOLD','frame':'NORMAL'}

def decode_mock(h):
    if any(abs(h[k][i])>1e-14 for k,ids in [('shear5',[2,4]),('n6',[1,2,3,4,5]),
        ('a3',[0,1,2]),('v3',[0,2])] for i in ids):raise BadPhysicalState('OFF_SLICE')
    if (h['norm'],h['time'],h['frame'])!=('BASS_WE','HUBBLE_EFOLD','NORMAL'):
        raise BadPhysicalState('WRONG_CONVENTION')
    sp=-h['shear5'][0]/2
    sm=(h['shear5'][1]-sp)/SQ3
    s13=h['shear5'][3]/SQ3
    n1=h['n6'][0];v=h['v3'][1]
    om4,_,_=from_four(sp,sm,n1,v,h['gamma'])
    got=(sp,sm,s13,n1,v)
    gp=1+(h['gamma']-1)*v*v
    cod=-SQ3*n1*s13-3*h['gamma']*gauss_omega(got)*v/gp
    if abs(cod)>1e-12:raise BadPhysicalState('CODAZZI')
    if abs(om4-h['omega'])>1e-12:raise BadPhysicalState('GAUSS')
    return got

def _blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()

def owner_guard(root:Path, require:bool):
    if not require:return {'claimed':'NO','status':'LOCAL_SOURCE_EQUIVALENT_REDERIVATION'}
    bad=[]
    for path,sha in SOURCE_LOCK['original_git_blobs_sha1'].items():
        p=root/path
        if not p.is_file():bad.append(f'MISSING:{path}')
        elif _blob(p)!=sha:bad.append(f'DRIFT:{path}')
    if bad:raise RuntimeError('SOURCE_OWNER_IDENTITY_FAILURE '+str(bad))
    return {'claimed':'YES','status':'EXACT_GIT_BLOB_VERIFIED','count':len(SOURCE_LOCK['original_git_blobs_sha1'])}

def analyze(root:Path,require_original:bool):
    guard=owner_guard(root,require_original)
    if require_original:
        obj=json.loads((root/FIXTURE).read_text())
        samples=obj['trajectory']['samples']
        times=[s['tau'] for s in samples];states=[tuple(s['state']) for s in samples]
        if len(states)!=401:raise RuntimeError('ORIGINAL_401_MISSING')
        original_rhs=[s['rhs'] for s in samples]
    else:
        times,states=rk4_fixture();original_rhs=None
    max_cod=0.;max_s13=0.;max_om=0.;max_round=0.;max_rhs=0.;min_abs_rank=math.inf
    rows=[]
    for j,(tau,s) in enumerate(zip(times,states)):
        sp,sm,s13,n1,v=s;omega=gauss_omega(s)
        omega4,s134,beta=from_four(sp,sm,n1,v)
        gp=1+(GAMMA-1)*v*v
        cod=-SQ3*n1*s13-3*GAMMA*omega*v/gp
        minor=-SQ3*n1*(1+2*beta*omega4)
        if minor>=0:raise RuntimeError('SINGULAR_CONSTRAINT_RANK')
        if original_rhs is not None:
            max_rhs=max(max_rhs,max(abs(a-b) for a,b in zip(source_rhs(s),original_rhs[j])))
        host=metric_mock(s)
        roundtrip=decode_mock(host)
        gap=max(abs(a-b) for a,b in zip(s,roundtrip))
        max_cod=max(max_cod,abs(cod));max_s13=max(max_s13,abs(s13-s134))
        max_om=max(max_om,abs(omega-omega4));max_round=max(max_round,gap)
        min_abs_rank=min(min_abs_rank,abs(minor))
        rows.append((j,tau,sp,sm,n1,v,s13,s134,omega,omega4,cod,minor,gap))
    summary=dict(schema='bass.typeii.mock_host_exact_constraint.v1',source=guard,
        original_parent=SOURCE_LOCK['immutable_parent_head'],original_main=SOURCE_LOCK['original_main_commit'],
        physical_rows=len(rows),max_codazzi=max_cod,max_reconstruction_sigma13=max_s13,
        max_reconstruction_omega=max_om,max_mock_roundtrip=max_round,
        max_source_rhs_gap=max_rhs,minimum_abs_constraint_minor=min_abs_rank,
        domain='original 5-state *embedded* four-dimensional TypeII constraint slice, gamma=1.3',
        production_ready=False,real_rustcore_compiled=False)
    if max(max_cod,max_s13,max_om,max_round,max_rhs)>1e-11:
        raise RuntimeError('PHYSICS_PARITY_FAILURE '+str(summary))
    return rows,summary

def write(root:Path,output:Path,require_original:bool):
    output.mkdir(parents=True,exist_ok=True)
    rows,record=analyze(root,require_original)
    with (output/'TYPEII_401_PHYSICAL_CHART.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['index','tau','SigmaPlus','SigmaMinus','N1','v2',
                'stored_Sigma13','chart_Sigma13','stored_Omega','chart_Omega','Codazzi','constraint_minor','mock_roundtrip']);w.writerows(rows)
    (output/'TYPEII_HOST_CHART_RESULTS.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    return record

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo-root',type=Path,default=Path.cwd())
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--require-original',action='store_true')
    a=p.parse_args()
    result=write(a.repo_root,a.output,a.require_original)
    print(json.dumps(result,indent=2))