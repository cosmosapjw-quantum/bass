#!/usr/bin/env python3
"""BASS Thomson first-collision gain from actual REI-F08 S0 13.7-eV photon birth.

Prescribed constant-H Bianchi I, source F08 saved H/He evolution, original
photoelectric H I Verner96 fit; unscattered photon characteristics integrated
from every birth cohort. No real S0 full-solver or CMB claim.
"""
from __future__ import annotations
import argparse,bisect,csv,gzip,hashlib,io,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"source_inputs"
SHA={
"S0_BI.csv.gz":"3096dc923520ec98da8c2e1dd3f03605cbf0809e944eeb5e4ceb6f58eff58893",
"S0_FLRW.csv.gz":"cab6e37e0f375e06dc03218067fa74fe3f14455e2dcf41a03051965008acb521",
"S0_BI-electron_density.csv.gz":"663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
"S0_FLRW-electron_density.csv.gz":"0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
"science_scenario_v1.json":"c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
"S0_BI-independent_history_receipt.json":"a86ffe981c4f721e9a4d9b6109cb53d14893e4b2e0a4a3f06c70062e1181722f",
"S0_BI-summary.json":"809391a8f16bc195b366ac0fa8acdd7ea8e6260dbea2c246ed795d8caa38ef63",
"S0_FLRW-summary.json":"0c30a98499f968610a51456ac1697626c5fc5ae19233c4989f36edf6b762664d",
"source_manifest.json":"3b1e753e77a82d8cfdce9decf9c7dd92e2db3dc85e9708af33fba03bde7a045d",
"REI_ORIGINAL_atomic_provider.rs":"b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3",
"REI_ORIGINAL_paired_runtime.rs":"b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7",
"REI_ORIGINAL_paired_history.rs":"b4f2bd67f0276766792ac8ff6dd53f314c5d507def726d8524a8af5b4bd076a3",
}
# Fixed owner in rust/rei_microphysics/src/atomic_provider.rs, SHA-256
ATOMIC_OWNER="b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3"
C=29979245800.0
SIG_T=6.6524587051e-25
THRESHOLD=13.60
BIRTH_EV=13.7
SOURCE_RATE=5e-15
INITIAL_COUNT=0.05
HAVG=1e-14
END=1e13
EPOCH_INDEX=(4000,8000,12000,16000)
SCHEMA="BASS_REI_F08_S0_TRUE_BIRTH_HI_ABS_THOMSON_GAIN_V1"

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def sigma_hi(E):
    """Exact scalar functional form/params of original Verner96 AtomicProvider::HI."""
    if not math.isfinite(E) or E<0 or E>50000:
        raise ValueError("source atomic owner energy-domain guard")
    if E<THRESHOLD:
        return 0.0
    x=E/0.4298
    y=abs(x)
    return 5.475e4*((x-1)**2)*y**(2.963/2-5.5)*(
        1+math.sqrt(y/32.88))**(-2.963)*1e-18

