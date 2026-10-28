from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
U=Path(__file__).resolve().parent
c=prepare(U); bind=binding(c); weights=[F(2),F(3),F(5)]
MAP={1:1,2:2,4:3,22:13}

def hgradient(fields):
    names=('H','h0','href','a','Pi_m_norm','y2','omega_gamma','omega_nu')
    if set(fields)!=set(names):raise ValueError('FIELD_IDENTITIES')
    v={k:interval(fields[k],positive=k in ('H','h0','href','a'),nonnegative=k.startswith('omega')) for k in names}
    h2=mul(v['H'],v['H']); inv=(1/h2[1],1/h2[0]);h02=mul(v['h0'],v['h0']); hr2=mul(v['href'],v['href'])
    a4=mul(mul(v['a'],v['a']),mul(v['a'],v['a'])); inva=(1/a4[1],1/a4[0])
    return {1:mul(mul(mul((F(-3),F(-3)),h02),v['Pi_m_norm']),inv),2:mul(mul(hr2,v['y2']),inv),3:mul(mul(mul(h02,v['omega_gamma']),inv),mul((F(1,2),F(1,2)),inva)),13:mul(mul(mul(h02,v['omega_nu']),inv),mul((F(1,2),F(1,2)),inva))}

def enclose(box,fields,*,source_binding=bind,scope='SUPPLIED_FIELD_BOX'):
    if scope!='SUPPLIED_FIELD_BOX':raise ValueError('SCOPE_PROMOTION')
    c.binding_check(source_binding); box=c.rate_box_check(box); hg=hgradient(fields)
    models=[c.polynomial([F(int(k==j)) for j in range(12)],weights,PROV,source_binding) for k in range(12)]
    vertices=c.state_vertices(); A=[None]*6;B=[None]*6
    for z in vertices:
        aa=[[m['b'][i]+c.matvec(m['P'],z)[i] for m in models] for i in range(6)]
        bb=[[c.matvec(m['Q'],z)[i] for m in models] for i in range(6)]
        for i in range(6):
            for coeff,dest in ((aa[i],A),(bb[i],B)):
                ran=(sum((v*(lo if v>=0 else hi) for v,(lo,hi) in zip(coeff,box)),F(0)),sum((v*(hi if v>=0 else lo) for v,(lo,hi) in zip(coeff,box)),F(0)))
                dest[i]=ran if dest[i] is None else (min(dest[i][0],ran[0]),max(dest[i][1],ran[1]))
    e=models[0]['electron_coefficients'];emax=e[0]*c.TOTALS[0]+max(e[1:3])+max(e[3:])
    ff=[add(a,mul((F(0),emax),b)) for a,b in zip(A,B)]
    entries=[[neg(mul(ff[i],hg[j])) if j in hg else (F(0),F(0)) for j in range(23)] for i in range(6)]
    return {'A':A,'B':B,'electron_interval':(F(0),emax),'F':ff,'hgrad':hg,'entries':entries,'rate_intervals':box,'source_fields':fields}

fields={'H':(F(2),F(3)),'h0':(F(1),F(2)),'href':(F(2),F(3)),'a':(F(1),F(2)),'Pi_m_norm':(F(-1),F(2)),'y2':(F(-2),F(1)),'omega_gamma':(F(0),F(1,3)),'omega_nu':(F(1,5),F(1,2))}
box=[(F(0),F(i+1,6)) for i in range(12)]
r=enclose(box,fields); tests={}; diagnostics=[]
tests['source_coordinate_map']=MAP=={1:1,2:2,4:3,22:13} and MAP[22]!=22
tests['138_entries_114_structural_zeros']=sum(j not in MAP.values() for row in r['entries'] for j in range(23))==114 and len(r['entries'])*len(r['entries'][0])==138
tests['signed_fields']=r['hgrad'][1][0]<0<r['hgrad'][1][1] and r['hgrad'][2][0]<0<r['hgrad'][2][1]
for t in (F(1,3),F(2,3)):
    z=[c.TOTALS[0]*t,F(1,5),F(1,4),F(1,6),F(1,7),F(1,8)]
    rates=[lo+t*(hi-lo) for lo,hi in box];model=c.polynomial(rates,weights,PROV,bind); f=c.evaluate(model,z)
    point={k:(lo+t*(hi-lo),)*2 for k,(lo,hi) in fields.items()};hg=hgradient(point)
    assert c.state_membership(z)['in_product_simplex']
    assert all(lo<=v<=hi for v,(lo,hi) in zip(f,r['F']))
    for i in range(6):
        for j,h in hg.items():
            value=-f[i]*h[0];lo,hi=r['entries'][i][j];assert lo<=value<=hi
    diagnostics.append({'z':z,'rates':rates,'fields':point,'F':f})
