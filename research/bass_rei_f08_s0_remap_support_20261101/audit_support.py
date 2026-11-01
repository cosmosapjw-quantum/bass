#!/usr/bin/env python3
"""Cold source-level adverse audit; standard library only, no production imports."""
import csv,gzip,hashlib,json,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
INPUT=ROOT/"source_inputs"
EPOCH=1e13
DT=6.25e8

def hsh(p):
    o=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            o.update(b)
    return o.hexdigest()
def dec(bits):
    return struct.unpack(">d",bytes.fromhex(bits))[0]
def table(p):
    with gzip.open(p,"rt",newline="") as f:return list(csv.DictReader(f))

def parse_source_owner(lab):
    header=json.loads((INPUT/(lab+"-header.jsonl")).read_text())
    raw=(INPUT/(lab+"-checkpoint.dat")).read_text().splitlines()
    h=raw[0].split()
    if (h[0],list(map(int,h[1:6])))!=("REI_F08_PAIRED_CHECKPOINT_V1",[4,8,16,16000,0]):
        raise ValueError("wrong original checkpoint / first-owner identity")
    E=list(map(float,header["energy_nodes"]))
    nd=8*16
    n=int(raw[4])
    assert n==nd*len(E)==2176
    photons=[dec(raw[5+i].split()[0]) for i in range(n)]
    assert int(raw[5+n])==nd
    guards=[dec(raw[6+n+i].split()[0]) for i in range(nd)]
    guard_u=[dec(raw[6+n+i].split()[1]) for i in range(nd)]
    assert len(raw)==6+n+nd
    hvec=([1.01e-14,9.9e-15,1e-14] if lab=="S0_BI" else [1e-14]*3)
    floor=13.7*math.exp(-max(hvec)*EPOCH)
    orig_below=sum(photons[k] for k in range(n) if E[k%len(E)]<floor)+sum(guards)
    orig_n=sum(photons)+sum(guards)
    original_energy=sum(photons[k]*E[k%len(E)] for k in range(n))+sum(guard_u)
    return {"header":header,"floor":floor,"original_n":orig_n,"original_below":orig_below,
            "original_below_fraction":orig_below/orig_n,"original_energy":original_energy,
            "original_guard":sum(guards),"original_guard_energy":sum(guard_u),
            "H":hvec,"E":E}