class History:
    def __init__(self,label,curve,elec,scenario):
        self.label=label
        self.H=tuple(scenario["background"]["pairs"]["BIANCHI_I" if label=="S0_BI" else "FLRW"]["H_per_s"])
        self.times=[0.];self.xh=[.9];self.ne=[];self.nh=[];self.nhi=[]
        with gzip.open(SOURCE/curve,"rt",newline="") as f:
            self.original=list(csv.DictReader(f))
        with gzip.open(SOURCE/elec,"rt",newline="") as f:
            rows=list(csv.DictReader(f))
        if len(self.original)!=16000 or len(rows)!=16001:
            raise ValueError("original F08 16000 interval support missing")
        for i,r in enumerate(rows):
            t=float(r["normal_time_s"]); nh=float(r["nH_proper_cm3"]);ne=float(r["ne_proper_cm3"])
            if t!=(i*6.25e8) or not all(math.isfinite(v) for v in (t,nh,ne)) or nh<=0 or ne<=0:
                raise ValueError("original exact F08 proper clock/density mismatch")
            if abs(nh/(1e-4*math.exp(-3*HAVG*t))-1)>6e-12:
                raise ValueError("original F08 proper H volume identity")
            self.ne.append(ne);self.nh.append(nh)
            if i:
                row=self.original[i-1]
                if float(row["time_s"])!=t:
                    raise ValueError("original F08 time key mismatch")
                xh,x2,x3=(float(row[k]) for k in ("x_HII","x_HeII","x_HeIII"))
                if not (0<=xh<=1 and 0<=x2 and 0<=x3 and x2+x3<=1+1e-12):
                    raise ValueError("original HHe charge fraction impossible")
                if abs((nh*(xh+.083*(x2+2*x3)))/ne-1)>1e-12:
                    raise ValueError("original F08 HHe electron history charge mismatch")
                self.times.append(t);self.xh.append(xh)
        self.nhi=[nh*(1-x) for nh,x in zip(self.nh,self.xh)]
        self.tauprefix=[0.]
        for i in range(16000):
            self.tauprefix.append(self.tauprefix[-1]+SIG_T*C*6.25e8*(
                self.ne[i]+self.ne[i+1])/2)
        if any(v<=0 for v in self.nhi):
            raise ValueError("original F08 neutral H must remain positive for this S0 study")
        self.original_source_physical_HI=self.nhi[-1]
    def linear(self,values,t):
        if t<0 or t>END:raise ValueError("outside F08 original clock")
        if t==END:return values[-1]
        i=min(int(t/6.25e8),15999)
        f=(t-self.times[i])/6.25e8
        return values[i]*(1-f)+values[i+1]*f
    def tau_electron(self,t):
        if t==END:return self.tauprefix[-1]
        if t<0 or t>END:raise ValueError("outside REI owner time")
        i=min(int(t/6.25e8),15999); d=t-self.times[i]
        nend=self.ne[i]+d/6.25e8*(self.ne[i+1]-self.ne[i])
        return self.tauprefix[i]+C*SIG_T*d*(self.ne[i]+nend)/2

def source_histories():
    for name,h in SHA.items():
        if digest(SOURCE/name)!=h:
            raise ValueError("original F08 source SHA256 mismatch: "+name)
    sc=json.loads((SOURCE/"science_scenario_v1.json").read_text())
    if sc["source"]["family"]!="S0" or sc["source"]["energy_at_birth_ev"]!=BIRTH_EV or sc["source"]["photons_per_H_per_s"]!=SOURCE_RATE:
        raise ValueError("wrong actual REI S0 astrophysical source")
    if sc["background"]["tilt"]!=[0.,0.,0.] or sc["time"]["t_end_s"]!=END:
        raise ValueError("wrong original proper-frame model")
    if sc["atomic_model"]["photo_cross_section"]!="Frozen Verner96 ground-state AtomicProvider::reference":
        raise ValueError("original Verner owner identity changed")
    return {lab:History(lab,lab+".csv.gz",lab+"-electron_density.csv.gz",sc) for lab in ("S0_BI","S0_FLRW")}

def direction_grid(nmu,nphi):
    if nmu<2 or nphi<4 or nphi%2:raise ValueError("angular quadrature domain")
    for i in range(nmu):
        mu=-1+2*(i+.5)/nmu
        r=math.sqrt(max(0,1-mu*mu))
        for j in range(nphi):
            phi=2*math.pi*(j+.5)/nphi
            yield i,j,(r*math.cos(phi),r*math.sin(phi),mu),mu,phi

def gauss_birth_direction_grid(nmu,nphi):
    """Unit-normalized 2-design or better for isotropic S0 photon birth.
    Gauss-Legendre integrates the unpolarized FLRW rank-two source exactly.
    Output sky still uses original equal-area midpoint pixel locations.
    """
    if nmu<2 or nphi<4 or nphi%2:
        raise ValueError("invalid physical birth angular integration")
    roots=[]
    for i in range(1,nmu+1):
        z=math.cos(math.pi*(i-.25)/(nmu+.5))
        for _ in range(30):
            p0,p1=1.,z
            for k in range(2,nmu+1):
                p0,p1=p1,((2*k-1)*z*p1-(k-1)*p0)/k
            dp=nmu*(z*p1-p0)/(z*z-1)
            step=p1/dp
            z-=step
            if abs(step)<2e-15:break
        roots.append((z,2/((1-z*z)*dp*dp)))
    for i,(mu,wmu) in enumerate(sorted(roots)):
        r=math.sqrt(max(0.,1-mu*mu))
        for j in range(nphi):
            phi=2*math.pi*(j+.5)/nphi
            yield i,j,(r*math.cos(phi),r*math.sin(phi),mu),mu,phi,wmu/(2*nphi)

def redshift(H,n,age):
    v=tuple(n[k]*math.exp(-H[k]*age) for k in range(3))
    g=math.sqrt(sum(z*z for z in v))
    return g,tuple(z/g for z in v)

