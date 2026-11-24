"""R112 bounded smoke, not a physical recombination history or convergence proof."""
import csv
import concurrent.futures
import json
import math
import pathlib
import subprocess
import sys

binary = pathlib.Path(sys.argv[1]).resolve()
root = pathlib.Path(sys.argv[2]).resolve()
root.mkdir(parents=True, exist_ok=False)
families = ["I","II","III","IV","V","VI0","VIh:-0.25","VIstar","VII0","VIIh:0.25","VIII","IX"]
base = ["--feedback","recoil","--dust-fraction","0.8","--baryon-fraction","0.157",
        "--tau","0.01","--duration","0.05","--nmu","10","--nphi","24","--lmax","3",
        "--los-lmax","4","--lie-update","congruence","--collision","sdirk2"]
def read(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter="\t"))
def run(label, extra, steps):
    out = root/label.replace(":","_")
    cmd = [str(binary),"--out",str(out),*base,"--steps",str(steps),*extra]
    p = subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode:
        raise RuntimeError(f"{label}: {p.stderr}")
    rows=read(out/"los_modes.tsv")
    diag=read(out/"diagnostics.tsv")
    assert len(rows)==25
    assert all(math.isfinite(float(v)) for r in rows+diag for v in r.values())
    err=0.; reality=0.; index={(int(r["ell"]),int(r["m"])):r for r in rows}
    def mode(r,x):
        return complex(float(r[x+"_re"]),float(r[x+"_im"]))
    for (l,m),r in index.items():
        for x in "TEB":
            reality=max(reality,abs(mode(index[l,-m],x)-(-1)**m*mode(r,x).conjugate()))
        for xy in ["TT","TE","TB","EE","EB","BB"]:
            err=max(err,abs(mode(r,xy)-mode(r,xy[0])*mode(r,xy[1]).conjugate()))
    assert err<1e-14 and reality<1e-12
    return dict(case=label,steps=steps,n_modes=len(rows),max_product_error=err,
                max_reality_error=reality,max_gauss=max(abs(float(r["gauss"])) for r in diag),
                max_codazzi=max(abs(float(r[f"codazzi_{x}"])) for r in diag for x in "xyz"),
                max_jacobi=max(abs(float(r["jacobi_norm"])) for r in diag),
                max_TT=max(float(r["TT_re"]) for r in rows),
                modes=str(out/"los_modes.tsv"))
def tilt(f):
    return run(f,["--family",f,"--dust-beta","0.1,0,0","--observer-beta","0.03,0.02,-0.01"],16)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    results=list(ex.map(tilt,families))
# Finite tilt is not an exact FLRW solution even with an initially FLRW metric.
results.append(run("FLRW_control",["--family","FLRW","--shear","0","--dust-beta","0,0,0"],16))
assert results[-1]["max_TT"] < 1e-24
lie=root/"classB.lie"
lie.write_text("shear 0.01 -0.005 -0.005 0.002 0.003 0.004\nn 0 0.2 -0.2 0 0 0\na 0.1 0 0\n")
results.append(run("classB_nonzero_codazzi",["--lie-ic",str(lie),"--observer-beta","0.03,0.02,-0.01"],16))
for steps in [32,64]:
    results.append(run(f"VIstar_{steps}",["--family","VIstar","--dust-beta","0.1,0,0","--observer-beta","0.03,0.02,-0.01"],steps))
def vec(p):
    return [float(r[x+"_"+part]) for r in read(pathlib.Path(p)) if int(r["ell"])>=1 for x in "TEB" for part in ("re","im")]
v=[vec(next(r["modes"] for r in results if r["case"]==s)) for s in ("VIstar","VIstar_32","VIstar_64")]
norm=lambda u:math.sqrt(sum(x*x for x in u))
diff=lambda a,b:norm([x-y for x,y in zip(a,b)])
summary={"cases":results,"VIstar_time_refinement":{"d16_32":diff(v[0],v[1]),"d32_64":diff(v[1],v[2]),"ratio":diff(v[0],v[1])/diff(v[1],v[2]),"relative_last":diff(v[1],v[2])/norm(v[2])}}
(root/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
for r in results: print(r["case"],r["n_modes"],r["max_gauss"],r["max_codazzi"],r["max_jacobi"])
print(summary["VIstar_time_refinement"])
