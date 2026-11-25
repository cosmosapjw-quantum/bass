"""Matched one-axis changes around the actual C2K finest live BASS trajectory."""
import argparse,hashlib,json,subprocess,time,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
p=argparse.ArgumentParser()
p.add_argument('--prior',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
def sha(f):
    with open(f,'rb') as g:return hashlib.file_digest(g,'sha256').hexdigest()
old=json.loads(a.prior.read_text());base=old['finest'];exe=Path(base['command'][0])
assert sha(exe)==old['binary_sha256']
basepath=Path(old['raw'])/base['case']
for name,digest in base['hashes'].items():assert sha(basepath/name)==digest
a.out.mkdir(exist_ok=False)
pars=np.array([(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)])
binding=np.array([13.598434599702,24.587389011,54.41776])
def moments(E,N,nh):
    out=[]
    for eth,e0,s0,ya,p,yw,y0,y1 in pars:
        x=E/e0-y0;y=np.sqrt(x*x+y1*y1)
        out.append(np.where(E>=eth,s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18,0.))
    s=np.asarray(out);fac=2.99792458e10*nh*1e-6
    return fac*(s@N),fac*((s*(E[None,:]-binding[:,None]))@N)
def read(root,n,tol):
    h=np.genfromtxt(root/'history.tsv',names=True,delimiter='\t')
    pk=np.genfromtxt(root/'packets.tsv',names=True,delimiter='\t')
    uv=np.genfromtxt(root/'uv_exchange.tsv',names=True,delimiter='\t')
    rate=dict(l.split('=',1) for l in (root/'rate_control.txt').read_text().splitlines())
    assert len(h)==len(uv)==n+1 and np.all(np.diff(h['time_s'])>0)
    assert np.all(np.isfinite(h.view(float))) and np.all(h['Tm_K']>0)
    assert np.all((h['x_HII']>=0)&(h['x_HII']<=1)&(h['x_HeII']>=0)&(h['x_HeIII']>=0)&(h['x_HeII']+h['x_HeIII']<=1))
    assert np.min(pk['energy_eV'])>=13.6 and np.min(pk['N_per_H'])>=0
    assert abs(h['eta'][-1]-math.log(21/5))<2e-15
    E,N=pk['energy_eV'],pk['N_per_H'];g,q=moments(E,N,h['nH_m3'][-1])
    assert np.all(g>0) and np.all(q>0)
    assert abs(N.sum()-h['N'][-1])<2e-12*max(N.sum(),1e-30)
    assert abs(N@E-h['U_eV'][-1])<2e-12*max(N@E,1e-30)
    tau=float(np.trapezoid(299792458.*6.6524587051e-29*h['nH_m3']*h['xe']/h['H_s'],h['eta']))
    assert abs(tau/h['tau'][-1]-1)<2e-8
    ng=float(np.max(abs(h['number_defect'])/np.maximum(h['emitted_N'],1.)))
    eg=float(np.max(abs(h['energy_defect'])/np.maximum(h['emitted_U'],1.)))
    de=uv['current_U']+uv['absorbed_U']+uv['boundary_U']+uv['geometry_U']-uv['emitted_U']
    ue=float(np.max(abs(de)/np.maximum(uv['emitted_U'],1e-30)))
    assert max(ng,eg)<1e-8 and ue<1e-9
    assert float(rate['max_group_relative'])<=tol/2 and float(rate['max_final_relative'])<=tol
    return dict(tau=tau,terminal={k:float(h[k][-1]) for k in ('x_HII','x_HeII','x_HeIII','Tm_K','N','U_eV','xe')},gamma=g.tolist(),heat=q.tolist(),ng=ng,eg=eg,uv_gap=ue,guard=rate,peak_packets=int(np.max(h['packets'])),hashes={f.name:sha(f) for f in root.iterdir() if f.is_file()}),h
baseline,bh=read(basepath,32768,1e-4)
def run(c):
    name,n,sub,tol=c;root=a.out/name
    cmd=list(base['command']);cmd[1]=str(root);cmd[3]=str(n);cmd[5]=str(sub);cmd[-1]=str(tol)
    t=time.monotonic();r=subprocess.run(cmd,capture_output=True,text=True,timeout=240)
    if r.returncode:
        return dict(name=name,command=cmd,returncode=r.returncode,stderr=r.stderr,wall_s=time.monotonic()-t)
    result,h=read(root,n,tol)
    zz=np.linspace(0,bh['eta'][-1],20001)
    result.update(name=name,n=n,sub=sub,tol=tol,command=cmd,returncode=0,wall_s=time.monotonic()-t,
      terminal_delta={k:result['terminal'][k]-baseline['terminal'][k] for k in baseline['terminal']},
      gamma_relative=(np.array(result['gamma'])/baseline['gamma']-1).tolist(),
      heat_relative=(np.array(result['heat'])/baseline['heat']-1).tolist(),
      history_max_abs={k:float(np.max(abs(np.interp(zz,h['eta'],h[k])-np.interp(zz,bh['eta'],bh[k])))) for k in ('x_HII','x_HeII','x_HeIII','Tm_K')})
    print(name,{k:result[k] for k in ('tau','terminal_delta','gamma_relative','peak_packets','wall_s')},flush=True)
    return result
cases=[('time2',65536,16,1e-4),('spec2',32768,32,1e-4),('spec4',32768,64,1e-4),('guard10',32768,16,1e-5),('cross',65536,32,1e-5)]
with ThreadPoolExecutor(max_workers=3) as pool:
    rows=list(pool.map(run,cases))
a.receipt.write_text(json.dumps(dict(scope='actual live BASS, same IC and FLRW geometry, controlled time/source quadrature/local guard changes; no global convergence theorem',prior_sha256=sha(a.prior),binary_sha256=sha(exe),baseline=baseline,results=rows),indent=2,allow_nan=False)+'\n')
