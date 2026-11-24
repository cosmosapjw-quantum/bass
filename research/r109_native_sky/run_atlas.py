#!/usr/bin/env python3
"""Reproduce the homogeneous sky reference atlas in a new directory from a pinned CLI."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import subprocess
import tarfile

import numpy as np


FAMILIES = ["I", "II", "III", "IV", "V", "VI0", "VIh", "VIstar", "VII0", "VIIh", "VIII", "IX"]
CHANNELS = ["TT", "TE", "TB", "EE", "EB", "BB"]
BETA = [.1, .035, -.025]
HERE = Path(__file__).resolve().parent


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def cases(recoil):
    for route in ["active", "tracer"] + (["recoil"] if recoil else []):
        for family in FAMILIES:
            yield f"{route}_{family}", route, family, 18, 10, 24, .35, .18
        for family in ["VIIh", "VIstar"]:
            for tag, steps, nmu, nphi in [("t2",36,10,24), ("t4",72,10,24), ("a2",18,16,40), ("a3",18,22,56)]:
                yield f"{route}_{family}_{tag}", route, family, steps, nmu, nphi, .35, .18
    for tag in ["norm", "observer"]:
        yield f"FLRW_{tag}", tag, "FLRW",18,12,32,.35,0.
    if recoil:
        for family in ["VIIh", "VIstar"]:
            yield f"recoil_{family}_no_scattering", "active_observer", family,18,10,24,.35,.18
            yield f"recoil_{family}_half_scattering", "recoil_half", family,18,10,24,.35,.18
        for tag, steps, nmu, nphi in [("long",48,14,36), ("long_t2",96,14,36), ("long_a2",48,20,52)]:
            yield f"recoil_VIstar_{tag}", "recoil", "VIstar", steps, nmu, nphi, .80,.18


def command(case, binary, dest):
    tag,route,family,steps,nmu,nphi,duration,shear=case
    args=[str(binary),"--family",family,"--shear",str(shear),"--duration",str(duration),
          "--steps",str(steps),"--nmu",str(nmu),"--nphi",str(nphi),"--lmax","4"]
    if route != "tracer":
        args.extend(["--expansion-equation","raychaudhuri"])
    if route in ("norm","observer"):
        args.extend(["--feedback","active","--tau","0"])
    elif route == "tracer":
        args.extend(["--feedback","tracer","--tau",".22","--electron-beta",".14,-.03,.02"])
    else:
        feedback = {"active_observer":"active","recoil_half":"recoil"}.get(route,route)
        depth = {"recoil":".22","recoil_half":".11"}.get(route,"0")
        args.extend(["--feedback",feedback,"--dust-fraction",".22","--dust-beta",".16,-.08,.04",
                     "--tau",depth])
    if route in ("tracer","recoil","recoil_half","active_observer","observer"):
        args.extend(["--observer-beta",",".join(map(str,BETA))])
    return [*args,"--out",str(dest/tag)]


def read_tsv(path):
    with path.open() as stream:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream, delimiter="\t")]


def products_and_checks(folder):
    modes=read_tsv(folder/"modes.tsv")
    cls=read_tsv(folder/"cl.tsv")
    keys=[(int(r["ell"]),int(r["m"])) for r in modes]
    if keys != [(ell,m) for ell in range(5) for m in range(-ell,ell+1)]:
        raise ValueError(f"missing or reordered signed modes in {folder}")
    def cm(row,key):
        return complex(row[key+"_re"],row[key+"_im"])
    harm=np.array([[cm(row,c) for c in "TEB"] for row in modes])
    products=np.array([[cm(row,c) for c in CHANNELS] for row in modes])
    recompute=np.array([[harm[i,"TEB".index(c[0])]*harm[i,"TEB".index(c[1])].conjugate()
                         for c in CHANNELS] for i in range(len(modes))])
    parity=max(np.max(np.abs(harm[keys.index((l,-m))]-(-1.)**m*harm[i].conj())) for i,(l,m) in enumerate(keys))
    cls_value=np.array([[r[c] for c in CHANNELS] for r in cls])
    cl_replay=np.array([products[[i for i,(l,m) in enumerate(keys) if l==ell]].mean(axis=0) for ell in range(5)])
    matrices=np.empty((len(modes),3,3),complex)
    for j,c in enumerate(CHANNELS):
        a,b="TEB".index(c[0]),"TEB".index(c[1])
        matrices[:,a,b]=products[:,j]
        matrices[:,b,a]=products[:,j].conjugate()
    evals=np.linalg.eigvalsh(matrices)
    if not np.isfinite(harm).all() or not np.isfinite(products).all() or not np.isfinite(cls_value).all():
        raise ValueError("non-finite harmonic output")
    checks={"signed_alm_reality_max_abs":float(parity),
            "outer_product_max_abs":float(np.max(abs(products-recompute))),
            "cl_replay_max_abs":float(np.max(abs(cl_replay-cls_value))),
            "product_min_eigenvalue":float(np.min(evals)),
            "product_second_eigenvalue_max_abs":float(np.max(abs(evals[:,1]))),
            "max_imaginary_cross_product":float(np.max(abs(products.imag)))}
    scale=max(1.,np.max(abs(harm)),np.max(abs(products)))
    if max(checks["signed_alm_reality_max_abs"],checks["outer_product_max_abs"],checks["cl_replay_max_abs"],
           -checks["product_min_eigenvalue"],checks["product_second_eigenvalue_max_abs"])>1e-12*scale:
        raise ValueError(f"harmonic identities did not close: {folder}, {checks}")
    return keys,harm,checks,cls_value


def diagnostics(folder):
    d=read_tsv(folder/"diagnostics.tsv")
    a={k: np.array([r[k] for r in d]) for k in d[0]}
    if not all(np.isfinite(x).all() for x in a.values()):
        raise ValueError(f"non-finite diagnostics for {folder}")
    peak=lambda v:float(np.max(np.abs(v)))
    norm=lambda names:np.sqrt(sum(a[k]**2 for k in names))
    summary={"n_time_rows":len(d),"gauss_initial":float(a["gauss"][0]),"gauss_max_abs":peak(a["gauss"]),
        "codazzi_initial_norm":float(norm(["codazzi_x","codazzi_y","codazzi_z"])[0]),
        "codazzi_max_norm":peak(norm(["codazzi_x","codazzi_y","codazzi_z"])),
        "jacobi_max_norm":peak(a["jacobi_norm"]), "solid_angle_max_abs_from_4pi":peak(a["solid_angle"]-4.*np.pi),
        "min_screen_eigenvalue":float(min(a["min_screen_eigenvalue"])), "max_screen_leak":peak(a["max_screen_leak"]),
        "endpoint":d[-1]}
    if "host_beta_x" in a:
        beta=np.column_stack([a["host_beta_"+i] for i in "xyz"])
        norms=np.linalg.norm(beta,axis=1)
        if np.any(norms>=1):
            raise ValueError("non-timelike massive stream in CLI diagnostics")
        spatial=beta/np.sqrt(1.0-norms**2)[:,None]
        summary["host_max_speed_over_c"]=float(max(norms))
        summary["host_momentum_per_rest_mass_c_initial_final"]=[spatial[0].tolist(),spatial[-1].tolist()]
    # New CLI releases may expose source-level per-step defects and momenta.
    for name in a:
        if any(s in name for s in ("defect","recoil","transfer","impulse","collision_energy","conservation")):
            summary.setdefault("exchange_columns",{})[name]={"max_abs":peak(a[name]),"final":float(a[name][-1])}
    return summary


def archive_products(dest, archive):
    # Byte-identical raw files, with deterministic tar/gzip headers and relative names.
    with archive.open("xb") as out, gzip.GzipFile(fileobj=out,mode="wb",filename="",mtime=0) as zipped, tarfile.open(fileobj=zipped,mode="w|") as tar:
        for tag in sorted(dest):
            for name in ("modes.tsv","cl.tsv","diagnostics.tsv","run.txt"):
                data=(dest[tag]/name).read_bytes()
                member=tarfile.TarInfo(f"{tag}/{name}")
                member.size=len(data)
                tar.addfile(member,io.BytesIO(data))


def summary(results, alms):
    changes={}
    def compare(lhs,rhs):
        diff=alms[lhs]-alms[rhs]
        denom=np.linalg.norm(alms[rhs],axis=0)
        err=np.linalg.norm(diff,axis=0)
        # Absolute cancellation in ungenerated channels should not be reported as a large relative error.
        return {"max_abs_alm_by_TEB":np.max(abs(diff),axis=0).tolist(),"l2_by_TEB":err.tolist(),
                "relative_l2_by_TEB":[float(x/y) if y>1e-12 else None for x,y in zip(err,denom)],
                "gauss_peak":[results[k]["diagnostics"]["gauss_max_abs"] for k in [lhs,rhs]],
                "codazzi_peak":[results[k]["diagnostics"]["codazzi_max_norm"] for k in [lhs,rhs]]}
    for tag in alms:
        if tag.endswith("_t2") and tag.removesuffix("_t2") in alms:
            base=tag.removesuffix("_t2")
            for a,b in [("", "_t2"),("_t2","_t4"),("","_a2"),("_a2","_a3")]:
                if base+a in alms and base+b in alms:
                    changes[base+a+"__"+base+b]=compare(base+a,base+b)
    matched={}
    for fam in ["VIIh","VIstar"]:
        base=f"recoil_{fam}"
        if base in alms:
            for suffix in ("no_scattering","half_scattering"):
                variant=base+"_"+suffix
                matched[base+"__"+variant]=compare(base,variant)
    control=alms["FLRW_norm"]
    obs=alms["FLRW_observer"]
    # Index order for ell=1: m=-1,0,+1; Condon-Shortley harmonics.
    direction=np.array([-np.sqrt(3/(2*np.pi))*obs[3,0].real,np.sqrt(3/(2*np.pi))*obs[3,0].imag,
                        np.sqrt(3/(4*np.pi))*obs[2,0].real])
    beta=np.linalg.norm(BETA)
    exact=(3./beta*(1.-beta/math.atanh(beta)))*np.array(BETA)/beta
    physical_controls={"flrw_rest_max_abs_alm":float(np.max(abs(control))),
        "flrw_boost_temperature_dipole":direction.tolist(),"analytic_dipole":exact.tolist(),
        "boost_max_component_error":float(max(abs(direction-exact))),
        "flrw_boost_max_abs_EB":float(np.max(abs(obs[:,1:]))),
        "analytic_law":"T_sky proportional to 1/[gamma (1-beta dot n_sky)], normalized by its full-sky mean"}
    if physical_controls["flrw_rest_max_abs_alm"]>1e-11 or physical_controls["boost_max_component_error"]>1e-9 or physical_controls["flrw_boost_max_abs_EB"]>1e-10:
        raise ValueError(f"FLRW control failure: {physical_controls}")
    return {"refinements":changes,"matched_optical_depth":matched,"controls":physical_controls}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True,help="New directory for native outputs, snapshots and receipt")
    p.add_argument("--with-recoil",action="store_true")
    opt=p.parse_args()
    dest=opt.raw.resolve()
    dest.mkdir(parents=True,exist_ok=False)
    exe=dest/"homogeneous_sky"
    shutil.copy2(opt.binary.resolve(strict=True),exe)
    results,alms,folders={},{},{}
    for case in cases(opt.with_recoil):
        tag=case[0]
        argv=command(case,exe,dest)
        completed=subprocess.run(argv,check=False,capture_output=True)
        if completed.returncode:
            raise RuntimeError(f"{tag} exit {completed.returncode}: {completed.stderr.decode()}")
        folder=dest/tag
        _,harm,check,cls=products_and_checks(folder)
        results[tag]={"argv":argv,"argv_sha256":hashlib.sha256(json.dumps(argv,separators=(",",":")).encode()).hexdigest(),
                      "files_sha256":{p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()},
                      "harmonic_checks":check,"diagnostics":diagnostics(folder),"cl_ell_0_to_4":cls.tolist()}
        alms[tag]=harm
        folders[tag]=folder
    repo=HERE.parents[1]
    relevant=[repo/"_rustcore"/name for name in ["Cargo.toml","Cargo.lock","examples/homogeneous_sky.rs",
              "src/kinetic/radiation_feedback.rs","src/kinetic/sky_spectrum.rs","src/kinetic/lie_history.rs","src/kinetic/tilted_dust.rs"]]
    relevant += sorted((repo/"_rustcore/src/homogeneous_sky").glob("*.rs"))
    inventory={str(f.relative_to(repo)):digest(f) for f in relevant if f.is_file()}
    report={"source_file_hashes_at_execution":inventory,"active_expansion_equation":"raychaudhuri","codazzi_residual_convention":"div(Sigma) + kappa*q/H^2 in normalized tetrad units","schema":"bass.r109.native_all_family_atlas/1","binary_sha256":digest(exe),"script_sha256":digest(Path(__file__)),
            "primary_route":"recoil" if opt.with_recoil else "active (collisionless)",
            "cl_columns":CHANNELS,"scope":"finite homogeneous deterministic T/E/B sky; C_lm is the oriented complex outer product. Fixed initial data and orientation; no primordial covariance or data likelihood.",
            "cases":results,**summary(results,alms)}
    archive=dest/"ATLAS_MODES.tar.gz"
    archive_products(folders,archive)
    report["archive_sha256"]=digest(archive)
    (dest/"ATLAS.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(f"{len(results)} native runs; controls={report['controls']}; archive={report['archive_sha256']}")


if __name__=="__main__":
    main()
