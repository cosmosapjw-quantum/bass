"""KM2L 246 physical spectral epochs, 36000 frequency rows and six actual science plots."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def make(source,output):
    p=Path(source)
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    d=json.loads(p.read_text())
    rows=[];spec=[]
    cols=("grid","mode","u","rho","ratio_to_P8_rho","mean_log_nu",
          "std_log_nu","redwing_fraction","quadrupole_frob",
          "first_collision_energy_rate","max_packet_thomson_tau",
          "mean_packet_survival")
    edges=np.asarray(d["hist_logfreq_edges"],float)
    ctr=(edges[:-1]+edges[1:])/2
    diff=np.diff(edges)
    modes=("shear_thomson","shear_free","Honly_thomson")
    for key,case in d["cases"].items():
        for mode in modes:
            for row in case["scenarios"][mode]["epochs"]:
                rows.append({k:(key if k=="grid" else mode if k=="mode" else row[k]) for k in cols})
            for snap in case["scenarios"][mode]["spectra"]:
                for i,e in enumerate(snap["spectrum_energy_bins"]):
                    spec.append({"grid":key,"mode":mode,"u":snap["u"],
                                 "log_frequency":float(ctr[i]),
                                 "spectral_energy_per_logfreq":float(e/diff[i]),
                                 "bin_energy":float(e)})
    if len(rows)!=246 or len(spec)!=36000:
        raise ArithmeticError("physical source row count mismatch")
    with (out/"KM2L_246_SPECTRAL_EPOCHS.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(cols));w.writeheader();w.writerows(rows)
    with (out/"KM2L_36000_FREQUENCY_BINS.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(spec[0]));w.writeheader();w.writerows(spec)

    specs=[
       ("ballistic_thomson_survival","mean_packet_survival",
        "Ballistic survival fraction (energy-weighted)"),
       ("first_thomson_scatter_events","first_collision_energy_rate",
        "Tagged first-scatter energy event rate / normal u"),
       ("transmitted_frequency_centroid","mean_log_nu",
        "Mean log(nu/nu_Lya)"),
       ("redwing_probability","redwing_fraction",
        "P[log(nu/nu_Lya) < -0.01]"),
       ("tagged_line_energy","rho",
        "Tagged unscattered Ly-alpha energy (BASS units)"),
    ]
    for stem,k,ylabel in specs:
        fig,ax=plt.subplots(figsize=(7.5,4.5))
        for grid in ("GL12","GL16"):
            for mode in modes:
                q=d["cases"][grid]["scenarios"][mode]["epochs"][1:]
                ax.plot([x["u"] for x in q],[x[k] for x in q],
                        lw=1.3,label=f"{grid} {mode}",
                        ls={"shear_thomson":"-","shear_free":":",
                            "Honly_thomson":"--"}[mode])
        ax.set_xlabel("Original Bianchi normal time u=t/Tstar")
        ax.set_ylabel(ylabel);ax.legend(fontsize=7)
        ax.grid(alpha=.2);fig.tight_layout()
        fig.savefig(out/(stem+".png"),dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    for grid in ("GL12","GL16"):
        for mode in modes:
            x=d["cases"][grid]["scenarios"][mode]["spectra"][-1]
            y=np.asarray(x["spectrum_energy_bins"])/diff
            ax.plot(ctr,y,ls={"shear_thomson":"-","shear_free":":",
                               "Honly_thomson":"--"}[mode],
                    label=grid+" "+mode)
    ax.set_xlim(-.25,.2)
    ax.set_xlabel("ln(nu_normal/nu_Lya) at u=0.25")
    ax.set_ylabel("Tagged Ly-alpha energy density / d log-frequency")
    ax.legend(fontsize=7);ax.grid(alpha=.2);fig.tight_layout()
    fig.savefig(out/"unscattered_Lya_spectral_shape.png",dpi=140);plt.close(fig)
    manifest={"source_data_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
              "physical_epochs":len(rows),"frequency_rows":len(spec),
              "spectral_snapshots":30,"physical_plots":[x[0]+".png" for x in specs]+
              ["unscattered_Lya_spectral_shape.png"]}
    (out/"FIGURE_PROVENANCE.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print("KM2L_SCIENCE_PLOTS",len(manifest["physical_plots"]),
          "EPOCHS",len(rows),"SPECTRAL_ROWS",len(spec),flush=True)
    return manifest


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    z=a.parse_args();make(z.source,z.output)
