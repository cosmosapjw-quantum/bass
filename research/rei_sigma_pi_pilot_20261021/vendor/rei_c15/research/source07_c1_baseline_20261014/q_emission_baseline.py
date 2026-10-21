"""C1 source-only fixed-q projection. No gas/transport ODE or active job mutation."""
from __future__ import annotations
import argparse,json,hashlib,math
from pathlib import Path
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad

KB=8.617333262145e-5
G=6.67430e-8
MP=1.67262192595e-24
LO,HI=13.6,100.0
CUTS=(24.59,54.42)
TSTAR=50000.

class Scenario:
    def __init__(self,repo):
        self.repo=Path(repo)
        self.data=json.loads((self.repo/"research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json").read_text())
        c=self.data["cosmology"]
        self.ar=self.data["interval"]["a_ref"]
        self.h0=c["h0_km_s_mpc"]*1e5/c["mpc_cm"]
        self.om=c["omega_m"];self.orad=c["omega_r"];self.ol=1-self.om-self.orad
        self.nh=(1-c["helium_mass_fraction"])*(0.0224/0.674**2)*3*self.h0**2/(8*math.pi*G*MP)
        self.mpc=c["mpc_cm"]
        self.xi=10**(1/(0.00038*0.002**0.227+0.01858)-math.log10(2.55))
    def hf(self,a):
        return self.h0*math.sqrt(self.om/a**3+self.orad/a**4+self.ol)
    def shear(self,a,q):
        return q*self.hf(self.ar)*(self.ar/a)**3
    def hubble(self,a,q):
        return math.hypot(self.hf(a),self.shear(a,q))
    @lru_cache(maxsize=256)
    def b(self,a,q):
        if q==0 or a==self.ar:return 0.
        f=lambda x:self.shear(self.ar*math.exp(x),q)/self.hubble(self.ar*math.exp(x),q)
        return quad(f,0,math.log(a/self.ar),epsabs=1e-13,epsrel=1e-12)[0]
    def ratios(self,a,q):
        b=self.b(a,q);r=self.ar/a
        return r*math.exp(b),r*math.exp(-2*b)
    def rate(self,a):
        zp=1/a
        psi=.015*zp**2.7/(1+(zp/2.9)**5.6)
        return .2*self.xi*psi/(self.nh*self.mpc**3)
    def total_emitted(self,q):
        f=lambda x:self.rate(self.ar*math.exp(x))/self.hubble(self.ar*math.exp(x),q)
        return quad(f,0,math.log(.2/self.ar),epsabs=3e-11,epsrel=1e-12)[0]

class Spectrum:
    def __init__(self):
        x,w=leggauss(128)
        e=(LO+HI)/2+(HI-LO)/2*x
        self.norm=float(np.dot(w,self.raw(e))*(HI-LO)/2)
    @staticmethod
    def raw(E):
        e=np.asarray(E,dtype=float)
        return e**2/np.expm1(e/(KB*TSTAR))
    def phi(self,E):
        return self.raw(E)/self.norm
    def project(self,sc,z,q,eref_high=433.,nmu=24,ne=24,omit_R=False):
        """E* is reference energy; proper photon number per E* dOmega*.
        Its Jacobian is R*J, with J=det(A)/R^3.
        """
        a=1/(1+z);rp,rz=sc.ratios(a,q)
        mu,wm=leggauss(nmu);x,wx=leggauss(ne)
        accum=np.zeros(6)
        for m,mw in zip(mu,wm):
            R=math.hypot(rp*math.sqrt(max(0,1-m*m)),rz*m)
            J=(sc.ar/a)**3/R**3
            l=max(LO,LO/R);h=min(eref_high,HI/R)
            if h<=l:continue
            knots=[l]+sorted(t/R for t in CUTS if l<t/R<h)+[h]
            for left,right in zip(knots[:-1],knots[1:]):
                eref=(left+right)/2+(right-left)/2*x
                e=eref*R
                v=wx*((right-left)/2)*self.phi(e)*J*(1 if omit_R else R)*mw/2
                accum[0]+=sum(v)
                accum[1]+=sum(v*e)
                if left>=CUTS[0]/R-1e-12:
                    accum[2]+=sum(v)
                    accum[4]+=sum(v*(e-CUTS[0]))
                if left>=CUTS[1]/R-1e-12:
                    accum[3]+=sum(v)
                    accum[5]+=sum(v*(e-CUTS[1]))
        return [float(y) for y in accum]

