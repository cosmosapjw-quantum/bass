"""Plot finalized S11 stored results; never imports or executes a projector."""
from pathlib import Path
import csv
from decimal import Decimal as D
import hashlib
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/bass_s11_matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import numpy as np

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent.parent
RUN = UNIT/"evidence/run_r1"
result = json.loads((RUN/"RETURN.json").read_text())
assert result["status"] == "PASS_SCOPED" and result["check_count"] == 101
responses = json.loads((RUN/"ANGULAR_RESPONSES.json").read_text())
projections = json.loads((RUN/"PROJECTIONS.json").read_text())
asymptotics = json.loads((RUN/"SMALL_STRAIN_CHECKS.json").read_text())
inputs = json.loads((RUN/"FIXED_INPUTS.json").read_text())
by_input = {r["id"]:r for r in inputs}
grid = {D(k)/40 for k in range(-24,25)}

def curve(identity, nonzero=False):
    return sorted((r for r in responses if r["id"] == identity and D(r["d"]) in grid
                   and (not nonzero or D(r["d"]) != 0)), key=lambda r:D(r["d"]))

colors = {"P24":"#0072B2", "P246":"#D55E00", "quartic":"#009E73"}
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10.5,
    "axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"bold",
    "axes.labelsize":11,"axes.titlesize":12,"legend.fontsize":9,
    "figure.facecolor":"white","axes.facecolor":"white","savefig.facecolor":"white"})
fig, axes = plt.subplots(2,2,figsize=(14,9.8))
fig.subplots_adjust(left=.075,right=.975,bottom=.14,top=.87,wspace=.30,hspace=.47)
fig.suptitle("S11: positive birth weights and finite-strain angular response",x=.075,y=.97,ha="left",fontsize=18,weight="bold")
fig.text(.075,.925,"Frozen source 7fb9b83cba01 | New isolated birth candidates | P24 / P246 exact gate: 3 × 10⁻¹⁵",fontsize=11,color="#444444")

ax=axes[0,0]
names=["b9_n64","b9_n128","b9_n256","b6_n64"]
extent=[max(float(x)**2 for x in by_input[n]["mu"]) for n in names]
barcolors=["#D55E00","#009E73","#009E73","#009E73"]
ax.barh(np.arange(4),extent,color=barcolors,height=.56)
for i,x in enumerate(extent):ax.text(x+.012,i,f"{x:.6f}",va="center",fontsize=10)
ax.axvline(5/7,color="#333333",ls="--",lw=1.3)
ax.text(5/7+.008,-.73,"P246 necessary: 5/7",fontsize=9,color="#333333")
ax.set(yticks=np.arange(4),yticklabels=names,xlim=(0,1.105),ylim=(3.6,-.9),
       xlabel=r"Largest stored $z=\mu^2$ (dimensionless)",title="a  Fixed support can make P246 impossible")
ax.text(.02,.98,"Orange: P246 infeasible\nGreen: every facet slack positive",
        transform=ax.transAxes,va="top",fontsize=8.5,bbox={"facecolor":"white","edgecolor":"none","alpha":.94})
ax.grid(axis="x",alpha=.2);ax.set_axisbelow(True)

ax=axes[0,1]
maxima={}
for label,identity in (("P24","dyadic_uniform_P4"),("P246","dyadic_uniform_P6")):
    r=curve(identity);x=[float(D(a["d"])) for a in r];y=[float(D(a["signed_error"])) for a in r]
    ax.plot(x,y,color=colors[label],lw=2,marker="o",ms=2.8,label=label)
    row=max(r,key=lambda a:abs(D(a["signed_error"])))
    maxima[label]={"max_abs":float(abs(D(row["signed_error"]))),"argmax_d":row["d"]}
ax.axhline(0,color="#999999",lw=.8)
ax.set(xlabel=r"Strain since birth $d=b(x)-b(u)$",ylabel=r"Signed angular bias $\mathcal{A}-\mathcal{A}_{iso}$",
       title="b  Finite-d bias need not decrease")
ax.text(.98,.05,"Uniform dyadic 7-ray support\n"+f"max |bias|: P24 {maxima['P24']['max_abs']:.5f}; P246 {maxima['P246']['max_abs']:.5f}",
        transform=ax.transAxes,ha="right",fontsize=9,bbox={"facecolor":"white","edgecolor":"none","alpha":.9})
ax.legend(loc="upper left",frameon=False);ax.grid(alpha=.2)

ax=axes[1,0]
styles=[("b9_n64", "#6f6f6f",(4,)),("b9_n128", "#0072B2",(4,6)),("b9_n256", "#D55E00",(4,6))]
for case,color,orders in styles:
    for order in orders:
        r=curve(f"{case}_P{order}",nonzero=True)
        for sign in (-1,1):
            rr=[a for a in r if D(a["d"])*sign>0]
            ax.semilogy([float(D(a["d"])) for a in rr],[float(abs(D(a["signed_error"]))) for a in rr],
                        color=color,lw=1.8,ls="--" if order==4 else "-",
                        label=f"{case}: {'P24' if order==4 else 'P246'}" if sign<0 else None)
