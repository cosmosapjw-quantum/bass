"""Draw real ODE source curves only; no invented simulation trajectories."""
import argparse,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def run(source,output):
    data=json.loads(Path(source).read_text());out=Path(output);out.mkdir(exist_ok=True,parents=True)
    cases=data['cases']; r=cases['GL16']['chemical_modes']
    xa=r['angular']['epochs'];xi=r['isotropic']['epochs']
    t=np.array([x['u'] for x in xa]);normal=lambda k:np.array([v[k] for v in xa]); isotropic=lambda k:np.array([v[k] for v in xi]);
    products={}
    for basename,label,series in [
      ('x_e_reaction.png','Free-electron fraction $x_e$',[(normal('x'),'3-level Peebles chemical ODE'),(normal('xe_hyrec_prescribed'),'Original HYREC-2 imported in parent P8'),(isotropic('x'),'H-only 3-level chemical control')]),
      ('directional_lya_quadrupole.png','Ly$\\alpha$ angular escape quadrupole norm',[(normal('lya_quadrupole_norm'),'Actual anisotropic escape'),(np.array([np.linalg.norm(x['quad_theory']) for x in xa]),'Analytic optically thick shear prediction')]),
      ('sobolev_escape_rate.png','Effective Ly$\\alpha$ escape rate [s$^{-1}$]',[(normal('lambda_lya_s'),'Directional averaged escape'),(normal('lambda_lya_H_only_s'),'Normal H-only escape')]),
      ('chemistry_branching.png','3-level recombination escape factor C',[(normal('C_factor'),'Directional angle-averaged C'),(isotropic('C_factor'),'Normal H-only C')]),
      ('chemical_binding_source.png','Omitted recombination photon energy source [J m$^{-3}$ s$^{-1}$]',[(normal('Q_photon_ionization_J_m3_s_DIAGNOSTIC'),'Missing microscopic radiation source; diagnostic only')]),
    ]:
        fig,ax=plt.subplots(figsize=(7.5,4.6))
        for vals,name in series:ax.plot(t,vals,label=name,lw=1.7)
        ax.set(xlabel='Normal proper time $u=t/T_\\star$',ylabel=label)
        ax.grid(True,alpha=.28);ax.legend(fontsize=8)
        fig.tight_layout();fig.savefig(out/basename,dpi=160);plt.close(fig)
        products[basename]=hashlib.sha256((out/basename).read_bytes()).hexdigest()
    fig,ax=plt.subplots(figsize=(7.3,4.6))
    c=cases['GL16'];a=c['chemical_modes']['angular'];tau=np.array(a['ray_optical_depths']); parent=a['parent_prescribed_ray_optical_depth_mean']
    ax.hist(tau,bins=22,histtype='step',lw=1.7,label='Self-evolved chemistry, one-way')
    ax.axvline(parent,ls='--',label='Parent imported HYREC mean')
    ax.set(xlabel='Counterfactual Thomson ray depth to $u=0.25$',ylabel='Ray counts');ax.legend(fontsize=9);ax.grid(True,alpha=.25)
    fig.tight_layout();fig.savefig(out/'chemical_thomson_raydepth.png',dpi=160);plt.close(fig)
    products['chemical_thomson_raydepth.png']=hashlib.sha256((out/'chemical_thomson_raydepth.png').read_bytes()).hexdigest()
    # Source-derived physical table, every sampled 41 ODE points
    import csv
    with (out/'KM2I_2GRID_164_EPOCH_PHYSICAL_DATA.csv').open('w') as f:
      cols=['n_theta','mode','u','x','xe_hyrec_prescribed','nH_rest_m3','T_m_K','C_factor','lambda_lya_s','lya_quadrupole_norm','xprime_u','binding_energy_change_eV_per_H']
      w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
      for k,c in cases.items():
       for mode,p in c['chemical_modes'].items():
        for row in p['epochs']:
         w.writerow({**{'n_theta':c['n_theta'],'mode':mode},**{x:row[x] for x in cols[2:]}})
    products['KM2I_2GRID_164_EPOCH_PHYSICAL_DATA.csv']=hashlib.sha256((out/'KM2I_2GRID_164_EPOCH_PHYSICAL_DATA.csv').read_bytes()).hexdigest()
    (out/'PLOT_SOURCE_MANIFEST.json').write_text(json.dumps({'source_json_sha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'plot_source_sha256':products,'points':164,'scope':'actual original BASS Einstein P8 geometry plus independent Peebles chemistry ODE; not chemistry feedback'},indent=2,sort_keys=True)+'\n')
    print('KM2I_PLOTS',len(products), '164 rows')
    return products

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.source,a.output)
