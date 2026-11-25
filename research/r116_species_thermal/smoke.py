#!/usr/bin/env python3
"""Finite-band species-thermal bridge smoke; not a cosmological fit."""
import argparse, concurrent.futures, csv, gzip, hashlib, json, math, os, pathlib, subprocess, time
P=pathlib.Path
p=argparse.ArgumentParser()
p.add_argument("--binary",required=True,type=P)
p.add_argument("--rec",required=True,type=P,help="REC research/r116_species_thermal")
p.add_argument("--out",required=True,type=P)
p.add_argument("--legacy",type=P,help="optional prior continuum smoke output")
a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False)
binary=a.binary.resolve()
env=dict(os.environ,RAYON_NUM_THREADS="1",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1")
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
refs={}
for name,z in [("helium_overlap",1700),("helium",2800),("h_window",1400),("thermal_window",250)]:
    f=a.out/(name+".tsv")
    f.write_bytes(gzip.decompress((a.rec/(name+".tsv.gz")).read_bytes()))
    refs[name]=(f,z,float(f.read_text().splitlines()[-1].split()[0]))
cases=[
 ("he_overlap_flrw","helium_overlap","FLRW",0.,0.,128,"harmonic"),
 ("he_overlap_i","helium_overlap","I",0.001,1e-5,128,"harmonic"),
 ("he_overlap_viih","helium_overlap","VIIh:0.25",0.001,1e-5,128,"harmonic"),
 ("he_flrw","helium","FLRW",0.,0.,256,"harmonic"),
 ("h_flrw","h_window","FLRW",0.,0.,128,"harmonic"),
 ("h_i","h_window","I",0.001,1e-5,128,"harmonic"),
 ("thermal_flrw","thermal_window","FLRW",0.,0.,128,"harmonic"),
 ("thermal_i","thermal_window","I",0.001,1e-5,128,"harmonic"),
 ("he_overlap_i_rays","helium_overlap","I",0.001,1e-5,128,"rays"),
 ("he_overlap_i_continuum","helium_overlap","I",0.001,1e-5,128,"harmonic-continuum"),
 ("h_i_64","h_window","I",0.001,1e-5,64,"harmonic"),
 ("h_i_256","h_window","I",0.001,1e-5,256,"harmonic"),
]
def run(case):
    name,ref,family,shear,beta,steps,route=case
    f,z,dur=refs[ref]
    matter=.14309694000000003*(1+z)**3
    rg=4.48162687719e-7*2.7255**4*(1+z)**4
    rn=.227107317660239*3.03821934419124*rg
    lam=.31113726660800006
    out=a.out/name
    cmd=[str(binary),"--out",str(out),"--family",family,"--shear",str(shear),"--dust-beta",f"{beta},{.3*beta},0","--duration",str(dur),"--steps",str(steps),"--route",route,"--feedback","recoil","--dust-fraction",str(matter/(matter+rg+rn)),"--baryon-fraction",str(.0224/.14309694000000003),"--omega-lambda",str(lam/(matter+rg+rn+lam)),"--neutrino-fraction",str(rn/(rg+rn)),"--expansion-equation","gauss-reduced","--collision","sdirk2","--lie-update","congruence","--lmax","3","--los-lmax","4","--los-ntheta","8","--los-nphi","16","--recombination","species-thermal","--species-reference",str(f)]
    cmd+=["--harmonic-lmax","4","--harmonic-ntheta","10","--harmonic-nphi","24"] if route.startswith("harmonic") else ["--nmu","10","--nphi","24"]
    if route=="harmonic-continuum":cmd+=["--harmonic-work-lmax","12"]
    t=time.monotonic()
    try:
        r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=150)
        row=dict(case=name,reference=ref,reference_sha256=sha(f),command=cmd,returncode=r.returncode,wall_s=time.monotonic()-t,stdout=r.stdout[-2000:],stderr=r.stderr[-3000:])
        if r.returncode==0:
            with (out/"thermochemistry.tsv").open() as h:
                rows=list(csv.DictReader(h,delimiter="\t"))
            row["n_rows"]=len(rows);row["header"]=list(rows[0]); row["last"]=rows[-1];row["sha256"]=sha(out/"thermochemistry.tsv")
            fhe=float(f.read_text().splitlines()[1].split()[1])
            rr=[{k:float(v) for k,v in r.items() if v!=""} for r in rows]
            def peak(k):return max(abs(r[k]) for r in rr if k in r)
            with (out/"diagnostics.tsv").open() as h: dg=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(h,delimiter="\t")]
            m=dict(
                max_charge=max(abs(r["xe"]-r["xp"]-r["x_heii"]-2*r["x_heiii"]) for r in rr),
                max_h_nuclei=max(abs(r["xp"]+r["x_hi"]-1) for r in rr),
                max_he_nuclei=max(abs(r["x_hei"]+r["x_heii"]+r["x_heiii"]-fhe) for r in rr),
                max_w_closure=max(abs(r["w_k"]-(1+fhe+r["xe"])*r["tm_k"]) for r in rr),
                max_continuity=max(abs(math.log(q["n_h_m3"]/r["n_h_m3"])+(q["eta"]-r["eta"])*q["expansion_ratio"]) for r,q in zip(rr,rr[1:])),
                max_thermal_defect_j_per_h=peak("thermal_defect_j_per_h"),
                max_scaled_residual=peak("scaled_residual"),peak_delta_xe=peak("delta_xe"),peak_delta_tm_k=peak("delta_tm_k"),
                min_species=min(r[k] for r in rr for k in ["xp","x_hi","x_heii","x_heiii","x_hei","xe"]),
                min_tm_k=min(r["tm_k"] for r in rr),min_n_h_m3=min(r["n_h_m3"] for r in rr),
                max_gauss=max(abs(r["gauss"]) for r in dg),max_codazzi=max(math.sqrt(sum(r[k]**2 for k in ["codazzi_x","codazzi_y","codazzi_z"])) for r in dg),
                max_jacobi=max(abs(r["jacobi_norm"]) for r in dg),min_screen=min(r["min_screen_eigenvalue"] for r in dg),
                max_collision_energy_defect=max(abs(r["collision_energy_defect"]) for r in dg))
            row["metrics"]=m
            assert len(rr)==steps+1
            assert all(math.isfinite(v) for r in rr+dg for v in r.values())
            assert max(m["max_charge"],m["max_h_nuclei"],m["max_he_nuclei"])<1e-14
            assert m["max_continuity"]<1e-12 and m["max_thermal_defect_j_per_h"]<1e-27
            assert m["min_species"]>=0 and m["min_tm_k"]>0 and m["min_n_h_m3"]>0 and m["min_screen"]>=0
            row["status"]="PASS_SCOPED"
        else:row["status"]="FAIL"
    except Exception as e:row=dict(case=name,command=cmd,status="ERROR",error=str(e))
    print(name,row["status"],row.get("stderr","")[-400:],row.get("error",""),flush=True)
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: results=list(ex.map(run,cases))
legacy={}
if a.legacy:
    old=json.loads((a.legacy/"summary.json").read_text())
    for case in ["grid_I","continuum_I"]:
        c=next(x for x in old["cases"] if x["case"]==case)
        cmd=list(c["command"]);cmd[0]=str(binary);cmd[cmd.index("--out")+1]=str(a.out/("legacy_"+case))
        r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=60)
        legacy[case]={"returncode":r.returncode,"stderr":r.stderr,"byte_equal":{n:(a.out/("legacy_"+case)/n).read_bytes()==(a.legacy/case/n).read_bytes() for n in ["modes.tsv","cl.tsv","los_modes.tsv","los_cl.tsv","diagnostics.tsv","lie_constants.tsv"]} if r.returncode==0 else {}}
by={r["case"]:r for r in results}
def compare(c1,c2):
    p1=by[c1]["last"];p2=by[c2]["last"]
    return {k:abs(float(p1[k])-float(p2[k])) for k in ["xe","tm_k","x_heii","delta_xe","delta_tm_k"]}
comparisons={}
for c1,c2 in [("he_overlap_i","he_overlap_i_rays"),("he_overlap_i","he_overlap_i_continuum"),("h_i_64","h_i"),("h_i","h_i_256")]:
    if by[c1]["status"]==by[c2]["status"]=="PASS_SCOPED":comparisons[c1+"__"+c2]=compare(c1,c2)
(a.out/"RESULTS.json").write_text(json.dumps(dict(schema="bass.r116.species.smoke/1",binary_sha256=sha(binary),scope="conditional source-owned tracer thermal BE, lagged opacity",cases=results,legacy=legacy,comparisons=comparisons),indent=2)+"\n")
