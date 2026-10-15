"""Actual independent native Rust RK4/Legendre64 Einstein-Vlasov parity evidence."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,subprocess,tempfile
from pathlib import Path
import einstein_vlasov_lrs as e

HERE=Path(__file__).resolve().parent
def run(out):
    if out.exists():raise FileExistsError(out)
    lock=e._read_lock();c=lock["cosmology"];k=lock["clock"]
    with tempfile.TemporaryDirectory(prefix="bass_anisostress_rust_") as dr:
        binary=Path(dr)/"ref"
        build=subprocess.run(["rustc","--edition=2021","-O",
                             str(HERE/"rust_reference.rs"),"-o",str(binary)],
                             capture_output=True,text=True)
        if build.returncode!=0:raise RuntimeError(build.stderr[-1600:])
        args=[str(binary),*(str(v) for v in [
            c["H0_per_s"],c["Omega_m"],c["Omega_r"],c["Omega_lambda"],k["a_ref"],k["a_end"],4096])]
        z=subprocess.run(args,capture_output=True,text=True)
        if z.returncode!=0:raise RuntimeError(z.stderr[-1800:])
        result=list(csv.DictReader(io.StringIO(z.stdout)))
    if len(result)!=8:raise AssertionError("independent native case count")
    cases=[]
    for row in result:
        q=float(row["q_ref"]);A=float(row["A"]);eta=float(row["eta"])
        model=e.EinsteinVlasovLRS(e.InitialData(q,A,eta),ang_n=128,rtol=7e-13,atol=3e-15)
        r=model.at_a(model.aend)
        fields=[
          ("dt_s",r["t_elapsed_proper_s"]),
          ("b_end",r["b"]),
          ("s_over_H_end",r["s_over_H"]),
          ("H_end",r["H_per_s"]),
          ("M0_end",r["radiation_M0"]),
          ("Mdelta_end",r["radiation_Mdelta"])]
        err={}
        for name,expected in fields:
            actual=float(row[name])
            err[name]={"actual_native_rust":actual,"python_reference":expected,
                       "absolute_difference":abs(actual-expected),
                       "relative_difference":abs(actual-expected)/max(1e-30,abs(expected))}
        if err["dt_s"]["relative_difference"]>1e-10 or \
           err["b_end"]["absolute_difference"]>2e-10 or \
           err["s_over_H_end"]["absolute_difference"]>2e-10:
            raise ArithmeticError(f"RUST_PYTHON_NONPHYSICAL_PARITY:{q},{A},{eta}:{err}")
        cases.append({"q_ref":q,"A":A,"eta":eta,"errors":err})
    out.parent.mkdir(parents=True,exist_ok=True)
    result={
      "schema":"bass.rei.axbi.initial_stress_native_rust_parity.v1",
      "source_lock_SHA256":e.LOCK_SHA,
      "Rust_source_SHA256":hashlib.sha256((HERE/"rust_reference.rs").read_bytes()).hexdigest(),
      "native_actual_rustc_exit_code":0,"actual_native_rust_test_steps":4096,
      "Rust_method":"independent fixed RK4 with independent Legendre64 roots/weights from Newton, no scipy",
      "Python_method":"DOP853 with NumPy Legendre128 real source",
      "n_positive_source_cases":len(cases),
      "max_absolute_b_difference":max(v["errors"]["b_end"]["absolute_difference"] for v in cases),
      "max_absolute_s_over_H_difference":max(v["errors"]["s_over_H_end"]["absolute_difference"] for v in cases),
      "max_relative_proper_time_difference":max(v["errors"]["dt_s"]["relative_difference"] for v in cases),
      "cases":cases,
      "native_REI_original_science_run_executed":False,
      "all_positive_and_dust_background_only":True
    }
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="cases"},indent=2))
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();run(a.out)
