"""Run actual stdlib Rust GL4 interval integrator against independent mp80 AX03.

The Rust source is explicitly supplied real AX03 mathematical formula with only
parameters passed on CLI from frozen family source, not a blind owner-binary
replacement. The original REI checkout remains untouched.
"""
from __future__ import annotations
import csv,hashlib,io,json,subprocess,tempfile
from pathlib import Path
import mpmath as mp

HERE=Path(__file__).resolve().parent
import sys
from shortstep import PARENT as SOURCE
sys.path.insert(0,str(SOURCE))
from axbi_provider import _read_lock

def run(result):
    if result.exists():raise FileExistsError(result)
    mp.mp.dps=90
    original=HERE/"evidence/MP80_SHORTSTEP.json"
    model=json.loads(original.read_text())
    src=_read_lock();cos=src["cosmology"];clk=src["clock"]
    with tempfile.TemporaryDirectory(prefix="bass_axbi_rust_shortstep_") as tmp:
        p=Path(tmp);exe=p/"shortstep";inputcsv=p/"input.csv";altered=p/"corrupt.csv"
        comp=subprocess.run(["rustc","--edition=2021","-O",str(HERE/"rust_shortstep.rs"),"-o",str(exe)],
                            capture_output=True,text=True)
        if comp.returncode!=0:raise RuntimeError(comp.stderr[-1700:])
        with inputcsv.open("w",newline="") as f:
            w=csv.writer(f,lineterminator="\n");w.writerow(["family","q","a0","a1"])
            for r in model["rows"]:w.writerow([r["family"],r["q"],r["a0"],r["a1"]])
        args=[str(exe),str(inputcsv),str(cos["H0_per_s"]),str(cos["Omega_m"]),
              str(cos["Omega_r"]),str(cos["Omega_lambda"]),
              str(clk["a_ref"]),str(clk["a_end"])]
        p1=subprocess.run(args,capture_output=True,text=True)
        if p1.returncode!=0:raise RuntimeError(p1.stderr)
        output=list(csv.DictReader(io.StringIO(p1.stdout)))
        if len(output)!=model["n_intervals"]:raise RuntimeError("SOURCE_RUST_OUTPUT_COUNT")
        rows=[]
        for idx,(r,g) in enumerate(zip(model["rows"],output)):
            for name in ("family","q","a0","a1"):
                if str(g[name])!=str(r[name]) and name=="family":
                    raise AssertionError("RUST_FAMILY_BAD")
            tt=mp.mpf(r["mp_t_sec"]);bb=mp.mpf(r["mp_b"])
            rust_t=float(g["dt_s"]);rust_b=float(g["db"])
            relt=float(abs((mp.mpf(rust_t)-tt)/tt))
            relb=float(abs((mp.mpf(rust_b)-bb)/bb)) if bb else 0.
            rows.append({"index":idx,"family":r["family"],"q":r["q"],
                        "a0":r["a0"],"a1":r["a1"],
                        "relative_t_error_to_mp80":relt,
                        "relative_b_error_to_mp80":relb,
                        "rust_time_s":rust_t,"rust_delta_b":rust_b,
                        "rust_vs_py_gl4_t_diff":abs(rust_t-r["gauss4_t_sec"])})
        bad=inputcsv.read_text().splitlines()
        cols=bad[1].split(",");cols[1]="0.123456789";bad[1]=",".join(cols)
        altered.write_text("\n".join(bad)+"\n")
        badp=subprocess.run([str(exe),str(altered),*args[2:]],capture_output=True,text=True)
        if badp.returncode==0 or "AXBI_SHORTSTEP_REJECT:Q_NOT_FROZEN" not in badp.stderr:
            raise RuntimeError("RUST_INVALID_CASE_WAS_ADMITTED")
    maxt=max(x["relative_t_error_to_mp80"] for x in rows)
    maxb=max(x["relative_b_error_to_mp80"] for x in rows)
    if maxt>1e-12 or maxb>1e-12:
        raise ArithmeticError(f"ACTUAL_RUST_GAUSS4_PARITY_HOLD:{maxt},{maxb}")
    receipt={
      "schema":"bass.rei.axbi.independent_native_rust_gl4_90_intervals.v1",
      "src_Rust_sha256":hashlib.sha256((HERE/"rust_shortstep.rs").read_bytes()).hexdigest(),
      "input_lock_sha256":"46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0",
      "rustc_exit_code":0,"native_positive_exit_code":0,
      "original_90_source_intervals_sha256":hashlib.sha256(original.read_bytes()).hexdigest(),
      "actual_Rust_exit_for_invalid_q":badp.returncode,
      "invalid_q_rejection":badp.stderr.strip().splitlines()[-1],
      "n_rows":len(rows),"maximum_Rust_dt_relative_diff_mp80":maxt,
      "maximum_Rust_db_relative_diff_mp80":maxb,
      "source_input_ownership":"source-frozen original AX03 family; not owner Rust production solver",
      "original_REI_checkout_mutations":0,
      "native_science_solver_started":0,
      "rows":rows
    }
    result.parent.mkdir(parents=True,exist_ok=True)
    result.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:v for k,v in receipt.items() if k!="rows"},indent=2))
    return receipt
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();run(a.output)
