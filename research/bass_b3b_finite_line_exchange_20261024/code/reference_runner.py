"""Bounded current validation plus one figure from actual computed outputs."""
import csv
import json
from pathlib import Path
import sys
import unittest
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
import test_finite_exchange as tests
from test_finite_exchange import fx


def main():
    suite=unittest.defaultTestLoader.loadTestsFromModule(tests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    summary=dict(test_count=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        status='PASS' if result.wasSuccessful() else 'FAIL',metrics=tests.METRICS,
        source_fixture_classification='SYNTHETIC_FROZEN_PARAMETERS; actual source/cards/core/kinetic',
        independent_code_review='PENDING_SEPARATE_REVIEWER')
    (ROOT/'results/VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
    if not result.wasSuccessful():return 1
    rows=[]
    line=tests.make_line(.4,.1)
    lte=tests.make_line(3*.1/1.4,.1)
    for omega in np.linspace(0,3,49):
        general=fx.gross_counts(line,tests.duration(line,float(omega)))
        equilibrium=fx.gross_counts(lte,tests.duration(lte,float(omega)))
        kwargs=tests.transaction_fixture()
        kwargs['dt_s']=tests.duration(kwargs['line'],float(omega))
        kwargs['transfer_id']=f'figure-independent-{omega:.17g}'
        finite=fx.commit_emission(**kwargs)
        D=finite['ledger']['net_m3'];N=line.N
        rows.append(dict(omega=float(omega),down_over_N=general['down_m3']/N,
            up_over_N=general['up_m3']/N,net_over_N=general['net_m3']/N,
            LTE_down_over_N=equilibrium['down_m3']/N,LTE_up_over_N=equilibrium['up_m3']/N,
            LTE_net_over_N=equilibrium['net_m3']/N,
            finite_upper_over_N=finite['population'].n_u_m3/N,
            finite_emitted_over_N=D/N,
            finite_gamma_rho_increment=float(finite['state'].rho[1]-kwargs['state'].rho[1]),
            finite_atomic_rho_increment=float(finite['state'].rho[0]-kwargs['state'].rho[0]),
            finite_constraint_normalized_residual=finite['residuals']['constraint_change_over_gross']))
    with (ROOT/'results/FIGURE_DATA.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    x=[row['omega'] for row in rows]
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11.4,4.4),layout='constrained')
    ax=axes[0]
    for key,label,color,style in [('down_over_N','Gross down','#2166ac','-'),
            ('up_over_N','Gross up','#b2182b','-'),('net_over_N','Stable net','#238443','-'),
            ('LTE_down_over_N','LTE down = up','#6a51a3','--'),
            ('LTE_net_over_N','LTE net = 0','#555555',':')]:
        ax.plot(x,[row[key] for row in rows],label=label,color=color,linestyle=style,lw=2)
    ax.set(xlabel=r'Frozen source time $\omega=\eta\,\Delta t$ (dimensionless)',
           ylabel=r'Integrated count / $N$ (dimensionless)',title='Prescribed incoming boundary: f = 0.1')
    ax.legend(fontsize=8,loc='upper left');ax.grid(alpha=.2)
    ax=axes[1]
    ax.plot(x,[r['finite_upper_over_N'] for r in rows],label=r'Finite upper population $n_u/N$',color='#2166ac',lw=2)
    ax.plot(x,[r['finite_emitted_over_N'] for r in rows],label=r'Created photons $D_{net}/N$',color='#e08214',lw=2)
    ax.axhline(.3,color='#555555',ls=':',label='Initial donor / N = 0.3')
    ax.set(xlabel=r'Frozen source time $\omega=\eta\,\Delta t$ (dimensionless)',
           ylabel=r'Finite population or photon count / $N$',title='Actual finite transaction: f = 0, initial vacuum')
    ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.suptitle('Frozen thick LINE01 exchange — synthetic frozen parameters, actual source and BASS receiver',fontsize=12)
    fig.savefig(ROOT/'results/FINITE_LINE_EXCHANGE.png',dpi=180)
    fig.savefig(ROOT/'results/FINITE_LINE_EXCHANGE.pdf')
    plt.close(fig)
    summary['figure']=dict(data='results/FIGURE_DATA.csv',rows=len(rows),
        image='results/FINITE_LINE_EXCHANGE.png',pdf='results/FINITE_LINE_EXCHANGE.pdf',
        max_finite_constraint_normalized_residual=max(abs(r['finite_constraint_normalized_residual']) for r in rows),
        claim='One frozen local interval per curve point; no IVP, history calibration or finite f>0 bath.')
    (ROOT/'results/VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',tests=result.testsRun,figure_rows=len(rows)),indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
