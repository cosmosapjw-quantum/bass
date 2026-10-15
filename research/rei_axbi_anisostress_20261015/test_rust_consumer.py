"""Native Rust stress table consumer positive/negative actual execution receipts."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,subprocess,tempfile
from pathlib import Path
import einstein_vlasov_lrs as e
HERE=Path(__file__).resolve().parent
CSV=HERE/"evidence/AX03_INITIAL_PI_TABLES/AX03_INITIAL_PI_BACKGROUND.csv"

def run(output):
    if output.exists():raise FileExistsError(output)
    original=hashlib.sha256(CSV.read_bytes()).hexdigest()
    c=e._read_lock()["cosmology"]
    with tempfile.TemporaryDirectory(prefix="bass_pi_stress_native_verify_") as tmp:
        root=Path(tmp);binary=root/"consumer"
        comp=subprocess.run(["rustc","--edition=2021","-O",str(HERE/"rust_stress_consumer.rs"),"-o",str(binary)],capture_output=True,text=True)
        if comp.returncode!=0:raise RuntimeError(comp.stderr)
        cli=[str(binary),str(CSV),str(c["H0_per_s"]),str(c["Omega_r"])]
        good=subprocess.run(cli,capture_output=True,text=True)
        if good.returncode!=0:raise RuntimeError("NATIVE_STRESS_CONSUMER_FAILED:"+good.stderr)
        record=json.loads(good.stdout)
        if record["rows"]!=8517 or record["physical_checks"]!="PASS":
            raise AssertionError("native consumer incomplete")
        src=CSV.read_text().splitlines()
        keys=src[0].split(",");index=keys.index("H_per_s")
        # Mutate a signed nontrivial row, independent H^2 vs source re-evaluation
        row=src[700].split(",");row[index]=str(1.05*float(row[index]));src[700]=",".join(row)
        corrupted=root/"corrupted_H.csv"
        corrupted.write_text("\n".join(src)+"\n")
        neg=subprocess.run([str(binary),str(corrupted),*cli[2:]],capture_output=True,text=True)
        if neg.returncode!=3 or "ANISOSTRESS_CSV_REJECT:NATIVE_EINSTEIN_HAMILTONIAN" not in neg.stderr:
            raise AssertionError("native source Hamiltonian negative control failed")
        src2=CSV.read_text().splitlines();col=keys.index("pi_parallel_J_m3")
        row2=src2[700].split(",");row2[col]=str(1.1*float(row2[col])+1e-11);src2[700]=",".join(row2)
        corrupted2=root/"corrupted_pi.csv";corrupted2.write_text("\n".join(src2)+"\n")
        neg2=subprocess.run([str(binary),str(corrupted2),*cli[2:]],capture_output=True,text=True)
        if neg2.returncode!=3 or "ANISOSTRESS_CSV_REJECT:PI_TRACE_NONZERO" not in neg2.stderr:
            raise AssertionError("native pressure trace negative control failed")
    if hashlib.sha256(CSV.read_bytes()).hexdigest()!=original:
        raise AssertionError("signed source CSV changed!")
    receipt={
      "schema":"bass.rei.axbi.native_einstein_vlasov_csv_consumer.v1",
      "original_SHA256":original,"Rust_source_SHA256":hashlib.sha256((HERE/"rust_stress_consumer.rs").read_bytes()).hexdigest(),
      "positive_returncode":good.returncode,"positive":record,
      "negative_H_returncode":neg.returncode,"negative_H":neg.stderr.strip().splitlines()[-1],
      "negative_pi_returncode":neg2.returncode,"negative_pi":neg2.stderr.strip().splitlines()[-1],
      "positive_input_unchanged":True,"actual_native_stress_run":"rustc isolated stdlib consumer"}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2)[:1300])
    return receipt
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();run(a.out)