def sufficient_support():
    return 420*4.2**.02

def accumulated_capture(sc,sp,q,eref_hi=100.,nmu=24,ne=16):
    limit=math.log(.2/sc.ar)
    def fn(logratio):
        a=sc.ar*math.exp(logratio)
        m=sp.project(sc,1/a-1,q,eref_hi,nmu,ne)
        return sc.rate(a)/sc.hubble(a,q)*m[0]
    return quad(fn,0.,limit,epsabs=2e-9,epsrel=1e-9)[0]

def evaluate(repo,output):
    sc=Scenario(repo); sp=Spectrum();out=Path(output);out.mkdir(parents=True,exist_ok=True)
    cases=[-.01,-.005,0.,.005,.01]
    count={f"{q:+.4f}":sc.total_emitted(q) for q in cases}
    support={f"{q:+.4f}":100/min(sc.ratios(.2,q)) for q in cases}
    captured={f"{q:+.4f}":accumulated_capture(sc,sp,q,100.) for q in cases}
    zgrid=np.linspace(20,4,25)
    progress={}
    for q in [-.01,0.,.01]:
        tag=f"{q:+.4f}"
        progress[tag]=[sp.project(sc,float(z),q,100.,24,16)[0] for z in zgrid]
    full={}
    for q in cases:
        full[f"{q:+.4f}"]={str(z):sp.project(sc,z,q,sufficient_support()+.01,32,32)
                              for z in (20.,12.,8.,4.)}
    correct=sp.project(sc,4.,0.,sufficient_support()+.01)
    omission=sp.project(sc,4.,0.,sufficient_support()+.01,omit_R=True)
    result={"scenario_id":sc.data["scenario_id"],"scope":"source-only q-emissivity numerical baseline",
        "source_revisions":{f:hashlib.sha256((Path(repo)/f).read_bytes()).hexdigest()
           for f in ["rust/rei_microphysics/src/axbi_sources.rs",
                     "rust/rei_microphysics/src/axbi_background.rs",
                     "rust/rei_microphysics/src/bianchi_i.rs"]},
        "number_per_H_z20_to4":count,"captured_per_H_with_100eV_fixed_q_ref":captured,
        "integrated_loss_fraction_with_100eV_fixed_q_ref":{k:1-captured[k]/count[k] for k in count},"z4_support_high_eV":support,
        "safe_support_high_eV":sufficient_support(),
        "complete_moments":full,"ref_normalization":sp.norm,
        "FLRW_z4_truncation_fraction":1-progress["+0.0000"][-1],
        "FLRW_z4_missing_R_factor":omission[0]/correct[0],
        "z_grid":zgrid.tolist(),"truncated_counts":progress}
    (out/"RESULT.json").write_text(json.dumps(result,indent=2))
    with (out/"COMPLETENESS.csv").open("w") as f:
        f.write("zbar,"+",".join(progress)+"\n")
        for i,z in enumerate(zgrid):
            f.write(",".join([str(z)]+[format(progress[c][i],".17g") for c in progress])+"\n")
    return result

def plot_result(result,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8.5,4.5))
    for label,counts in result["truncated_counts"].items():
        ax.plot(result["z_grid"],100*np.asarray(counts),label=f"q_ref={label}")
    ax.set_xlim(20,4);ax.set_ylim(0,103)
    ax.set_xlabel("Mean redshift");ax.set_ylabel("Newly emitted photons retained (%)")
    ax.set_title("Hypothetical fixed-q E* <= 100 eV, not the current production grid")
    ax.legend();ax.grid(alpha=.3);fig.tight_layout()
    fig.savefig(Path(out)/"COMPLETENESS.png",dpi=170);plt.close(fig)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=evaluate(args.repo,args.out)
    plot_result(result,args.out)
    for key in ("number_per_H_z20_to4","captured_per_H_with_100eV_fixed_q_ref",
                "integrated_loss_fraction_with_100eV_fixed_q_ref","z4_support_high_eV",
                "safe_support_high_eV","FLRW_z4_truncation_fraction",
                "FLRW_z4_missing_R_factor"):
        print(key,result[key])
