#!/usr/bin/env python3
"""CE1-W model-generated Bianchi-I angular-geometry response, no CMB temperature."""
import csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research.ce1t_20261030.cellwise_gl_rust import make_cell_rays, frozen_source_identity
SOURCE="022e6548c0a8562c20cc819667f1a9a002af9db7bc250a5148ffa692b4223035"
PIN={6:"6eff8cd9f31d027bbee55720332302b6fbad71b3639b5809aab6b9ce6f53e489",
     8:"1398980ec71662494273e05eb4bd52a78f6e6c7f208702638da6c739698f7502"}
RAY={6:"6f6e5d0797404521abd51cb8394a8b2beca3e96b392924b9ad30b2093098d957",
     8:"90e29d100d35dc7ac31f9d75f7d6d4c2d423d90ad487ec0922246bc8f39891cb"}
MASS={6:"56cb2c5baabdcf10355cc7ddf2f1cf41ad8a131d890e285320e39bab52758199",
      8:"2c0b9ca7d1845458639217fae0a86b3339c32f57f9f71dd6c649c3408d319a79"}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(n):
    assert frozen_source_identity()==SOURCE
    q,m=make_cell_rays(n)
    assert sha(q.tobytes())==RAY[n] and sha(m.tobytes())==MASS[n]
    p=ROOT/"research/ce1v_20261030/inputs"/f"GL{n}_coupled_41epochs.csv"
    assert sha(p.read_bytes())==PIN[n]
    with p.open(newline="") as f: rows=list(csv.DictReader(f))
    assert len(rows)==41
    cols=("u","E","P1","P2","P3","ell1","ell2","ell3","a20","a22","a40","a42","a44")
    data={z:np.array([float(row[z]) for row in rows]) for z in cols}
    assert np.max(abs(data["u"]-np.linspace(0,.08,41)))<2e-15
    return q,m,data
def polynomials(t):
    x,y,z=t.T
    A=math.sqrt(5/(16*math.pi));B=math.sqrt(15/(32*math.pi))
    C=3/(16*math.sqrt(math.pi));D=3/8*math.sqrt(5/(2*math.pi));F=3/16*math.sqrt(35/(2*math.pi))
    v=np.stack([A*(3*z-1),B*(x-y),C*(35*z*z-30*z+3),D*(x-y)*(7*z-1),F*(x*x-6*x*y+y*y)],axis=1)
    g=np.zeros((len(t),5,3))
    g[:,0,2]=3*A
    g[:,1,0]=B;g[:,1,1]=-B
    g[:,2,2]=C*(70*z-30)
    g[:,3,0]=D*(7*z-1);g[:,3,1]=-D*(7*z-1);g[:,3,2]=7*D*(x-y)
    g[:,4,0]=F*(2*x-6*y);g[:,4,1]=F*(2*y-6*x)
    return v,g
def response(ell,q,m):
    v=q*np.exp(-ell)
    r=np.linalg.norm(v,axis=1)
    t=(v/r[:,None])**2
    W=m*np.exp(-ell.sum())*r
    E=W.sum();P=np.einsum("n,ni->i",W,t)
    Y,g=polynomials(t)
    a=np.einsum("n,nk->k",W,Y)
    da=np.zeros((5,3))
    for j in range(3):
        dt=2*t*(t[:,j,None]-np.eye(3)[j])
        dY=np.einsum("nki,ni->nk",g,dt)
        da[:,j]=np.einsum("n,nk->k",W,dY-Y*(1+t[:,j,None]))
    alpha=(4*math.pi/E)*a
    dalpha=(4*math.pi/E)*(da+a[:,None]*(1+P[None,:]/E))
    return E,P,a,alpha,dalpha
def build(n,out):
    q,m,d=read(n)
    E=[];a=[];alpha=[];dalpha=[]
    names=["a20","a22","a40","a42","a44"]
    for i in range(41):
        ell=np.array([d[f"ell{j}"][i] for j in range(1,4)])
        en,p,aa,al,dal=response(ell,q,m)
        assert abs(en-d["E"][i])<5e-13
        assert np.max(abs(p-np.array([d[f"P{j}"][i] for j in range(1,4)])))<5e-13
        assert np.max(abs(aa-np.array([d[z][i] for z in names])))<4e-12
        assert np.max(abs(dal.sum(axis=1)))<8e-12
        E.append(en);a.append(aa);alpha.append(al);dalpha.append(dal)
    a=np.array(a);alpha=np.array(alpha);dalpha=np.array(dalpha)
    with (out/f"GL{n}_response_41.csv").open("w",newline="") as f:
        c=["u","E"]+sum(([key,"delta_"+key]+[f"delta_{key}_dell{j}" for j in (1,2,3)] for key in names),[])
        w=csv.writer(f);w.writerow(c)
        for i in range(41):
            v=[d["u"][i],E[i]]
            for k in range(5):v.extend([a[i,k],alpha[i,k],*dalpha[i,k,:]])
            w.writerow([format(x,".17g") for x in v])
    summary={}
    with (out/f"GL{n}_two_time_transfer_1681.csv").open("w",newline="") as f:
        cols=["u","v"]+[f"K{l}delta" for l in (2,4)]+[f"dK{l}_{slot}{j}" for l in (2,4) for slot in ("u","v") for j in (1,2,3)]
        w=csv.writer(f);w.writerow(cols)
        store={}
        for l,ix,weight in [(2,[0,1],[1.,2.]),(4,[2,3,4],[1.,2.,2.])]:
            A=alpha[:,ix];D=dalpha[:,ix,:];ww=np.array(weight)
            K=(A*ww)@A.T/(2*l+1)
            Du=np.einsum("imj,km,m->ikj",D,A,ww)/(2*l+1);Dv=Du.transpose(1,0,2)
            assert np.max(abs(K-K.T))<2e-13
            assert np.max(abs(Du-Dv.transpose(1,0,2)))<2e-13
            assert np.min(np.linalg.eigvalsh(K))>-2e-12
            assert np.max(abs(Du.sum(axis=2)))<5e-12
            np.savez_compressed(out/f"GL{n}_K{l}_response.npz",u=d["u"],K=K,Du=Du,Dv=Dv)
            summary[str(l)]={"K_0_end":float(K[0,-1]),"dK_0_end_initial_geometry":Du[0,-1].tolist(),
                             "dK_0_end_final_geometry":Dv[0,-1].tolist(),
                             "max_common_scale_gap":float(np.max(abs(Du.sum(axis=2))))}
            store[l]=(K,Du,Dv)
        for i in range(41):
            for j in range(41):
                v=[d["u"][i],d["u"][j]]
                v.extend([store[l][0][i,j] for l in (2,4)])
                for l in (2,4):
                    v.extend(store[l][1][i,j]);v.extend(store[l][2][i,j])
                w.writerow([format(x,".17g") for x in v])
    return summary
def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--out",default="research/ce1w_20261030/data")
    opt=ap.parse_args();out=Path(opt.out);out.mkdir(parents=True,exist_ok=True)
    values={f"GL{n}":build(n,out) for n in (6,8)}
    meta={"schema":"bass.ce1w.geometry_transfer.v1","original_source_sha256":SOURCE,"parent_pr":267,
          "upper_dag":"9/15","physics":"82 single-time records and 3362 unequal-time sensitivity records",
          "status":"BINARY64_MODEL_DATA_NOT_FULL_CONTINUUM_CERTIFICATE","data":values}
    (out/"RESULTS.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("CE1W_PHYSICAL_MODEL_RESPONSE_PASS",json.dumps(values))
if __name__=="__main__":main()
