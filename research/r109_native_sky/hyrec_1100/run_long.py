"""Run and summarize long-epoch homogeneous recombination-only sky controls."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import gzip
import hashlib
import io
import json
import math
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
S=5.0e-4
# External chemistry remains a single q=0 history throughout these tests.
CASES={
    "VIII_192": ("custom_VIII",None,None,192,6,12),
    "VIII_384": ("custom_VIII",None,None,384,6,12),
    "VIII_angular": ("custom_VIII",None,None,384,10,20),
    "FLRW_zero": ("I",0.,0.,192,6,12),
    "I_96": ("I",S,.001,96,6,12),
    "I_192": ("I",S,.001,192,6,12),
    "I_384": ("I",S,.001,384,6,12),
    "I_angular": ("I",S,.001,384,10,20),
    "VII0_96": ("VII0",S,.001,96,6,12),
    "VII0_192": ("VII0",S,.001,192,6,12),
    "VII0_384": ("VII0",S,.001,384,6,12),
    "VII0_angular": ("VII0",S,.001,384,10,20),
}
for steps in (3072,6144,12288):
    CASES[f"I_t{steps}"]=("I",S,.001,steps,6,12)
    CASES[f"VIII_t{steps}"]=("custom_VIII",None,None,steps,6,12)
CASES["FLRW_t12288"]=("I",0.,0.,12288,6,12)
for nmu in (24,48,96):
    CASES[f"VII0_mu{nmu}"]=("VII0",S,.001,1536,nmu,24)
CASES["VII0_t3072mu96"]=("VII0",S,.001,3072,96,24)

CASES["VII0_mu144"]=("VII0",S,.001,1536,144,24)
CASES["VII0_mu144phi48"]=("VII0",S,.001,1536,144,48)
CASES["FLRW_96"]=("I",0.,0.,96,6,12)
CASES["FLRW_384"]=("I",0.,0.,384,6,12)
CLOCK_CASES=["FLRW_96","FLRW_zero","FLRW_384","FLRW_t12288","VIII_192","VIII_384","VIII_t3072","I_384","VII0_mu96"]
for label in CLOCK_CASES:
    CASES[label+"_reduced"]=CASES[label]
for nphi in (48,96,144,192):
    CASES[f"VII0_phi{nphi}"]=("VII0",S,.001,768,96,nphi)
def table(path):
    with path.open() as f: return list(csv.DictReader(f,delimiter="\t"))
def flat_reference(src):
    data=table(HERE/"hyrec_xe.tsv")
    scale=299792458*6.6524587051e-29*src["n_h_emit_m3"]/src["h_emit_s"]
    h=lambda t: math.sqrt(.75*math.exp(-3*t)+.25*math.exp(-4*t))
    nodes=[(-math.sqrt(3/5),5/9),(0.,8/9),(math.sqrt(3/5),5/9)]
    ds=[]
    for x,y in zip(data,data[1:]):
        lo,hi=float(x["eta"]),float(y["eta"])
        xe0,xe1=float(x["xe_per_H"]),float(y["xe_per_H"])
        total=0.
        for v,w in nodes:
            u=(1+v)/2
            t=lo+(hi-lo)*u
            total+=.5*w*math.exp(-3*t)/h(t)*(xe0+(xe1-xe0)*u)
        ds.append((hi-lo)*scale*total)
    return dict(tau=math.fsum(ds),hubble_ratio=h(float(data[-1]["eta"])))
def command(binary,raw,label,src):
    fam,s,b,steps,nmu,nphi=CASES[label]
    ic = ["--lie-ic",HERE/"generic_viii.tsv"] if fam=="custom_VIII" else ["--family",fam,"--shear",s,"--dust-beta",f"{b},0,0"]
    q = ["--expansion-equation","gauss-reduced"] if label.endswith("_reduced") else []
    return list(map(str,[binary,*q,*ic,"--dust-fraction",.75,
        "--duration",src["eta_terminal"],"--steps",steps,"--nmu",nmu,"--nphi",nphi,"--lmax",4,
        "--feedback","recoil","--ionization",HERE/"hyrec_xe.tsv","--n-h-emit-m3",src["n_h_emit_m3"],
        "--h-emit-s",src["h_emit_s"],"--out",raw/label]))
def summarize(raw, labels, src, out, binary=None):
    data={"scope":"recombination-only q=0 x_e replay; observer normal; opposing dust and photons; initial conditional sky",
          "source_table_sha256":src["table_sha256"],"flat_dust_radiation_reference":flat_reference(src),"cases":{},"changes":{},"expansion_equation_comparisons":{}}
    if binary is not None:
        data["bass_executable_sha256"]=hashlib.sha256(binary.read_bytes()).hexdigest()
    labels=[n for n in CASES if n in labels]
    all_modes={}
    for name in labels:
        d=raw/name
        diag=table(d/"diagnostics.tsv")
        cls=table(d/"cl.tsv")
        modes=table(d/"modes.tsv")
        if len(modes)!=25 or len(diag)!=CASES[name][3]+1: raise ValueError(f"incomplete history {name}")
        for t in (diag,cls,modes):
            if any(not math.isfinite(float(v)) for row in t for v in row.values()): raise ValueError(f"nonfinite {name}")
        j=diag[-1]
        if abs(float(j["eta"])-src["eta_terminal"])>1e-12: raise ValueError("terminal eta")
        obs={k:float(j[k]) for k in ("eta","proper_depth","hubble_ratio","omega_radiation","omega_dust","host_beta_x")}
        equation="gauss-reduced" if name.endswith("_reduced") else "raychaudhuri"
        run=(d/"run.txt").read_text()
        if equation=="gauss-reduced" and ("expansion_equation="+equation) not in run:
            raise ValueError(f"unexpected expansion equation in {name}")
        obs.update(expansion_equation=equation,initial_host_beta=[float(diag[0]["host_beta_"+a]) for a in "xyz"],case=CASES[name],max_abs_gauss=max(abs(float(x["gauss"])) for x in diag),
                   max_abs_codazzi=max(abs(float(x[k])) for x in diag for k in ("codazzi_x","codazzi_y","codazzi_z")),
                   max_abs_collision_energy_defect=max(abs(float(x["collision_energy_defect"])) for x in diag),
                   max_abs_solid_angle_defect=max(abs(float(x["solid_angle"])-4*math.pi) for x in diag),
                   modes_sha256=hashlib.sha256((d/"modes.tsv").read_bytes()).hexdigest(),
                   cl=[{k:float(v) for k,v in row.items()} for row in cls])
        data["cases"][name]=obs
        all_modes[name]=modes
    for family in ("I","VII0","VIII"):
        comparisons=[("96","192"),("192","384"),("384","angular")]
        if family in ("I","VIII"):
            comparisons += [("384","t3072"),("t3072","t6144"),("t6144","t12288")]
        else:
            comparisons += [("mu24","mu48"),("mu48","mu96"),("mu96","t3072mu96"),("mu96","mu144"),("mu144","mu144phi48"),("phi48","phi96"),("phi96","phi144"),("phi144","phi192")]
        for lo,hi in comparisons:
            a,b=family+"_"+lo,family+"_"+hi
            if a not in all_modes or b not in all_modes:continue
            comp={}
            for c in "TEB":
                u=[complex(float(m[c+"_re"]),float(m[c+"_im"])) for m in all_modes[a] if int(m["ell"])>=2]
                v=[complex(float(m[c+"_re"]),float(m[c+"_im"])) for m in all_modes[b] if int(m["ell"])>=2]
                delta=math.sqrt(math.fsum(abs(x-y)**2 for x,y in zip(u,v)))
                norm=math.sqrt(math.fsum(abs(x)**2 for x in v))
                comp[c]=dict(delta_L2=delta,finer_L2=norm,relative=delta/norm if norm else None)
            data["changes"][a+"_to_"+b]=comp
    for name in CLOCK_CASES:
        alternate=name+"_reduced"
        if alternate not in all_modes or name not in all_modes:continue
        old=data["cases"][name]
        new=data["cases"][alternate]
        comparison={n:new[n]-old[n] for n in ("proper_depth","hubble_ratio","max_abs_gauss","max_abs_codazzi")}
        for c in "TEB":
            amplitudes=[[(float(m[c+"_re"]),float(m[c+"_im"])) for m in all_modes[key] if int(m["ell"])>=2] for key in (name,alternate)]
            delta=math.sqrt(math.fsum((x-u)**2+(y-v)**2 for (x,y),(u,v) in zip(*amplitudes)))
            norm=math.sqrt(math.fsum(x*x+y*y for x,y in amplitudes[1]))
            comparison[c]=dict(delta_L2=delta,reduced_L2=norm,relative=delta/norm if norm else None)
        data["expansion_equation_comparisons"][name]=comparison
    out.mkdir(exist_ok=True,parents=True)
    (out/"long_epoch.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")
    # Preserve signed harmonic coefficients and all six per-mode products for completed runs.
    buf=io.StringIO()
    for i,name in enumerate(labels):
        lines=(raw/name/"modes.tsv").read_text().splitlines()
        if i==0: buf.write("case\t"+lines[0]+"\n")
        for line in lines[1:]: buf.write(name+"\t"+line+"\n")
    (out/"long_modes.tsv.gz").write_bytes(gzip.compress(buf.getvalue().encode(),mtime=0))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--case",choices=CASES,action="append")
    p.add_argument("--jobs",type=int,default=1)
    p.add_argument("--summarize-only",action="store_true")
    p.add_argument("--output",type=Path,default=HERE)
    a=p.parse_args()
    src=json.loads((HERE/"source.json").read_text())
    names=a.case or list(CASES)
    if not a.summarize_only:
        a.raw.mkdir(parents=True,exist_ok=True)
        # Prioritize the more expensive angular refinements when parallel runs are selected.
        order=sorted(names,key=lambda n: CASES[n][3]*CASES[n][4]*CASES[n][5],reverse=True)
        with ThreadPoolExecutor(max_workers=a.jobs) as pool:
            list(pool.map(lambda n: subprocess.run(command(a.binary,a.raw,n,src),check=True),order))
    summarize(a.raw,names,src,a.output,a.binary)
if __name__=="__main__":
    main()
