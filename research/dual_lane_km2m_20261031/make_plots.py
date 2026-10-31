"""KM2M source-derived plots and exact 10x1200 bin physical CSV."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def make(source,destination):
    s=Path(source);root=Path(destination);root.mkdir(parents=True,exist_ok=True)
    d=json.loads(s.read_text())
    cases=d["snapshots"];edges=np.asarray(d["frequency_bin_edges"],float)
    freq=.5*(edges[1:]+edges[:-1])
    spectra=[]
    epochs=[]
    for grid,case in cases.items():
        for rec in case["measurements"]:
            epoch={k:v for k,v in rec.items()
                   if k not in ("incoming_electron_frame_spectrum",
                                "gained_electron_frame_spectrum",
                                "gained_normal_frame_spectrum",
                                "normal_gain_angle_energy","normal_loss_angle_energy",
                                "normal_gain_linear_polarization_fraction")}
            epochs.append({"grid":grid,**epoch})
            for i,y in enumerate(freq):
                spectra.append({
                    "grid":grid,"u":rec["u"],"y_logfreq_e_bin":float(y),
                    "electron_incoming_energy_bin":rec["incoming_electron_frame_spectrum"][i],
                    "electron_gain_energy_bin":rec["gained_electron_frame_spectrum"][i],
                    "normal_gain_energy_bin":rec["gained_normal_frame_spectrum"][i]
                })
    if len(epochs)!=10 or len(spectra)!=12000:
        raise ArithmeticError("real source cardinality mismatch")
    numbers=("u","incoming_ballistic_tagged_rho",
             "incoming_first_event_energy_rate",
             "normal_first_gain_energy_rate","normal_gain_over_loss",
             "linear_polarization_mean","linear_polarization_rms",
             "linear_polarization_max",
             "electron_rest_source_gain_relative_error",
             "normal_scattered_logfrequency_centroid",
             "electron_rest_scattered_logfrequency_centroid",
             "P8_gain_bolometric_parity_relative_error")
    with (root/"KM2M_FIRST_GAIN_10_EPOCHS.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=("grid",*numbers),extrasaction="ignore")
        w.writeheader();w.writerows(epochs)
    with (root/"KM2M_THOMSON_12000_PHYSICAL_FREQUENCY_BINS.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(spectra[0]))
        w.writeheader();w.writerows(spectra)
    figures=[
        ("first_gain_vs_loss_energy","incoming_first_event_energy_rate",
         "normal_first_gain_energy_rate","First Thomson energy event rate (BASS/u)"),
        ("first_scatter_polarization","linear_polarization_mean",
         "linear_polarization_rms","Thomson generated linear polarization"),
        ("bulk_compton_energy_exchange","normal_gain_over_loss",
         None,"normal photon gain / input ballistic loss"),
        ("scattered_frequency_centroid","normal_scattered_logfrequency_centroid",
         "electron_rest_scattered_logfrequency_centroid","mean log-frequency"),
    ]
    for stem,a,b,ylabel in figures:
        fig,ax=plt.subplots(figsize=(7.5,4.5))
        for grid,case in cases.items():
            x=case["measurements"]
            ax.plot([z["u"] for z in x],[z[a] for z in x],label=grid+" "+a,lw=1.6)
            if b is not None:
                ax.plot([z["u"] for z in x],[z[b] for z in x],
                        label=grid+" "+b,ls="--",lw=1.5)
        ax.set_xlabel("Original Einstein P8 normal time u=t/Tstar")
        ax.set_ylabel(ylabel);ax.grid(alpha=.25);ax.legend(fontsize=7)
        fig.tight_layout();fig.savefig(root/(stem+".png"),dpi=150);plt.close(fig)
    for stem,keys,ylab in [
        ("Thomson_first_gain_normal_spectrum",("gained_normal_frame_spectrum",),"Normal frame first gain spectral rate per bin"),
        ("electron_frame_redistribution",("incoming_electron_frame_spectrum",
                                          "gained_electron_frame_spectrum"),"Electron frame input / gain spectral rate per bin")
    ]:
        fig,ax=plt.subplots(figsize=(7.5,4.5))
        for grid,case in cases.items():
            fin=case["measurements"][-1]
            for key in keys:
                y=np.asarray(fin[key])
                ax.plot(freq,y,label=grid+" "+key,ls="--" if key.startswith("incoming") else "-")
        ax.set_xlabel("ln(nu/nu_Lya), frame as labeled")
        ax.set_ylabel(ylab)
        ax.set_xlim(-.22,.19)
        ax.grid(alpha=.25);ax.legend(fontsize=7)
        fig.tight_layout();fig.savefig(root/(stem+".png"),dpi=150);plt.close(fig)
    plots=[i[0]+".png" for i in figures]+[
      "Thomson_first_gain_normal_spectrum.png","electron_frame_redistribution.png"]
    manifest={"source_sha256":hashlib.sha256(s.read_bytes()).hexdigest(),
              "epochs":len(epochs),"spectral_bins":len(spectra),
              "physical_PNG":plots}
    (root/"PLOT_SOURCE_MANIFEST.json").write_text(
        json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("KM2M_SCIENTIFIC_PLOTS",len(plots),"EPOCHS",len(epochs),
          "FREQUENCY_BINS",len(spectra),flush=True)
    return manifest


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();make(a.source,a.output)
