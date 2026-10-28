"""Alternate-method verification: no imports of the production enclosure code.

Decimal180 is a numerical corroboration. Fraction corner and residual inequalities
are exact comparisons of the saved interval box. They are not a second author.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
from itertools import product
import hashlib,json
U=Path(__file__).resolve().parents[1]
checks=[]
def check(name,passed):checks.append({'name':name,'pass':bool(passed)})
def interval(x):return F(int(x['lo']),1<<x['bits']),F(int(x['hi']),1<<x['bits'])
def fp(x):return F(int(x['numerator']),int(x['denominator']))
def inside(I,x):return I[0]<=x<=I[1]

def point(src):
    c=src['clock'];co=src['cosmology'];maps=src['maps'];inc=src['incoming']
    cv=lambda k:D.from_float(float(co[k]))
    h=D(c['h']);u=D(src['cut']['u']);eta=D(c['eta0'])+u
    NH=D(c['NH_reference']);g=D(c['g0'])+(D(c['g1'])-D(c['g0']))*u/h
    theta=D(src['cut']['t_s'])/D(src['duration'])
    omr=cv('photon_omega_prefactor')*cv('T0_K')**4*(1+cv('neutrino_factor')*cv('Nnueff'))
    H=cv('H_prefactor_s_inv')*(cv('omh2')*(-3*eta).exp()+cv('odeh2')+omr*(-4*eta).exp()).sqrt()
    ra=cv('LYA_FACT_cm3_inv')*D(10**6)*H*(3*u).exp()/(NH*g)
    j=src['source_segment'];a=(inc['source_indices'][j]-5126)*h+D(c['lag'])
    dep=[D.from_float(float.fromhex(s)) for s in inc['departure_hex']]
    f=dep[j]+(dep[j+1]-dep[j])*(u-a)/h+(-D(c['A'])*u.exp()).exp()
    M=[[D(maps['M0'][i][j])+theta*D(maps['delta_M'][i][j]) for j in range(2)] for i in range(2)]
    M[1][1]+=ra
    b=[D(maps['b0'][i][0])+theta*D(maps['delta_b'][i][0]) for i in range(2)];b[1]+=3*ra*g*f
    # Elimination, not the production Cramer formula.
    factor=M[1][0]/M[0][0]
    y=(b[1]-factor*b[0])/(M[1][1]-factor*M[0][1]);x=(b[0]-M[0][1]*y)/M[0][0]
    return [x,y],M,b

def main():
    source_bytes=(U/'inputs/SOURCE_SLICE.json').read_bytes();src=json.loads(source_bytes)
    out=json.loads((U/'evidence/PRIMARY.json').read_text())
    check('source_identity',hashlib.sha256(source_bytes).hexdigest()==out['source_slice_sha256'])
    with localcontext() as ctx:
        ctx.prec=180
        qd,Md,bd=point(src)
    qref=list(map(F,qd));corner_records=[]
    for row in out['rows']:
        p=row['precision_bits'];box=[interval(x) for r in row['M'] for x in r]+[interval(x) for x in row['b']]
        qs=[interval(x) for x in row['q_interval']];qh=[fp(x) for x in row['q_hat']]
        for i in range(2):check(f'Decimal180_P{p}_q{i}',inside(qs[i],qref[i]))
        for i in range(4):check(f'Decimal180_P{p}_matrix{i}',inside(box[i],F(Md[i//2][i%2])))
        for i in range(2):check(f'Decimal180_P{p}_source{i}',inside(box[4+i],F(bd[i])))
        residual_ranges=[interval(v) for v in row['residual']];worst_r=F(0);worst_q=F(0);detmin=None
        for idx,values in enumerate(product(*box)):
            a,m01,m10,d,b0,b1=values
            det=a*d-m01*m10;detmin=det if detmin is None else min(detmin,det)
            factor=m10/a;q1=(b1-factor*b0)/(d-factor*m01);q0=(b0-m01*q1)/a
            r=[b0-a*qh[0]-m01*qh[1],b1-m10*qh[0]-d*qh[1]]
            check(f'P{p}_corner{idx}',det>0 and inside(qs[0],q0) and inside(qs[1],q1)
                  and inside(residual_ranges[0],r[0]) and inside(residual_ranges[1],r[1]))
            worst_r=max(worst_r,sum(map(abs,r)));worst_q=max(worst_q,abs(q0-qh[0])+abs(q1-qh[1]))
        gamma=fp(row['gamma_cut_lower']);res=fp(row['E_residual']);rad=fp(row['E_QSS_new'])
        check(f'P{p}_exact_corner_radius',worst_q<=rad)
        check(f'P{p}_exact_residual_radius',worst_r/gamma<=res)
        check(f'P{p}_rounded_representative_radius',all(inside(qs[i],qh[i]) for i in range(2)))
        corner_records.append({'bits':p,'corners':64,'determinant_min_positive':detmin>0,'max_corner_error_exact':str(worst_q),'max_corner_residual_exact':str(worst_r)})
    # Numeric constant semantics are explicitly checked, not silently decimalized.
    check('binary64_not_decimal_point13',F.from_float(src['cosmology']['omh2'])!=F('0.13'))
    result={'checks':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks),'corners_total':192,
            'reference_q_180digits':[str(x) for x in qd],'corner_records':corner_records,
            'independence':'alternate implementation and arithmetic in same author context; NOT distinct-author review',
            'imports_production':False,'native_ODEs':0,'old_campaign_replays':0}
    (U/'evidence/REFERENCE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'total':result['total'],'exact_corners':192,'independence':result['independence']}))
    if not all(x['pass'] for x in checks):raise AssertionError('independent-method failure preserved')
if __name__=='__main__':main()
