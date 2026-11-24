"""Extract a recombination-only, externally prescribed x_e(ln(a/a_emit))."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess

PIN = "4cffa8a0abdb104a40cac17cfc65593bec909fb3"
SOURCE = "research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/producer_inputs/independent_integer_z_history.csv"
SHA = "c7c113af50fd49e7937a3bfef15ac2e295fe51cc161e83196bc921e0f02c98ce"
Z_EMIT = 1100

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rec_repo",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    blob=subprocess.check_output(["git","-C",str(a.rec_repo),"show",f"{PIN}:{SOURCE}"])
    if hashlib.sha256(blob).hexdigest()!=SHA:
        raise ValueError("original REC source mismatch")
    rows=[]
    for item in csv.DictReader(io.StringIO(blob.decode())):
        z=int(item["z"])
        xe=float(item["xe"])
        if z<=Z_EMIT: rows.append((z,xe))
    if [z for z,_ in rows] != list(range(Z_EMIT,-1,-1)) or any(not math.isfinite(x) or x<0 for _,x in rows):
        raise ValueError("invalid redshift support or electron fraction")
    zp1=1+Z_EMIT
    nh0=11.223846333047*0.0224*(1-0.2454)
    wr=4.48162687719e-7*2.7255**4*(1+.227107317660239*3.03821934419124)
    h=3.2407792896393e-18*math.sqrt(0.14309694000000003*zp1**3+.31113726660800006+wr*zp1**4)
    a.output.mkdir(parents=True,exist_ok=True)
    tab=a.output/"hyrec_xe.tsv"
    with tab.open("w") as f:
        f.write("eta\txe_per_H\n")
        for z,xe in rows: f.write(f"{math.log(zp1/(1+z)):.17g}\t{xe:.17g}\n")
    data=dict(source_repo="cosmosapjw-quantum/rec_bianchi",commit=PIN,source=SOURCE,
              source_sha256=SHA,source_cosmology=["scripts/c_harness/original_hyrec_low_z_to_end_harness.c",
              "src/full_bianchi_hyrec/trajectory/primordial_2012_helium.py"],q=0,
              chemistry="Externally prescribed HyRec recombination only, no astrophysical reionization",
              z_emit=Z_EMIT,z_terminal=0,rows=len(rows),eta_terminal=math.log(zp1),
              n_h_emit_m3=nh0*zp1**3,h_emit_s=h,xe_emit=rows[0][1],xe_terminal=rows[-1][1],
              table_sha256=hashlib.sha256(tab.read_bytes()).hexdigest())
    (a.output/"source.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data))
if __name__=="__main__":
    main()
