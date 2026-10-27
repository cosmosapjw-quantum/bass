"""Plot only saved consumer outputs; no new scientific calculation or rerun."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from binding import ROOT,write_json


def main():
    out=ROOT/'results'
    births=json.loads((out/'BIRTH_ROWS.json').read_text())['rows']
    endpoints=json.loads((out/'SAVED_ENDPOINT_BRIDGE.json').read_text())['rows']
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for label,color in [('ISO','#1f77b4'),('ANISO','#d95f02')]:
        rows=[r for r in births if r['fixture']==label]; tau=[r['tau_birth'] for r in rows]
        axes[0,0].plot(tau,[r['n_b_m3'] for r in rows],label=label,color=color)
        axes[0,1].plot(tau,[r['T_J_m3'][0][0] for r in rows],label=label,color=color)
        axes[1,0].plot(tau,[r['pi_J_m3'][0][0] for r in rows],label=label+' xx',color=color)
        axes[1,0].plot(tau,[r['pi_J_m3'][2][2] for r in rows],label=label+' zz',color=color,linestyle='--')
        axes[1,1].plot(tau,[max(abs(x) for rr in r['signed_representation_residuals']['spatial'] for x in rr) for r in rows],label=label,color=color)
    for ax,title,ylabel in zip(axes.flat,['Integrated birth number','Integrated birth energy','Signed birth anisotropic stress','Spatial representation residual'],['n_b [m⁻³]','E_b n_b [J m⁻³]','π component [J m⁻³]','max |ΔTij| / (E_b n_b)']):
        ax.set(title=title,xlabel='birth τ',ylabel=ylabel);ax.grid(alpha=.2);ax.legend()
    fig.suptitle('Actual saved B3c source receipts · manufactured detached f₊=0 model\nNumerical residuals are separate from unspecified physical source errors',fontsize=13)
    fig.savefig(out/'ACTUAL_BIRTHS.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for index,label in enumerate(['ISO','ANISO']):
        rows=[r for r in endpoints if r['fixture']==label];tau=[r['tau'] for r in rows]
        for sector,name,color in [(0,'lower rest R','#777777'),(1,'excitation X','#d95f02'),(2,'radiation','#1f77b4')]:
            axes[0,index].plot(tau,[r['rho_hat'][sector] for r in rows],label=name,color=color)
        axes[0,index].set_yscale('symlog',linthresh=1e-13)
        axes[0,index].set(title=label+' sector density',ylabel='αL T00',xlabel='endpoint τ')
        for component,color in [(0,'#1f77b4'),(1,'#d95f02'),(2,'#2ca02c')]:
            axes[1,index].plot(tau,[r['pi_hat'][2][component][component] for r in rows],label=['πxx','πyy','πzz'][component],color=color)
        axes[1,index].set(title=label+' signed radiation stress',ylabel='αL π',xlabel='endpoint τ')
    for ax in axes.flat:ax.grid(alpha=.2);ax.legend()
    fig.suptitle('514 saved endpoints · cold R/X sectors and radiation · source rates U=J=0',fontsize=13)
    fig.savefig(out/'SECTOR_STRESS.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.2),layout='constrained')
    for label,color in [('ISO','#1f77b4'),('ANISO','#d95f02')]:
        rows=[r for r in endpoints if r['fixture']==label];tau=[r['tau'] for r in rows]
        axes[0].plot(tau,[max(abs(x) for t in r['signed_roundtrip_residual_on_sector_scale'] for rr in t for x in rr) for r in rows],label=label,color=color)
        axes[1].plot(tau,[r['radiation_trace_residual'] for r in rows],label=label,color=color)
    for ax,title,ylabel in zip(axes,['SI/core roundtrip','Radiation trace'],['max |ΔT| / sector scale','(tr Tij − T00) / radiation scale']):
        ax.set(title=title,xlabel='endpoint τ',ylabel=ylabel);ax.grid(alpha=.2);ax.legend()
    fig.suptitle('Representation residuals only · actual zeros retained · physical radii remain null')
    fig.savefig(out/'GEOMETRY_RESIDUALS.png',dpi=160);plt.close(fig)
    write_json(out/'FIGURE_METADATA.json',dict(actual_input_only=True,zero_handling='LINEAR_AXES_RETAIN_EXACT_ZEROS',
        physical_uncertainty_plotted=False,figures=['ACTUAL_BIRTHS.png','SECTOR_STRESS.png','GEOMETRY_RESIDUALS.png']))
    print('Saved three actual-input figures.')


if __name__=='__main__':main()
