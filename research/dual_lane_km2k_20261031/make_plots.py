"""KM2K six actual physical plots and source-table CSVs, no mock inputs."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
COLS=("grid","scenario","u","rho","mean_log_nu","std_log_nu",
      "redwing_fraction","quadrupole_frob","ratio_to_P8_rho","x_e","H")


def make(source,outdir):
    src=Path(source);out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    d=json.loads(src.read_text())
    assert set(d["data"])=={"GL12","GL16"}
    rows=[]
    spec_rows=[]
    edges=np.asarray(d["hist_logfreq_edges"],float)
    centers=.5*(edges[:-1]+edges[1:])
    delta=np.diff(edges)
    for grid,c in d["data"].items():
        for scenario,p in c["scenarios"].items():
            for ep in p["epochs"]:
                rows.append({k:(grid if k=="grid" else scenario if k=="scenario" else ep[k]) for k in COLS})
            for z in p["spectra"]:
                for iy,energy in enumerate(z["spectrum_energy_bins"]):
                    spec_rows.append({"grid":grid,"scenario":scenario,"u":z["u"],
                                      "log_frequency":float(centers[iy]),
                                      "spectral_energy_density":float(energy/delta[iy]),
                                      "bin_energy":energy})
    f=out/"KM2K_164_EPOCH_SPECTRAL_PHYSICS.csv"
    with f.open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=COLS);w.writeheader();w.writerows(rows)
    g=out/"KM2K_20_SPECTRAL_SNAPSHOTS_24000_ROWS.csv"
    with g.open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(spec_rows[0]));w.writeheader();w.writerows(spec_rows)
    specs=[
        ("frequency_centroid","mean_log_nu","Escaped Ly-alpha log-frequency centroid"),
        ("spectral_width","std_log_nu","Escaped Ly-alpha log-frequency standard deviation"),
        ("redwing_fraction","redwing_fraction","Escaped photons with log(nu/nu_alpha)<-0.01"),
        ("line_energy_fraction_P8","ratio_to_P8_rho","Tagged Ly-alpha energy / original P8 photon rho"),
        ("angular_quadrupole","quadrupole_frob","Tagged line angular quadrupole Frobenius norm"),
    ]
    for filename,k,ylabel in specs:
        fig,ax=plt.subplots(figsize=(7,4.2))
        for grid in ("GL12","GL16"):
            for scenario in ("shear","H_only"):
                q=d["data"][grid]["scenarios"][scenario]["epochs"][1:]
                ax.plot([x["u"] for x in q],[x[k] for x in q],
                        label=grid+" "+scenario,ls="-" if scenario=="shear" else "--")
        ax.set_xlabel("Original Einstein–P8 normal time u=t/Tstar")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8);ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(out/(filename+".png"),dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.2))
    for grid in ("GL12","GL16"):
        for scenario in ("shear","H_only"):
            final=d["data"][grid]["scenarios"][scenario]["spectra"][-1]
            y=np.asarray(final["spectrum_energy_bins"])/delta
            ax.plot(centers,y,label=grid+" "+scenario,
                    ls="-" if scenario=="shear" else "--")
    ax.set_xlim(-.23,.18)
    ax.set_xlabel("ln(nu_normal/nu_Lya) at u=0.25")
    ax.set_ylabel("d rho_Lya / d ln(nu/nu_Lya) (tagged)")
    ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/"escaped_line_frequency_profile.png",dpi=150);plt.close(fig)
    plots=[q+".png" for q,_,_ in specs]+["escaped_line_frequency_profile.png"]
    manifest={"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
              "epoch_rows":len(rows),"frequency_snapshot_rows":len(spec_rows),
              "spectral_slices":20,"physical_pngs":plots}
    if len(rows)!=164 or len(spec_rows)!=24000:raise ArithmeticError("source data cardinality mismatch")
    (out/"PLOT_SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("KM2K_PLOTS",len(plots),"EPOCHS",len(rows),"SPECTRAL_ROWS",len(spec_rows),flush=True)
    return manifest


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();make(a.source,a.output)
