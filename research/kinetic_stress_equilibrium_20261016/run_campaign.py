"""Rebuild 45 FD96 neutral roots plus 45 angle refinement cases.
Source-only BASS Python, create-only results, no rei_bianchi/native process.
"""
import argparse,csv,hashlib,json,math,pathlib,sys
from kinetic_equilibrium import FD96Equilibrium,XMAX

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True)
    out=p.parse_args().output
    if out.exists():raise FileExistsError('CREATE_ONLY_OUTPUT_EXISTS')
    out.mkdir(parents=True)
    rows=[]
    for m in (3,30,300):
        f=FD96Equilibrium(m)
        for x in (0.,.7,XMAX):
            for A in (-1.,-.5,0.,.5,2.):
                r=f.equilibrium(x,A)
                rows.append(dict(m=m,x=x,A=A,b_star=r.b_star,db_dA=r.db_dA,db_dx=r.db_dx,
                    chi_b=r.chi_b,rho_min=r.rho_min,delta_residual=r.residual_delta,
                    delta_over_rho=abs(r.residual_delta)/r.rho_min,
                    b_nonrel=r.b_nonrel))
    with (out/'SOURCE_CHART.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    ang=[]
    for m in (3,30,300):
        for A in (-1.,.5,2.):
            for n in (8,16,32,64,128):
                e=FD96Equilibrium(m,n).equilibrium(.7,A)
                ang.append(dict(m=m,A=A,angular_n=n,b_star=e.b_star,residual_delta=e.residual_delta))
    with (out/'ANGULAR_CONVERGENCE.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(ang[0]));w.writeheader();w.writerows(ang)
    receipt={'schema':'bass.vlasov.neutral_stress_chart.v1',
       'mass_cases':3,'source_root_rows':len(rows),'angular_cases':len(ang),
       'all_chi_negative':all(c['chi_b']<0 for c in rows),
       'all_A_response_positive':all(c['db_dA']>0 for c in rows),
       'max_abs_bstar':max(abs(c['b_star']) for c in rows),
       'max_normalized_root_residual':max(c['delta_over_rho'] for c in rows),
       'source_base_PR166':'02149a6830dfe7ed214b77f5309e38350d2659fb'}
    assert len(rows)==45 and len(ang)==45 and receipt['all_chi_negative']
    assert receipt['all_A_response_positive'] and receipt['max_abs_bstar']<1
    (out/'CAMPAIGN.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()
       +'  '+f.name for f in sorted(out.iterdir()))+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