def threshold_age(H,n):
    lo,hi=0.,END
    for _ in range(50):
        mid=(lo+hi)/2
        if BIRTH_EV*redshift(H,n,mid)[0]>THRESHOLD:lo=mid
        else:hi=mid
    return (lo+hi)/2

def tau_hi(history,birth,observer,n,max_age,simpson_n=16):
    """Piecewise-linear original F08 n_HI(t), exact frequency along null ray."""
    if not (0<=birth<=observer<=END) or simpson_n<=0 or simpson_n%2:
        raise ValueError("invalid exact physical time/integration")
    window=min(observer-birth,max_age)
    if window<=0:return 0.
    h=window/simpson_n
    H=history.H
    v=0.
    for k in range(simpson_n+1):
        elapsed=k*h
        time=birth+elapsed
        E=BIRTH_EV*redshift(H,n,elapsed)[0]
        # At the exact HI cutoff take the left (ionizing) limit. The
        # discontinuous value at one integration endpoint has zero measure;
        # floating-point angular rounding must not decide it.
        if k==simpson_n and observer-birth>=max_age:
            E=THRESHOLD
        s=sigma_hi(E) * history.linear(history.nhi,time)
        v+=(1 if k==0 or k==simpson_n else 4 if k%2 else 2)*s
    return C*v*h/3

def split_threshold_births(source_samples,t,max_age):
    """Integrate constant source separately on either side of E=13.60 eV.
    Each source bin is bisected only if the genuine photon cutoff crosses it.
    """
    cutoff_birth=t-max_age
    npanels=len(source_samples)-1
    for idx,(midpoint,weight,kind) in enumerate(source_samples):
        if idx==0:
            yield idx,(midpoint,weight,kind)
            continue
        lo=(idx-1)*t/npanels
        hi=idx*t/npanels
        if lo<cutoff_birth<hi:
            for a,b in ((lo,cutoff_birth),(cutoff_birth,hi)):
                if b>a:
                    yield idx,((a+b)/2,SOURCE_RATE*(b-a),kind)
        else:
            yield idx,(midpoint,weight,kind)