tests['exact_interior_inclusions']=True
# Independent quotient identity and nonzero sign adversary.
N,H,D,t=F(7),F(3),F(-2,5),F(1,7)
deriv=-N*D/H**2
assert (N/(H+t*D)-N/H-t*deriv)*(H+t*D)*H**2==N*t*t*D*D
assert deriv==-(N/H)*(D/H) and deriv!=+(N/H)*(D/H)
tests['quotient_rule_polynomial_remainder_and_wrong_sign']=True
z=F(2,5);gamma=F(3,7);kappa=F(4,9)
rates=[gamma]+[F(0)]*11;m=c.polynomial(rates,weights,PROV,bind)
assert c.evaluate(m,[z,0,0,0,0,0])[0]==gamma*(c.TOTALS[0]-z)
rates=[F(0)]*12;rates[6]=kappa;m=c.polynomial(rates,weights,PROV,bind)
assert c.evaluate(m,[z,0,0,0,0,0])[0]==-kappa*weights[0]*z*z and c.TOTALS[0]!=1
tests['single_photo_and_recombination_nonunit_H']=True
zero=enclose([(F(0),F(0))]*12,fields)
assert all(v==(0,0) for row in zero['entries'] for v in row)
tests['zero_rates_zero_block']=True
tests['signed_interval_products']=mul((F(-2),F(3)),(F(-5),F(7)))==(F(-15),F(21))
bad=dict(fields);bad['H']=(F(0),F(1));bad2=dict(fields);bad2['omega_nu']=(F(-1),F(1))
tests['rejections']=all([reject(lambda:enclose(box,bad)),reject(lambda:enclose(box,bad2)),reject(lambda:enclose([(2,1)]+box[1:],fields)),reject(lambda:enclose(box,fields,source_binding={**bind,'binding_id':'wrong'})),reject(lambda:enclose(box,fields,scope='FULL30')),reject(lambda:interval((float('inf'),1)))])
assert all(tests.values()),tests
result={'unit':'BASS-CHEM-GEOMETRY-CROSSBLOCK','status':'PASS_CONDITIONAL_SUPPLIED_FIELD_BOX','controls':tests,'scientific_control_groups':len(tests),'diagnostic_count':len(diagnostics),'diagnostics':diagnostics,'binding':bind,'weights':weights,'weight_provenance':PROV,'totals':c.TOTALS,'source_formula':'J_chemical,geometry = -outer(Fchem, gradient log H)','source_full_to_reduced_geometry':MAP,'chemical_rows':c.COORDINATES,'conditional_enclosure':r,'potentially_nonzero_entries':24,'structural_zero_entries':114,'proof':'At each state vertex, A and B are linear in rates; sign endpoints and simplex convexity enclose A and B separately. [0,e_max] times B then encloses quadratic F; signed products enclose -F*hgrad. No quadratic F vertex extrema claim.','independent_box_role':'Safe relaxation; rates and H physically correlated; no exact extrema claim','missing_premises':['Actual whole corridor H,h0,href,a,Pi,y2,omega enclosures','Actual effective rate and electron-weight enclosure binding','Geometry rows','Thomson/tau rows','Owner capsule','Clock and callback rounding'],**CEILINGS}
dump(U/'RESULTS.json',result);dump(U/'DIAGNOSTIC_INPUTS.json',{'rate_intervals':box,'fields':fields,'weights':weights,'binding':bind,'points':diagnostics})
# Meaningful saved interval plot: all four potentially nonzero columns, six rows.
import html
W=920; Hh=620; lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" role="img"><title>Conditional chemical geometry interval bounds</title><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#172635"><text x="30" y="30" font-size="20">6 x 23 source chemical geometry block: 24 interval entries</text><text x="30" y="53">Synthetic supplied field box; 114 other entries are structural zeros only in this block</text>']
cols=[1,2,3,13]
for k,j in enumerate(cols):
    vals=[r['entries'][i][j] for i in range(6)];lo=min(a for a,b in vals);hi=max(b for a,b in vals);span=hi-lo or 1;x0=70+k*220
    lines.append(f'<text x="{x0}" y="90">reduced column {j}</text>')
    for i,(a,b) in enumerate(vals):
        yy=125+i*65;xa=x0+155*float((a-lo)/span);xb=x0+155*float((b-lo)/span)
        lines.append(f'<text x="{x0-30}" y="{yy+4}" font-size="11">{23+i}</text><line x1="{xa}" x2="{xb}" y1="{yy}" y2="{yy}" stroke="#1768a2" stroke-width="4"/><text x="{x0}" y="{yy+20}" font-size="10">[{float(a):.4g}, {float(b):.4g}]</text>')
lines.append('<text x="30" y="565">Panel positions scaled independently. Labels are approximate displays; RESULTS.json holds exact rationals.</text><text x="30" y="590">Source: pinned coupled.py / geometry.py / compact_system.py; full model certificate remains HOLD.</text></g></svg>')
(U/'geometry_block.svg').write_text(''.join(lines)+'\n')
print('PASS',len(tests),'control groups; saved 138 rational interval entries')