ax.set(xlabel=r"Strain since birth $d$",ylabel=r"Absolute angular bias $|\mathcal{A}-\mathcal{A}_{iso}|$",
       title="c  Archived b9 supports: diagnostic errors remain",ylim=(1e-13,1e-1))
ax.legend(loc="lower left",frameon=True,framealpha=.95,ncol=1,fontsize=8.5)
ax.text(.99,.02,"d=0 omitted\nb9_n64: no P246 output",
        transform=ax.transAxes,ha="right",va="bottom",fontsize=8.5)
ax.grid(alpha=.2,which="major")

ax=axes[1,1]
for identity,label,color in (("dyadic_uniform_P4","P24, leading p=2",colors['P24']),
    ("dyadic_uniform_P6","P246, leading p=3",colors['P246']),
    ("dyadic_uniform_P6_quartic","P246 after cubic removal, p=4",colors['quartic'])):
    r=sorted((a for a in asymptotics if a['id']==identity),key=lambda a:D(a['d']))
    x=np.array([float(D(a['d'])) for a in r]);power=r[0]['leading_power']
    measured=np.array([float(abs(D(a['measured_coefficient'])*D(a['d'])**power)) for a in r])
    predicted=np.array([float(abs(D(a['exact_stored_coefficient'])*D(a['d'])**power)) for a in r])
    ax.loglog(x,predicted,color=color,ls='--',alpha=.65,lw=1)
    ax.loglog(x,measured,color=color,lw=1.8,marker='o',ms=5,label=label)
    direct_label = ("P24: p=2" if power==2 else ("P246: p=3" if power==3 else "Cubic removed\np=4"))
    ax.text(x[-1]*1.06,measured[-1],direct_label,color=color,va="center",fontsize=8.5)
ax.set(xlabel=r"Positive strain $d$",ylabel=r"Residual $|E_p(d)|$ after lower terms are removed",
       title="d  Local powers: 2, 3 and 4")
ax.set_xticks([.00025,.0005,.001],[r"$2.5\times10^{-4}$",r"$5\times10^{-4}$",r"$10^{-3}$"])
ax.set_xlim(.00023,.00165)
ax.xaxis.set_minor_locator(NullLocator())
ax.grid(alpha=.2,which="major")
fig.text(.075,.066,"Stored results only; no solver is run by this figure script. Panel d uses E_p(d) = bias minus all actual rounded-output Taylor terms below order p.",fontsize=9,color="#444444")
fig.text(.075,.043,"Scope: factorized collisionless angular response. These checks do not certify evolving reactive full finite-bin spectral history or native Einstein/shear coupling.",fontsize=9,color="#444444")
for extension in ("png","svg","pdf"):
    fig.savefig(HERE/("S11_P246_RESPONSE."+extension),dpi=180)
plt.close(fig)

stats=[]
for r in projections:
    if r['python']['status'] != 'PROJECTED':continue
    data=curve(r['id']);worst=max(data,key=lambda a:abs(D(a['signed_error'])))
    stats.append({'id':r['id'],'grid_count':len(data),'max_abs_angular_bias':str(abs(D(worst['signed_error']))),
                  'argmax_d':worst['d'],'signed_worst_bias':worst['signed_error'],
                  'rust_exact_max_residual':r['rust_exact_certificate']['max_abs_residual'],
                  'max_cross_implementation_weight_difference':r['cross_weight_max_abs']})
figure_stats={'source_commit':result['source_commit'],'main_run_status':result['status'],
              'dyadic_grid_maxima':maxima,'dyadic_P246_vs_P24_worst_bias_ratio':maxima['P246']['max_abs']/maxima['P24']['max_abs'],
              'grid_errors':stats,'plot_scope':'stored-data postprocessing, no new solver/history execution',
              'data_hashes':{name:hashlib.sha256((RUN/name).read_bytes()).hexdigest() for name in ('RETURN.json','PROJECTIONS.json','ANGULAR_RESPONSES.json','SMALL_STRAIN_CHECKS.json')},
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(HERE/'FIGURE_STATS.json').write_text(json.dumps(figure_stats,indent=2)+'\n')
with (HERE/'ANGULAR_RESPONSE_GRID.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['id','d','A','A_iso','signed_error']);writer.writeheader()
    writer.writerows(r for r in responses if D(r['d']) in grid)
print(json.dumps({'figures':['S11_P246_RESPONSE.png','S11_P246_RESPONSE.svg','S11_P246_RESPONSE.pdf'],
                  'worst_bias_ratio':figure_stats['dyadic_P246_vs_P24_worst_bias_ratio'],'grid_rows':588}))