def model_epoch(history,t,n_birth=128,nmu=16,nphi=32,simpson_n=16,detail=False):
    """Original S0 isotropic initial 0.05+constant injection; HI absorption and
    exact null energy/direction; first Thomson scattering local gain at epoch.
    """
    if t<=0 or t>END or n_birth<8:
        raise ValueError("unsupported source epoch/birth panels")
    if t not in history.times:
        raise ValueError("epoch not an original source accepted clock")
    H=history.H
    nH=history.linear(history.nh,t); ne=history.linear(history.ne,t)
    source_samples=[(0.,INITIAL_COUNT,"initial")]
    source_samples += [((k+.5)*t/n_birth, SOURCE_RATE*t/n_birth,"continuous") for k in range(n_birth)]
    if abs(sum(w for _,w,_ in source_samples)-(INITIAL_COUNT+SOURCE_RATE*t))>1e-14:
        raise ValueError("photon source per H normalization")
    tin=history.tau_electron(t)
    moment=[0.]*9
    ntotal,utotal,gtotal,ngain,ugain=0.,0.,0.,0.,0.
    nbelow=0.
    cohorts=[{"birth_time_s":b,"source_type":kind,"source_number_per_H":w,
              "survived_number_per_H":0.,"survived_energy_eV_per_H":0.,
              "HI_photo_rate_per_s":0.} for b,w,kind in source_samples]
    directions=list(gauss_birth_direction_grid(nmu,nphi))
    if abs(sum(r[5] for r in directions)-1)>1e-12:
        raise ValueError("unpolarized source birth angular weights not normalized")
    edge_by_direction=[threshold_age(H,x[2]) for x in directions]
    for (i,j,n,mu,phi,w_direction),max_age in zip(directions,edge_by_direction):
        for cidx,(birth,n_b,kind) in split_threshold_births(source_samples,t,max_age):
            age=t-birth
            R,nt=redshift(H,n,age)
            Et=BIRTH_EV*R
            photo=tau_hi(history,birth,t,n,max_age,simpson_n)
            if photo<0 or not math.isfinite(photo):
                raise ValueError("negative source absorption optical depth")
            w=n_b*w_direction*math.exp(-photo)
            energy=w*Et
            ntotal+=w;utotal+=energy
            g=C*nH*w*sigma_hi(Et)
            gtotal+=g
            cohorts[cidx]["survived_number_per_H"]+=w
            cohorts[cidx]["survived_energy_eV_per_H"]+=energy
            cohorts[cidx]["HI_photo_rate_per_s"]+=g
            if Et<10: nbelow+=w
            surviving_scatter=math.exp(-(tin-history.tau_electron(birth)))
            gain=energy*surviving_scatter
            ngain+=w*surviving_scatter
            ugain+=gain
            for a in range(3):
                for bidx in range(3):
                    moment[a*3+bidx]+=gain*nt[a]*nt[bidx]
    if abs(sum(moment[k*3+k] for k in range(3))/ugain-1)>2e-12:
        raise ValueError("Thomson source second moment not positive trace matched")
    M=tuple(moment)
    if t==END: idx=15999
    else:idx=round(t/6.25e8)-1
    orig=history.original[idx]
    # Original paired_history.rs::summary_json includes lower-guard in these totals.
    # Do not add the guard twice. Other columns expose its subcomponent only.
    original_n=float(orig["photon_n"])
    original_u=float(orig["photon_u_ev_per_h"])
    original_gamma=float(orig["gamma_HI_per_s"])
    # source model vs original discrete numerical solution, not same operator
    res={
       "model":"EXACT_BIANCHI_NULL_S0_BIRTH_HI_ABS_FIRST_THOMSON_GAIN",
       "branch":history.label,"observer_time_s":t,
       "birth_panels":n_birth,"nmu_in":nmu,"nphi_in":nphi,"simpson_panels":simpson_n,
       "source_photons_per_H":INITIAL_COUNT+SOURCE_RATE*t,
       "model_survivor_n_per_H":ntotal,"model_survivor_u_ev_per_H":utotal,
       "model_gamma_HI_per_s":gtotal,
       "original_survivor_n_per_H":original_n,"original_survivor_u_ev_per_H":original_u,
       "original_gamma_HI_per_s":original_gamma,
       "model_minus_original_n_rel":ntotal/original_n-1,
       "model_minus_original_u_rel":utotal/original_u-1,
       "model_minus_original_gamma_rel":gtotal/original_gamma-1,
       "original_lower_guard_n_per_H":float(orig["lower_guard_n"]),
       "original_lower_guard_u_ev_per_H":float(orig["lower_guard_u"]),
       "original_lower_guard_n_fraction":float(orig["lower_guard_n"])/original_n,
       "exact_null_minimum_E_ev":BIRTH_EV*math.exp(-max(H)*t),
       "model_photons_below_10eV_per_H":nbelow,
       "pre_first_scatter_unscattered_n_per_H":ngain,
       "pre_first_scatter_unscattered_u_ev_per_H":ugain,
       "electron_opacity_0_to_t":tin,
       "source_matrix_3x3":[list(M[k*3:k*3+3]) for k in range(3)],
       "source_owner_scientific_admission":"HOLD"
    }
    if detail:return res,cohorts
    return res

def outgoing_gain(M,source_energy,ne,mu,phi):
    nmu=mu
    R=math.sqrt(max(0,1-nmu*nmu))
    theta=(nmu*math.cos(phi),nmu*math.sin(phi),-R)
    az=(-math.sin(phi),math.cos(phi),0.)
    n=(R*math.cos(phi),R*math.sin(phi),nmu)
    def tens(a,b):
        return sum(a[i]*M[3*i+j]*b[j] for i in range(3) for j in range(3))
    pref=3/(16*math.pi)
    JI=pref*(source_energy+tens(n,n))
    JQ=-pref*(tens(theta,theta)-tens(az,az))
    JU=-2*pref*tens(theta,az)
    rate=C*SIG_T*ne
    if JI<0 or JI+1e-20<math.hypot(JQ,JU):
        raise ValueError("negative/overpolarized original photon Thomson gain")
    return (JI*rate,JQ*rate,JU*rate,math.hypot(JQ,JU)/JI)

def csv_gz(path,rows):
    with path.open("wb") as f:
        with gzip.GzipFile(fileobj=f,filename="",mtime=0,mode="wb",compresslevel=6) as z:
            with io.TextIOWrapper(z,encoding="utf8",newline="") as text:
                writer=csv.DictWriter(text,fieldnames=list(rows[0]))
                writer.writeheader();writer.writerows(rows)
    return digest(path)

