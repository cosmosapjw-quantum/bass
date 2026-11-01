"""Three distinct BASS physical-data figures from original source response CSV."""
from pathlib import Path
import argparse,csv,gzip
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.hashsalt']='bass-rei-igm-polarized-history-source-v1'
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--results',type=Path,default=HERE/'results')
parser.add_argument('--figures',type=Path,default=HERE/'figures')
args=parser.parse_args()
with gzip.open(args.results/'KM2_REI_POLARIZED_PHOTON_HISTORY_SKY_RESPONSE.csv.gz','rt') as f:rows=list(csv.DictReader(f))
rows={gl:sorted((x for x in rows if x['GL']==gl and x['observer_k']=='40'),key=lambda x:int(x['electron_panel'])) for gl in ['GL12','GL16']}
FIG=args.figures;FIG.mkdir(parents=True,exist_ok=True)

def save(name,ykey,ylabel,zero=True):
 fig,ax=plt.subplots(figsize=(8.6,4.3))
 for gl in ['GL12','GL16']:
  ss=rows[gl];x=[.5*(float(r['panel_start_u'])+float(r['panel_end_u'])) for r in ss];y=[float(r[ykey]) for r in ss]
  ax.plot(x,y,marker='o',markersize=3.4,linewidth=1,label=gl)
 if zero:ax.axhline(0,linestyle=':',linewidth=1)
 ax.set_xlabel('Original BASS electron-history panel midpoint, u=t/T*')
 ax.set_ylabel(ylabel)
 ax.set_title('BASS KM2N original Lyα, exactly one Thomson scattering, observer u=0.25')
 ax.grid(alpha=.2);ax.legend();fig.tight_layout()
 for ext in ['png','svg']:fig.savefig(FIG/(name+'.'+ext),dpi=160,metadata={'Date':None} if ext=='svg' else None)
 plt.close(fig)
save('BASS_REI_IGM_PHOTON_ENERGY_ELECTRON_HISTORY','dlogrho_dlnne_panel','d ln(observed tagged photon energy) / d ln(ne panel)')
save('BASS_REI_IGM_POLARIZATION_ELECTRON_HISTORY','dpol_dlnne_panel','d mean linear polarization fraction / d ln(ne panel)')
save('BASS_REI_IGM_SCATTER_TIME_ELECTRON_HISTORY','dmean_scatter_dlnne_panel','d source-weighted first-scatter time / d ln(ne panel)')
print('SCIENCE_FIGURES',len(list(FIG.iterdir())))
