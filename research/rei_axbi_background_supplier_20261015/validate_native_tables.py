"""Compile portable Rust table consumer off-owner and test strict physical failures."""
from __future__ import annotations
import argparse,csv,io,json,os,subprocess,tempfile,hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
INPUT=HERE/"evidence/AX03_SUPPLIER_TABLES/AX03_BACKGROUND.csv"

def run(output:Path):
    if output.exists():raise FileExistsError(output)
    before=hashlib.sha256(INPUT.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="axbi_native_consumer_") as t:
        root=Path(t)
        binary=root/"axbi_table_consumer"
        code=HERE/"rust_bridge/src/table_consumer.rs"
        comp=subprocess.run(["rustc","--edition=2021","-O",str(code),"-o",str(binary)],capture_output=True,text=True)
        if comp.returncode!=0:raise RuntimeError(comp.stderr[-1200:])
        valid=subprocess.run([str(binary),str(INPUT)],capture_output=True,text=True)
        if valid.returncode!=0:raise RuntimeError(valid.stderr)
        result=json.loads(valid.stdout)
        if result.get("rows")!=3006 or result.get("constraint_checks")!="PASS":
            raise AssertionError("original native source data validation failed")
        # Actual forbidden physics perturbation: H_mean no longer satisfies constraint.
        source=INPUT.read_text().splitlines()
        fields=source[0].split(",")
        i=fields.index("H_mean_per_s")
        assert len(source)>100
        row=source[100].split(",")
        row[i]=str(float(row[i])*1.05)
        source[100]=",".join(row)
        altered=root/"tampered.csv"
        altered.write_text("\n".join(source)+"\n")
        invalid=subprocess.run([str(binary),str(altered)],capture_output=True,text=True)
        if invalid.returncode==0 or "REI_AXBI_TABLE_REJECT" not in invalid.stderr:
            raise AssertionError("native Rust consumer failed to refuse bad H constraint")
        checksum_after=hashlib.sha256(INPUT.read_bytes()).hexdigest()
        if checksum_after!=before:raise AssertionError("positive original table mutated")
        rec={"schema":"bass.rei.axbi.native_consumer_negative_test.v1",
          "input_sha256":before,"compiler":"actual rustc --edition=2021 -O",
          "positive":{"code":valid.returncode,"actual":result},
          "negative":{"code":invalid.returncode,"rejection":invalid.stderr.strip()},
          "original_input_identity_preserved":True,
          "original_owner_Rust_files_changed":False}
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(rec,indent=2)+"\n")
        print(json.dumps(rec,indent=2)[:1300])
        return rec

if __name__=="__main__":
    pa=argparse.ArgumentParser();pa.add_argument("--output",type=Path,required=True)
    run(pa.parse_args().output)