def run(out,n_birth=128,nmu_in=16,nphi_in=32,simpson_n=16):
    histories=source_histories()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    epochs=[];cohort_rows=[];sky=[]
    for label in ("S0_BI","S0_FLRW"):
        h=histories[label]
        for idx in EPOCH_INDEX:
            t=h.times[idx]
            e,coh=model_epoch(h,t,n_birth,nmu_in,nphi_in,simpson_n,True)
            epochs.append(e)
            for row in coh:
                cohort_rows.append({"branch":label,"epoch_s":t,**row})
            mat=tuple(x for matrow in e["source_matrix_3x3"] for x in matrow)
            ne=h.ne[idx]
            for i,j,n,mu,phi in direction_grid(16,32):
                I,Q,U,p=outgoing_gain(mat,e["pre_first_scatter_unscattered_u_ev_per_H"],ne,mu,phi)
                sky.append({"branch":label,"epoch_s":t,"mu_index":i,"phi_index":j,
                            "mu":mu,"phi_rad":phi,"out_gain_I_ev_per_H_s_sr":I,
                            "out_gain_Q_ev_per_H_s_sr":Q,
                            "out_gain_U_ev_per_H_s_sr":U,"out_gain_P_over_I":p})
    sky_path=out/"ORIGINAL_S0_HI_ABS_THOMSON_POLARIZED_GAIN_SKY.csv.gz"
    cohorts_path=out/"ORIGINAL_S0_PHOTON_BIRTH_COHORTS.csv.gz"
    sky_sha=csv_gz(sky_path,sky)
    cohorts_sha=csv_gz(cohorts_path,cohort_rows)
    summary={
      "schema":SCHEMA,"science_status":"SOURCE_AUTHENTIC_REI_HISTORY_S0_RECONSTRUCTED_FIRST_SCATTER_CONDITIONAL",
      "source_sha256":SHA,"original_atomic_provider_SHA256":ATOMIC_OWNER,
      "reference_S0_rei_scientific_admission":"HOLD",
      "original_physical_photon_energy_min_ev":BIRTH_EV*math.exp(-1.01e-14*END),
      "original_numerical_lower_guard_energy_cutoff_ev":10.,
      "original_numerical_lower_guard_interpretation":"BELOW_10EV_DISCRETE_GUARD_CONFLICTS_WITH_EXACT_S0_NULL_ENERGY_SUPPORT_CAUSE_NOT_CERTIFIED",
      "strong_no_go_claim":False,"full_photon_angular_source_equivalence":False,
      "observer_role":"INSTANTANEOUS_LOCAL_THOMSON_GAIN_NO_POSTSCATTER_TRANSFER",
      "incoming_exact_null":True,"original_S0_isotropic_initial_and_birth":True,
      "original_source_rate_per_H_per_s":SOURCE_RATE,"original_initial_photons_per_H":INITIAL_COUNT,
      "HI_photo_owner":"Verner1996_HI_outer_ground_state_original_threshold_13.60_eV",
      "photon_model_replay":"independent_continuum_birth_characteristic_and_nHI_from_REI_curves",
      "c_cm_per_s":C,"sigmaThomson_cm2":SIG_T,
      "epochs":epochs,"sky_rows":len(sky),"birth_cohort_rows":len(cohort_rows),
      "sky_filename":sky_path.name,"sky_sha256":sky_sha,
      "cohort_filename":cohorts_path.name,"cohort_sha256":cohorts_sha,
      "original_F08_source_pair":"0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8",
      "REI_central":"28/88_REPORTED","REI_working":"33/88_REPORTED",
      "BASS_upper":"9/15_SCOPED_SOURCE_MAPPED",
      "new_canonical_nodes":0,"new_full_upper_nodes":0,
      "production":"HOLD","merge":False
    }
    (out/"RESULT.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"science_model":SCHEMA,"sky_rows":len(sky),"cohort_rows":len(cohort_rows),
      "sha256":sky_sha,"final_BI":epochs[3],"final_FLRW":epochs[7],"REI":"28/88"},sort_keys=True))
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"results")
    p.add_argument("--birth-panels",type=int,default=128)
    p.add_argument("--in-mu",type=int,default=16)
    p.add_argument("--in-phi",type=int,default=32)
    p.add_argument("--simpson",type=int,default=16)
    a=p.parse_args()
    run(a.out,a.birth_panels,a.in_mu,a.in_phi,a.simpson)
