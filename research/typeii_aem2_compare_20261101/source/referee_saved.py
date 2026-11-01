"""Independent original hosted saved-data referee; no physics-code import; -O safe."""
import csv,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
SRC=HERE.parent/"ci_generated"
D=json.loads((SRC/"ORIGINAL_TYPEII_AEM2_REPLAY.json").read_text())
rows=D["records"]
if len(rows)!=96:raise RuntimeError("COUNT_RESEARCH_ROWS_MISMATCH")
with (SRC/"ORIGINAL_TYPEII_AEM2_REPLAY.csv").open() as f:
    raw=list(csv.DictReader(f))
if len(raw)!=96:raise RuntimeError("COUNT_SAVED_CSV_MISMATCH")
for i,(a,b) in enumerate(zip(rows,raw)):
    for key in ("grid","mode","alpha","N","method"):
        if str(a[key])!=str(b[key]):raise RuntimeError(f"DISCRETE_IDENTITY_MISMATCH {i} {key}")
    for key in ("relative_error","endpoint_defect"):
        if not math.isclose(float(a[key]),float(b[key]),rel_tol=2e-13,abs_tol=1e-14):
            raise RuntimeError(f"SCIENTIFIC_VALUE_MISMATCH {i} {key}")
for grid in ("axis6","lebedev26"):
 for mode in ("fixed","paired"):
  for alpha in (1,1000,100000):
   for method in ("old","kato"):
    series=sorted([r for r in rows if r["grid"]==grid and r["mode"]==mode and r["alpha"]==alpha and r["method"]==method],key=lambda r:r["N"])
    if [r["N"] for r in series]!=[4,8,16,32]:raise RuntimeError("STEP_LEVEL_MISSING")
    for i in (1,2,3):
        e0,e1=series[i-1]["relative_error"],series[i]["relative_error"]
        calculated=math.log(e0/e1,2)
        if not math.isclose(calculated,series[i]["local_order"],abs_tol=2e-12):
            raise RuntimeError("FORGED_CONVERGENCE_ORDER")
base=json.loads((HERE.parent/"LOCAL_REFERENCE_SCIENCE.json").read_text())["baseline"]
z=[r for r in rows if r["grid"]=="lebedev26" and r["mode"]=="paired" and r["alpha"]==100000 and r["N"]==32]
a=next(x for x in z if x["method"]=="old")
b=next(x for x in z if x["method"]=="kato")
if not(1.45<a["local_order"]<1.65 and 1.9<b["local_order"]<2.12):
    raise RuntimeError("PHYSICAL_STRONG_ORDER_REGRESSION")
if a["endpoint_defect"]/b["endpoint_defect"]<100:raise RuntimeError("KATO_PROJECTOR_LIFT_LOST")
if abs(a["relative_error"]-base["old_error"])>5e-7 or abs(b["relative_error"]-base["kato_error"])>5e-7:
    raise RuntimeError("ORIGINAL_SOURCE_REPLAY_PARITY_LOST")
if not(D["production_ready"] is False and D["join_J1"]=="0/2_FULL_PASS_HOLD"):
    raise RuntimeError("FALSE_PRODUCTION_ADMISSION")
print("INDEPENDENT_SAVED_RESEARCH_VERIFIED",len(rows),"KATO_RATIO",a["endpoint_defect"]/b["endpoint_defect"])
