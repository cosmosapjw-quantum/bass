"""Strict source-bound, kinematically consistent BASS PR164 geometry table consumer.

This is an isolated Python reference for future Rust rei_microphysics implementation.
The owner driver and old checkpoints are neither read nor modified.

Signature (-,+,+,+), non-tilted LRS Bianchi I, SI proper time:
 a_perp=a exp(-b), a_parallel=a exp(2b), b'=s/H,
 Sigma=sqrt(3)|s|/H; native BackgroundPoint.sigma is signed s/H.

Use cubic Hermite of b(x) with endpoint derivative s/H, and log H(x)
with derivative (dH/dx)/H. Defining s=H b' enforces the geometric
identity at every interpolated point, not just at the CSV knots. Reconstruct
proper time from positive quadrature dt/dx=1/H, rather than resuming any
original AX08 chemistry checkpoint. This does NOT prove the intermediate
Einstein shear equation or transport/chemistry source closure.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
import csv
import hashlib
import json
import math
import numpy as np
from numpy.polynomial.legendre import leggauss

H0=2.1842852410855026e-18
OM=.315
OR=.000092
OL=.6849080000000001
OB=.049309230511847414
AREF=1.0/21.0
AEND=.2
XRANGE=math.log(AEND/AREF)
SCHEMA="bass.rei.proposed_background_point_tangent.v1"
ORIGINAL_BASS_COMMIT="3c39bbbf46b6663e7c40277e194fd0ef48118472"
EXPECTED_CASE_NAMES=("COLD_FLRW","WARM_ISOTROPIC","MASSIVE_A_PLUS",
                     "MASSIVE_A_MINUS","MASS3_A_PLUS","MASS300_A_PLUS",
                     "SIGNED_PLUS","SIGNED_MINUS")
HEADER=("case","x","a","zbar","proper_elapsed_s","b","H_mean_per_s",
        "s_per_s","Sigma","signed_s_over_H","H_cold_FLRW_reference_per_s",
        "massive_rho_norm","massive_pbar_norm","massive_deltaP_norm",
        "massive_partial_b_deltaP_norm","massive_deltaP_A_norm",
        "dH_db_per_s","db_dA","d(s_per_s)_dA",
        "dH_dln_a_per_s","H_perp_per_s","H_parallel_per_s")
LEG=leggauss(8)
L_NODES=(LEG[0]+1)/2
L_WEIGHTS=LEG[1]/2

class SourceTableError(ValueError):
    """An input/source/restart-contract failure, never a silent repair."""


def check(ok, message):
    if not ok: raise SourceTableError(message)


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()


def close(actual, expected, rtol=2e-12, atol=1e-26):
    return math.isfinite(actual) and math.isfinite(expected) and abs(actual-expected)<=atol+rtol*abs(expected)


@dataclass(frozen=True)
class Node:
    x:float
    a:float
    time_s:float
    b:float
    h:float
    s:float
    hprime:float
    delta_norm:float
    rho_norm:float
    pbar_norm:float
    sigma:float

@dataclass(frozen=True)
class GeometryPoint:
    x:float
    a:float
    b:float
    time_s:float
    h_per_s:float
    s_per_s:float
    sigma_signed:float
    Sigma:float
    a_perp:float
    a_parallel:float
    H_perp_per_s:float
    H_parallel_per_s:float

    def as_native_background_point(self):
        """Fields of rei_microphysics::axbi_background::BackgroundPoint.

        h_flrw_per_s is a *reference*, not the actual kinetic H. No
        original chemistry driver is switched by constructing this dict.
        """
        hc=H0*math.sqrt(OM/self.a**3+OR/self.a**4+OL)
        return {"a":self.a,"b":self.b,"time_s":self.time_s,
                "h_flrw_per_s":hc,"h_per_s":self.h_per_s,
                "s_per_s":self.s_per_s,"sigma":self.sigma_signed}


class HermiteInterval:
    __slots__=("left","right","span","logh0","logh1","dh0","dh1","b0","b1","bprime0","bprime1")
    def __init__(self,left:Node,right:Node):
        self.left=left
        self.right=right
        self.span=right.x-left.x
        check(self.span>0,"nonmonotonic x nodes")
        self.logh0=math.log(left.h)
        self.logh1=math.log(right.h)
        self.dh0=left.hprime/left.h
        self.dh1=right.hprime/right.h
        self.b0=left.b
        self.b1=right.b
        self.bprime0=left.s/left.h
        self.bprime1=right.s/right.h

    def _basis(self,x):
        u=(x-self.left.x)/self.span
        return u,u*u,u*u*u

    def _hermite(self,y0,y1,dy0,dy1,x):
        u,u2,u3=self._basis(x)
        h=self.span
        value=(2*u3-3*u2+1)*y0+(u3-2*u2+u)*h*dy0+(-2*u3+3*u2)*y1+(u3-u2)*h*dy1
        derivative=((6*u2-6*u)*y0+(3*u2-4*u+1)*h*dy0+(-6*u2+6*u)*y1+(3*u2-2*u)*h*dy1)/h
        return value,derivative

    def state(self,x):
        lh,lhprime=self._hermite(self.logh0,self.logh1,self.dh0,self.dh1,x)
        b,dbdx=self._hermite(self.b0,self.b1,self.bprime0,self.bprime1,x)
        h=math.exp(lh)
        s=h*dbdx
        return b,h,s,lhprime

    def dt_integral(self,x):
        """Positive 8-point Gauss integration of dt/dx=1/H in segment."""
        if x==self.left.x: return 0.0
        hspan=x-self.left.x
        vals=[1.0/self.state(self.left.x+float(t)*hspan)[1]
              for t in L_NODES]
        return float(hspan*np.dot(L_WEIGHTS,vals))


class BackgroundTable:
    def __init__(self,manifest_path:Path,csv_path:Path):
        manifest_path=Path(manifest_path)
        csv_path=Path(csv_path)
        info=json.loads(manifest_path.read_text())
        check(info.get("schema")==SCHEMA,"unknown schema")
        check(info.get("rows",0)>0,"empty source")
        check(info.get("csv_sha256")==sha256(csv_path),"CSV_SHA256_MISMATCH")
        check(info.get("state_columns")==list(HEADER),"HEADER_CONTRACT_MISMATCH")
        check(info.get("cases")==len(EXPECTED_CASE_NAMES),"CASE_COUNT_MISMATCH")
        check(info.get("consumer_contract",{}).get("adoption")=="NOT_ADOPTED_OWNER_REI_REQUIRES_NEW_SOURCE_CHECKPOINT","SOURCE_ADOPTION_CHANGED")
        check(info.get("consumer_contract",{}).get("native_geometry_requires")=="a,b,time_s,H_per_s,s_per_s,sigma_signed=s/H","SIGNED_SHEAR_CONTRACT_CHANGED")
        rows=[]
        with csv_path.open(newline="") as handle:
            reader=csv.DictReader(handle)
            check(reader.fieldnames==list(HEADER),"CSV_HEADER_MISMATCH")
            for row in reader:
                check(None not in row and all(k in row for k in HEADER),"CSV_COLUMNS_CHANGED")
                try: parsed={k:(v if k=="case" else float(v)) for k,v in row.items()}
                except (ValueError,TypeError) as e: raise SourceTableError("CSV_PARSE_NONFINITE") from e
                check(all(math.isfinite(v) for k,v in parsed.items() if k!="case"),"CSV_NONFINITE")
                rows.append(parsed)
        check(len(rows)==info["rows"],"ROW_COUNT_MISMATCH")
        n=int(info["points_per_case"])
        check(11<=n<=2001 and len(rows)==n*len(EXPECTED_CASE_NAMES),"POINT_COUNT_MISMATCH")
        check([x["case"] for x in info["cases_receipt"]]==list(EXPECTED_CASE_NAMES),"CASE_SEQUENCE_RECEIPT")
        self.info=info
        self.source_sha256=info["csv_sha256"]
        self.manifest_sha256=sha256(manifest_path)
        self.samples={}
        self.producer_clock_max_rel=0.0
        self.producer_raychaudhuri_max_rel=0.0
        for i,case in enumerate(EXPECTED_CASE_NAMES):
            part=rows[i*n:(i+1)*n]
            check(all(v["case"]==case for v in part),"CASE_ORDER_OR_NAME")
            params=info["cases_receipt"][i]["params"]
            fm=float(params["fraction"])
            check(0<=fm<=(OM-OB)/OM,"NONBARYONIC_FRACTION")
            check(float(params["mass"])>=3 and -1<=float(params["A"])<=2,"MASSIVE_SOURCE_PARAMETERS")
            if case=="COLD_FLRW":check(fm==0,"COLD_FLRW_FRACTION")
            cm=OM*fm/AREF**3
            nodes=[]
            for j,row in enumerate(part):
                a=row["a"];h=row["H_mean_per_s"];s=row["s_per_s"]
                sigma=row["Sigma"]
                check(j==0 or (row["x"]>part[j-1]["x"] and row["proper_elapsed_s"]>part[j-1]["proper_elapsed_s"]),"NONMONOTONE_CLOCK")
                check(h>0 and a>0 and abs(row["b"])<=1,"NONPHYSICAL_GEOMETRY")
                check(close(a,AREF*math.exp(row["x"])),"SCALE_AND_X_MISMATCH")
                check(close(row["zbar"],1/a-1,atol=2e-11),"REDSHIFT_MISMATCH")
                check(close(sigma,math.sqrt(3)*abs(s)/h,atol=3e-13),"SIGMA_MAGNITUDE_MISMATCH")
                check(close(row["signed_s_over_H"],s/h,atol=2e-13),"SIGN_OF_SHEAR_MISMATCH")
                check(close(row["H_perp_per_s"],h-s) and close(row["H_parallel_per_s"],h+2*s),"DIRECTIONAL_H_MISMATCH")
                check(close(row["H_cold_FLRW_reference_per_s"],H0*math.sqrt(OM/a**3+OR/a**4+OL)),"COLD_REFERENCE_MISMATCH")
                rho=row["massive_rho_norm"];pbar=row["massive_pbar_norm"];delta=row["massive_deltaP_norm"]
                check(rho>=0 and pbar>=0 and pbar<=rho/3+1e-19 and pbar-delta/3>=-1e-16 and pbar+2*delta/3>=-1e-16,"KINETIC_PRESSURE_CONE")
                predicted_h2=H0*H0*(OM*(1-fm)/a**3+OR/a**4+OL+rho)+s*s
                check(close(h*h,predicted_h2,rtol=3e-12,atol=1e-34),"EINSTEIN_HAMILTONIAN")
                check(close(row["dH_db_per_s"],-H0*H0*delta/h,atol=1e-31),"H_B_DERIVATIVE")
                predicted_hp=(H0*H0*(-3*OM*(1-fm)/a**3-4*OR/a**4-3*(rho+pbar))-6*s*s)/(2*h)
                self.producer_raychaudhuri_max_rel=max(self.producer_raychaudhuri_max_rel,abs(predicted_hp-row["dH_dln_a_per_s"])/max(abs(predicted_hp),1e-300))
                check(close(row["dH_dln_a_per_s"],predicted_hp,rtol=3e-12),"RAYCHAUDHURI_ROW")
                nodes.append(Node(row["x"],a,row["proper_elapsed_s"],row["b"],h,s,
                                  row["dH_dln_a_per_s"],delta,rho,pbar,sigma))
            check(close(nodes[0].x,0,atol=1e-14) and close(nodes[-1].x,XRANGE,atol=5e-12),"X_DOMAIN_ENDPOINTS")
            check(nodes[0].time_s==0 and nodes[0].b==0,"INITIAL_CLOCK_AND_GEOMETRY")
            segs=[HermiteInterval(l,r) for l,r in zip(nodes[:-1],nodes[1:])]
            times=[0.0]
            for seg in segs:
                dt=seg.dt_integral(seg.right.x)
                check(dt>0 and math.isfinite(dt),"POSITIVE_PROPER_CLOCK_INTEGRAL")
                times.append(times[-1]+dt)
            for old,new in zip(nodes,times):
                e=abs(old.time_s-new)/max(abs(old.time_s),1.0)
                self.producer_clock_max_rel=max(self.producer_clock_max_rel,e)
            self.samples[case]=(nodes,segs,times)

    def point_at_x(self,case:str,x:float)->GeometryPoint:
        if not math.isfinite(x):raise SourceTableError("NONFINITE_QUERY")
        if case not in self.samples:raise SourceTableError("UNKNOWN_CASE")
        nodes,segs,times=self.samples[case]
        if x<nodes[0].x or x>nodes[-1].x:raise SourceTableError("OUTSIDE_SOURCE_X")
        j=min(bisect_right([k.x for k in nodes],x)-1,len(segs)-1)
        if j<0:j=0
        seg=segs[j]
        b,h,s,_=seg.state(x)
        a=AREF*math.exp(x)
        t=times[j]+seg.dt_integral(x)
        ap=a*math.exp(-b)
        az=a*math.exp(2*b)
        check(all(math.isfinite(v) for v in (b,h,s,a,t,ap,az)) and h>0 and ap>0 and az>0,"NONFINITE_INTERPOLATED_GEOMETRY")
        return GeometryPoint(x,a,b,t,h,s,s/h,math.sqrt(3)*abs(s)/h,
                             ap,az,h-s,h+2*s)

    def point_at_time(self,case:str,t_s:float)->GeometryPoint:
        if case not in self.samples:raise SourceTableError("UNKNOWN_CASE")
        if not math.isfinite(t_s):raise SourceTableError("NONFINITE_QUERY")
        nodes,segs,times=self.samples[case]
        if t_s<0 or t_s>times[-1]:raise SourceTableError("OUTSIDE_SOURCE_TIME")
        if t_s==0.0:return self.point_at_x(case,nodes[0].x)
        if t_s==times[-1]:return self.point_at_x(case,nodes[-1].x)
        j=min(bisect_right(times,t_s)-1,len(segs)-1)
        j=max(j,0)
        lo,hi=nodes[j].x,nodes[j+1].x
        for _ in range(58):
            mid=(lo+hi)/2
            tmid=times[j]+segs[j].dt_integral(mid)
            if tmid<t_s:lo=mid
            else:hi=mid
        return self.point_at_x(case,(lo+hi)/2)

    def export_receipt(self):
        return {"schema":"bass.rei.pr165.checked_proper_time_intake.v1",
                "source_csv_sha256":self.source_sha256,
                "producer_manifest_sha256":self.manifest_sha256,
                "source_parent_commit":ORIGINAL_BASS_COMMIT,
                "case_names":list(EXPECTED_CASE_NAMES),
                "points_per_case":int(self.info["points_per_case"]),
                "source_knot_rows":int(self.info["rows"]),
                "max_producer_vs_integral_clock_relative":self.producer_clock_max_rel,
                "max_independent_row_raychaudhuri_relative":self.producer_raychaudhuri_max_rel,
                "time_definition":"integral_x dx/H interpolated from log H; original tabulated time not blindly adopted",
                "signed_shear":"sigma_native=s/H; public Sigma=sqrt3 abs(s)/H",
                "exclusions":["full native HHe gas solver","stellar source Q^a", "polarized photon transport", "source-adapted checkpoint"],
                "scientific_status":"Python reference source-check, native Rust integration NOT_RUN"}
