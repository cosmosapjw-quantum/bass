"""KM2N: measured original-Bianchi exactly-once Lyalpha science plots and 12000 spectral rows."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def make(source,outdir):
    p=Path(source);d=json.loads(p.read_text());out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)
    cases=d["cases"]
    edges=np.linspace(-.5,.5,1201)
    mid=.5*(edges[:-1]+edges[1:]);width=np.diff(edges)
    rows=[];spectra=[]
    keys=("u","rho_exactly_one","original_KM2L_ballistic_rho",
          "new_once_scattered_to_ballistic_energy_ratio",
          "mean_linear_polarization","rms_linear_polarization",
          "max_linear_polarization","mean_logfreq","sigma_logfreq_bin",
          "frequency_bolometric_relative_gap","screen_eigen_min")
    for grid,case in cases.items():
        for snapshot in case["snapshots"]:
            rows.append({"grid":grid,**{k:snapshot[k] for k in keys}})
            for k,e in enumerate(snapshot["spectral_energy_bins"]):
                spectra.append({"grid":grid,"u":snapshot["u"],
                                "log_nu_over_Lya":float(mid[k]),
                                "frequency_bin_energy":float(e),
                                "energy_per_logfrequency":float(e/width[k])})
    if len(rows)!=10 or len(spectra)!=12000:
        raise ArithmeticError("actual physical epoch/frequency cardinality mismatch")
    with (out/"KM2N_10_REAL_ONCE_SCATTERED_EPOCHS.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["grid",*keys]);writer.writeheader();writer.writerows(rows)
    with (out/"KM2N_12000_REAL_SCATTERED_FREQUENCIES.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(spectra[0]));writer.writeheader();writer.writerows(spectra)
    plots=[]
    plotvars=[
      ("once_scattered_energy",("rho_exactly_one","original_KM2L_ballistic_rho"),
         "Tagged photon energy: exactly-one vs zero scattering (BASS)"),
      ("scatter_order_ratio",("new_once_scattered_to_ballistic_energy_ratio",),
         "Exactly-one / zero Thomson scatter photon energy"),
      ("once_scattered_linear_polarization",("mean_linear_polarization","rms_linear_polarization"),
         "Propagated once-scattered linear polarization"),
      ("once_scattered_frequency_centroid",("mean_logfreq",),
         "Mean ln(nu/nu_Lya) after first scatter and free geodesics"),
      ("once_scattered_spectral_spread",("sigma_logfreq_bin",),
         "Propagated first-scatter log-frequency spread")]
    for name,fields,ylabel in plotvars:
        fig,ax=plt.subplots(figsize=(7.4,4.3))
        for grid,case in cases.items():
            d=case["snapshots"]
            for f in fields:
                ax.plot([r["u"] for r in d],[r[f] for r in d],
                        lw=1.5,ls="--" if len(fields)>1 and f==fields[-1] else "-",
                        label=grid+" "+f)
        ax.set_xlabel("Original coupled Einstein-P8 proper normal time u=t/Tstar")
        ax.set_ylabel(ylabel);ax.grid(alpha=.2);ax.legend(fontsize=7)
        fig.tight_layout();fig.savefig(out/(name+".png"),dpi=150);plt.close(fig)
        plots.append(name+".png")
    fig,ax=plt.subplots(figsize=(7.4,4.3))
    for grid,case in cases.items():
        for item in (case["snapshots"][2],case["snapshots"][-1]):
            ax.plot(mid,np.array(item["spectral_energy_bins"])/width,
                    label=f"{grid} u={item['u']:.3f}",
                    linestyle="-" if item is case["snapshots"][-1] else "--",lw=1.5)
    ax.set_xlabel("ln(nu_normal/nu_Lya)")
    ax.set_ylabel("One-scatter photon energy / dln(nu/nu_Lya)")
    ax.set_xlim(-.25,.17);ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(out/"once_scattered_frequency_spectra.png",dpi=150);plt.close(fig)
    plots.append("once_scattered_frequency_spectra.png")
    manifest={"science_json_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
              "source_data_epoch_rows":len(rows),"source_data_spectral_rows":len(spectra),
              "scientific_plots":plots}
    (out/"FIGURE_SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("KM2N_SCIENCE_PLOTS",len(plots),"EPOCHS",len(rows),"SPECTRAL_ROWS",len(spectra),flush=True)
    return manifest

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    t=a.parse_args();make(t.source,t.output)