def run():
    srcsha={}
    for record in (INPUT/"LOCKED_CHECKPOINT_SHA256SUMS.txt").read_text().splitlines():
        expected,filename=record.split()
        got=hsh(INPUT/filename)
        if got!=expected:raise ValueError("original V1 checkpoint SHA mismatch: "+filename)
        srcsha[filename]=got
    assert len(srcsha)==4
    res=json.loads((ROOT/"results"/"RESULT.json").read_text())
    for field,name in (("time_sha256","time_file"),("spectrum_sha256","spectrum_file"),("angular_sha256","angular_file")):
        assert hsh(ROOT/"results"/res[name])==res[field]
    times=table(ROOT/"results"/res["time_file"])
    spectrum=table(ROOT/"results"/res["spectrum_file"])
    angular=table(ROOT/"results"/res["angular_file"])
    assert (len(times),len(spectrum),len(angular))==(60,108,768)
    checks=[]
    for lab in ("S0_BI","S0_FLRW"):
        origin=parse_source_owner(lab)
        E=origin["E"]
        qhat=origin["header"]["qhat"]
        assert len(qhat)==128 and len(E)==17
        original_curve=table(ROOT.parent/"bass_rei_f08_s0_source_photon_thomson_20261101"/"source_inputs"/(lab+".csv.gz"))
        owner=float(original_curve[-1]["photon_n"])
        assert abs(origin["original_n"]/owner-1)<1e-12
        j=12
        weights=[]
        for q in qhat:
            red=math.sqrt(sum(q[i]**2*math.exp(-2*origin["H"][i]*DT) for i in range(3)))
            down=(E[j]*(1-red))/(E[j]-E[j-1])
            assert 0<down<1 and E[j-1]<13.7*math.exp(-max(origin["H"])*DT)
            weights.append(down)
        first_mass=sum(weights)/len(weights)*.05
        st=next(x for x in res["stat_records"] if x.get("type")=="ACTUAL_SOURCE_FIRST_STEP_HAT_WITNESS" and x["branch"]==lab)
        # Independent math.sqrt + summation differs from NumPy by 4.28e-16 photons/H.
        assert abs(st["first_step_artificial_mass_before_absorption_per_H"]-first_mass)<1e-15
        assert abs(first_mass)>0.00017
        st=next(x for x in res["stat_records"] if x.get("type")=="ORIGINAL_PHYSICAL_S0_END_CHECKPOINT" and x["branch"]==lab)
        assert math.isclose(st["original_below_exact_physical_support_fraction"],origin["original_below_fraction"],rel_tol=5e-14)
        assert origin["original_below_fraction"]>.23
        assert 0<origin["original_guard"]<origin["original_below"]
        assert origin["original_guard_energy"]/origin["original_guard"]<10
        final=next(x for x in times if x["branch"]==lab and x["mode"]=="FROZEN_HI_IMPLICIT_ABSORPTION" and x["tick"]=="16000")
        n=float(final["n_per_H"]); frac=float(final["under_exact_min_fraction"])
        assert abs(n-owner)<1.05e-5
        assert abs(frac-origin["original_below_fraction"])<3e-5
        assert abs(float(final["guard_n_per_H"])-origin["original_guard"])<1e-7
        passive=next(x for x in times if x["branch"]==lab and x["mode"]=="PASSIVE_REMAP_ONLY" and x["tick"]=="16000")
        assert math.isclose(float(passive["n_per_H"]),0.1,rel_tol=5e-12)
        rows=[x for x in spectrum if x["branch"]==lab and x["mode"]=="ORIGINAL_F08_SOURCE_CHECKPOINT"]
        assert len(rows)==18 and sum(float(z["photon_n_per_H"]) for z in rows)>0.05
        ang=[x for x in angular if x["branch"]==lab and x["mode"]=="ORIGINAL_F08_SOURCE_CHECKPOINT"]
        assert len(ang)==128
        assert math.isclose(sum(float(x["retained_n_per_H"]) for x in ang),owner,rel_tol=2e-13)
        checks.append({
            "branch":lab,
            "original_checkpoint_total_photons_per_H":origin["original_n"],
            "original_checkpoint_under_exact_floor_per_H":origin["original_below"],
            "original_checkpoint_under_exact_floor_fraction":origin["original_below_fraction"],
            "original_checkpoint_guard_per_H":origin["original_guard"],
            "first_step_original_hat_below_null_support_per_H":first_mass,
            "frozen_matter_hat_total_per_H":n,
            "frozen_vs_original_total_relative":n/owner-1,
            "frozen_vs_original_below_floor_fraction_delta":frac-origin["original_below_fraction"]
        })
    report={
        "schema":"BASS_REI_F08_S0_ORIGINAL_HAT_RED_TEAM_V1",
        "evidence_type":"SAME_AUTHOR_INDEPENDENT_STDLIB_ORIGINAL_CHECKPOINT_AND_BIN_READBACK",
        "original_checkpoint_sha256":srcsha,
        "source_owner_code":"UNMODIFIED",
        "status":"PASS_SCOPED",
        "independent_math":"EXACT_FIRST_STEP_FIXED_GRID_POSITIVE_MEAN_PRESERVING_HAT_VIOLATES_PHYSICAL_SOURCE_SUPPORT",
        "full_original_chemistry_solver_replayed":False,
        "6pct_discrepancy_exactly_attributed":False,
        "no_go_scope":"ONE_SPECIFIC_ORIGINAL_TWO_POINT_FIXED_GRID_REMAP_OPERATOR_NOT_UNIVERSAL_MONOTONE_TRANSFER",
        "science_counts":{"timelines":60,"spectra":108,"angular":768},
        "findings":checks,
        "REI_DAG":"28/88_REPORTED_NO_CHANGE",
        "BASS_DAG":"9/15_SCOPED_SOURCE_MAPPED_NO_FULL_PROMOTION"
    }
    (ROOT/"results/INDEPENDENT_AUDIT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("AUDIT_PASS",json.dumps(checks,sort_keys=True))
    return report
if __name__=="__main__":run()
