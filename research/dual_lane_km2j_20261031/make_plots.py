"""KM2J physical figures and machine-checkable long-format per-epoch data."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def produce(source,output):
    s=Path(source); out=Path(output); out.mkdir(parents=True,exist_ok=True)
    data=json.loads(s.read_text())
    cases=data["cases"]; rows=[]
    keys=("u","x_e","xe_parent_hyrec","H","shear_frob","rho_gamma",
          "rho_baryon","nu_live","chemical_mass_ratio",
          "chemical_rest_emission_per_u","lyalpha_quad_F","hamiltonian_normalized")
    for label,run in cases.items():
        for mode,mode_data in run["cases"].items():
            for p in mode_data["epochs"]:
                rows.append({"grid":label,"mode":mode,**{k:p[k] for k in keys}})
    csv_path=out/"KM2J_4LIVE_IVPS_164_EPOCHS.csv"
    with csv_path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=("grid","mode",*keys))
        writer.writeheader();writer.writerows(rows)

    plot_specs=[
      ("xe_dynamic_vs_parent","x_e","Electron fraction per H nucleus",1),
      ("p8_photon_energy","rho_gamma","P8 polarized photon energy (BASS)",1),
      ("einstein_shear_norm","shear_frob","Shear Frobenius norm (BASS)",1),
      ("chemical_mass_defect","chemical_mass_ratio","Baryon rest mass / initial M0",1),
      ("chemical_grey_power","chemical_rest_emission_per_u","Rest-frame grey emissivity per u",1),
      ("thomson_opacity","nu_live","Live Thomson rate per normal u",1),
    ]
    for filename,k,label,scale in plot_specs:
        fig,ax=plt.subplots(figsize=(7,4.3))
        for key in ("GL12","GL16"):
            for mode in ("full","opacity_only"):
                epochs=cases[key]["cases"][mode]["epochs"]
                u=np.array([z["u"] for z in epochs])
                y=np.array([z[k] for z in epochs])
                ax.plot(u,y,linestyle="-" if mode=="full" else "--",
                        linewidth=1.25,label=key+" "+mode)
        if k=="x_e":
            epochs=cases["GL16"]["cases"]["full"]["epochs"]
            ax.plot([e["u"] for e in epochs],[e["xe_parent_hyrec"] for e in epochs],
                    color="black",alpha=.7,linestyle=":",label="old HYREC prescription GL16")
        ax.set_xlabel("Normal proper time u=t/Tstar")
        ax.set_ylabel(label);ax.legend(fontsize=7,loc="best")
        ax.grid(alpha=.2);fig.tight_layout()
        fig.savefig(out/(filename+".png"),dpi=150)
        plt.close(fig)
    manifest={"source_data_sha256":hashlib.sha256(s.read_bytes()).hexdigest(),
              "rows":len(rows),"columns":["grid","mode",*keys],
              "science_plots":[name+".png" for name,_,_,_ in plot_specs]}
    (out/"PLOT_SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("KM2J_FIGURES",len(plot_specs),"ROWS",len(rows))
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path);p.add_argument("--output",required=True,type=Path)
    a=p.parse_args();produce(a.source,a.output)
