#!/usr/bin/env python3
"""Figures from genuinely source-matched original BASS / REI F08 geometry & tau."""
from pathlib import Path
import csv,gzip,json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
R=HERE/"results"
F=HERE/"figures"
F.mkdir(parents=True,exist_ok=True)
with gzip.open(R/"BASS_REI_F08_S0_SOURCE_MATCHED_SACHS_OBSERVABLES.csv.gz","rt") as fp:
 rows=list(csv.DictReader(fp))
primary=[r for r in rows if int(r["angular_nmu"])==32 and int(r["angular_nphi"])==64 and float(r["window_fraction"])==.95]
assert len(primary)==2048
for field, name, title, label in [
 ("DA_BI_over_FLRW","DA_RATIO_FIXED_RELATIVE_Z","Angular-diameter-distance ratio at fixed observer-relative z","D_A(Bianchi I) / D_A(FLRW)"),
 ("conditional_delta_magnitude_BI_minus_FLRW","SCREENED_STANDARD_CANDLE_DELTA_MAG","Conditional same-source geometric + Thomson screening","Delta magnitude (BI - FLRW)")
]:
 sky=np.zeros((32,64))
 for r in primary:
  sky[int(r["mu_bin"]),int(r["phi_bin"])]=float(r[field])
 fig,ax=plt.subplots(figsize=(9,4.5))
 m=ax.imshow(sky,origin="lower",extent=[0,360,-1,1],aspect="auto",interpolation="nearest")
 ax.set(xlabel="Observer azimuth [degrees]",ylabel="cos(theta)",title=title+"\nz_rel=0.0996589, F08 S0 prescribed H_i and source")
 fig.colorbar(m,ax=ax,label=label)
 fig.tight_layout()
 for ext in ["png","svg"]:
  fig.savefig(F/(name+"."+ext),dpi=160)
 plt.close(fig)
o=json.loads((R/"BASS_REI_F08_S0_MATCHED_SACHS_RESULT.json").read_text())
s=[x for x in o["physical_outputs"] if x["n_mu"]==32]
s=sorted(s,key=lambda r:r["z_relative"])
z=[x["z_relative"] for x in s]
fig,ax=plt.subplots(figsize=(7.5,4.5))
for label,attr in [("min direction","DA_BI_over_FLRW_min"),("sky mean","DA_BI_over_FLRW_mean"),("max direction","DA_BI_over_FLRW_max")]:
 ax.plot(z,[x[attr] for x in s],marker="o",label=label)
ax.set(xlabel="Observer-relative redshift z_rel (not cosmological z=0)",ylabel="DA(BI)/DA(FLRW)",title="Source-matched BASS Sachs distance: same F08 S0 electron history")
ax.legend(loc="best")
fig.tight_layout()
for ext in ["png","svg"]:fig.savefig(F/("SOURCE_MATCHED_DA_SHELLS."+ext),dpi=160)
plt.close(fig)
print("FIGURES",len(list(F.iterdir())))
