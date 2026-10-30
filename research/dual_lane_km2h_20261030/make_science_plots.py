"""Physical-ODE-source plots/CSV, never interpolated fabricated evolution.

Reads 41 actual DOP853 dense-output evaluations stored by external_opacity_bianchi.
Each plot has a separate figure and unit-labeled axis; no theory-independent
observational-accuracy claim. No network or source modification.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SERIES={
 'electron_fraction':('x_e (free electrons per H nucleus)','Source-driven ionization, z_vol proxy','x_e'),
 'thomson_rate':('nu_rest = n_e sigma_T c Tstar','Normal-time free-electron Thomson rate','nu_rest'),
 'photon_anisotropy':('||pi_gamma||_F (dimensionless)','Original P8 photon anisotropic stress','photon_pi_norm'),
 'gravitational_shear':('||sigma - zeta sigma_initial||_F','Einstein shear sourced by total anisotropic stress','sourced_shear_norm'),
 'expansion_H':('H Tstar (dimensionless)','Einstein Bianchi-I expansion','H_dimless'),
}
LABELS={'hyrec':'HYREC-2 external x_e','class':'CLASS HyRec2020 external x_e','frozen_hyrec':'Fixed initial HYREC-2 x_e'}


def main(source:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    p=json.loads(source.read_text())
    assert p['schema']=='bass.km2h.external_flrw_opacity_Einstein_Bianchi_I.v1'
    data={mode:p['cases']['GL16_'+mode]['dense_physical_curve_41epochs'] for mode in LABELS}
    manifest={}
    tab=[]
    for mode,rows in data.items():
        for r in rows:tab.append({'mode':mode,**r})
    cols=['mode']+list(data['hyrec'][0])
    path=out/'BASS_KM2H_EXTERNAL_REAL_41_EPOCH_CURVES.csv'
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(tab)
    manifest[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    # Preserve every direct physical epoch and every GL24 force quadrature sample.
    all_dense=[];five=[];forcing=[];depth_rows=[]
    for k,c in sorted(p['cases'].items()):
        for row in c['dense_physical_curve_41epochs']:
            all_dense.append({'case':k,**row})
        for row in c['epochs']:
            five.append({'case':k,'u':row['u'],'H':row['H'],
                'rho_gamma':row['rho_photon'],'rho_baryon':row['total_baryon_density'],
                'xe':row['xe_external_per_hydrogen'],'nu':row['nu_rest_tstar'],
                'Hamiltonian_norm':row['hamiltonian_normalized'],
                'momentum_norm':row['momentum_constraint_normalized'],
                'z_volume_proxy':row['z_volume_proxy'],
                'photon_pi_frobenius':float(np.linalg.norm(np.asarray(row['photon_anisotropic_pressure']))),
                'charge_C_m3':row['charge_C_m3']})
        for row in c['balances']['force_gap_time_rows']:
            forcing.append({'case':k,'u':row['u'],**{f'deltaF_{i}':row['gap'][i] for i in range(4)}})
        for j,tau in enumerate(c['optical_depth_ray_list']):
            depth_rows.append({'case':k,'ray_index':j,'tau':tau})
    for basename,rows in [
        ('BASS_KM2H_EXTERNAL_6CASE_41EPOCH.csv',all_dense),
        ('BASS_KM2H_EXTERNAL_6CASE_5EPOCH_STRESS.csv',five),
        ('BASS_KM2H_EXTERNAL_GL24_P8_FORCE_GAPS.csv',forcing),
        ('BASS_KM2H_EXTERNAL_DIRECTIONAL_TAU.csv',depth_rows),
    ]:
        target=out/basename
        with target.open('w') as fi:
            writer=csv.DictWriter(fi,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
        manifest[basename]=hashlib.sha256(target.read_bytes()).hexdigest()
    for name,(ylabel,title,key) in SERIES.items():
        fig,ax=plt.subplots(figsize=(8.4,5.2))
        for mode,rows in data.items():
            ax.plot([r['u'] for r in rows],[r[key] for r in rows],label=LABELS[mode],linewidth=1.7)
        ax.set(xlabel='Normal proper time u = t / Tstar',ylabel=ylabel,title=title)
        ax.grid(True,alpha=.25);ax.legend(loc='best',fontsize=9)
        fig.tight_layout()
        target=out/(name+'.png')
        fig.savefig(target,dpi=170);plt.close(fig)
        manifest[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
    fig,ax=plt.subplots(figsize=(8.4,5.2))
    for mode in LABELS:
        v=p['cases']['GL16_'+mode]['optical_depth_ray_list']
        ax.hist(v,bins=25,histtype='step',linewidth=1.7,label=LABELS[mode])
    ax.set(xlabel='Ray-direction Thomson optical depth to u=0.25',ylabel='Angular-grid ray count',title='Original P8 directional scattering depths')
    ax.legend(fontsize=9);ax.grid(True,alpha=.25)
    fig.tight_layout()
    target=out/'directional_optical_depth_histogram.png'
    fig.savefig(target,dpi=170);plt.close(fig)
    manifest[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
    summary={'source_json_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'plots':manifest,'series_obtained_from':'full DOP853 Einstein-Boltzmann ODE states at 41 actual evaluation times; no FLRW anisotropic recombination solve',
             'units':'Dimensionless u; synthetic BASS normalization, NOT observed universe',
             'n_theta':16,'n_phi':32}
    (out/'PLOT_SOURCE_MANIFEST.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('KM2H_PLOTS_PASS',json.dumps({'plots':len(manifest)-1,'csv_rows':len(tab),'source_sha256':summary['source_json_sha256']},sort_keys=True))
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--output-dir',required=True,type=Path)
    x=ap.parse_args();main(x.source,x.output_dir)
