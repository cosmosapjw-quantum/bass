"""Source-derived optical-depth row, exact rational conditional box.

No owner/native module imports. Reconstructed only from pinned source snapshots.
K = owner THOMSON is supplied, never silently replaced by c*sigma_T.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
import json, math, hashlib

P=Path(__file__).resolve().parents[1]
SOURCE_HASH={'coupled.py':'09a3325c584b895f8c1de44d3b64a458ec7e27f8eec843c7e15aa246a6088d47',
'compact_system.py':'3ebf56b5a8f1f392681365ec0769364329f293f944a0de4a5add441c8cbc1c49',
'atomic_network.py':'baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80',
'geometry.py':'b998b83f83da581cf51d08a734b34ecade5215f90ca1e72df43ce129c0fb38a0',
'atomic_model.json':'9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614',
'chemical_polynomial.py':'ff4b00b35305872f02aff88892e5b7567b5492ca14ef3feaa5e443c30e540b16'}
GEO_FULL=(1,2,4,22)
GEO_COMPACT=(1,2,3,13)
CHARGED=tuple(range(23,29))
TAU_ROW=29
N_COLUMNS=30
SIMPLEX_TOTALS=(Q((1<<53)-1,1<<53),Q(1),Q(1))
SOURCE_BINDING='8cb268e8de741e284cf494013f1e0748d27f03c5e77ba0c64413ae92af082d16'


def exact(v)->Q:
    if isinstance(v,(float,bool)) or v is None:
        raise ValueError('exact rational string or integer required, no float/bool')
    try:return Q(v)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as exc:
        raise ValueError('malformed rational') from exc


@dataclass(frozen=True)
class Interval:
    lo:Q
    hi:Q
    def __post_init__(self):
        object.__setattr__(self,'lo',exact(self.lo))
        object.__setattr__(self,'hi',exact(self.hi))
        if self.lo>self.hi:raise ValueError('interval reversal')
    def __add__(self,o):
        o=interval(o);return Interval(self.lo+o.lo,self.hi+o.hi)
    def __neg__(self):return Interval(-self.hi,-self.lo)
    def __sub__(self,o):return self+(-interval(o))
    def __mul__(self,o):
        o=interval(o);p=[a*b for a in (self.lo,self.hi) for b in (o.lo,o.hi)];return Interval(min(p),max(p))
    def __truediv__(self,o):
        o=interval(o)
        if o.lo<=0<=o.hi:raise ValueError('division interval contains zero')
        return self*Interval(1/o.hi,1/o.lo)
    def __pow__(self,n):
        if not isinstance(n,int) or n<0:raise ValueError('positive integer power only')
        if n==0:return Interval(1,1)
        if n%2==0 and self.lo<=0<=self.hi:return Interval(0,max(abs(self.lo),abs(self.hi))**n)
        p=[self.lo**n,self.hi**n];return Interval(min(p),max(p))
    def includes(self,v):v=exact(v);return self.lo<=v<=self.hi
    def as_json(self):return [str(self.lo),str(self.hi)]


def interval(x):
    if isinstance(x,Interval):return x
    if isinstance(x,(tuple,list)):
        if len(x)!=2:raise ValueError('expected interval pair')
        return Interval(*x)
    return Interval(x,x)


def verify_source()->dict:
    got={}
    for file,expected in SOURCE_HASH.items():
        b=(P/'input'/file).read_bytes();h=hashlib.sha256(b).hexdigest()
        if h!=expected:raise ValueError('PINNED_SOURCE_MISMATCH:'+file)
        got[file]={'sha256':h,'bytes':len(b)}
    coupled=(P/'input/coupled.py').read_text()
    for line in ("out[61]=THOMSON*ne/field['H']","jac[61,:40]=-THOMSON*ne/h*hgrad","jac[61,40:61]=THOMSON/h*negrad","negrad=nb*self.atomic.q*self.scale"):
        if line not in coupled:raise ValueError('OWNER_TAU_SOURCE_CHANGED:'+line)
    compact=(P/'input/compact_system.py').read_text()
    for line in ('GEOMETRY = np.array([0, 1, 2]', 'ATOMIC = np.array([1,2,10,11,12,17,18,19,20])','SELECT = np.r_[GEOMETRY,40+ATOMIC,61]'):
        if line not in compact:raise ValueError('COMPACT_LIFT_SOURCE_CHANGED')
    return got


def source_weights():
    """Replicate actual owner normalization and float divisions before binary64 exactification."""
    verify_source()
    r=json.loads((P/'input/atomic_model.json').read_text())['inventory_number_ratios_to_H1']
    masses=dict(n=1,H1=1,D=2,T=3,He3=3,He4=4,Li6=6,Li7=7)
    norm=math.fsum(masses[name]*r[name] for name in ('n','H1','D','T','He3','He4','Li6','Li7'))
    # Actual model owner scalar scale is ratio / math.fsum. This operation is binary64.
    numbers={name:Q.from_float(r[name]/norm) for name in masses}
    wH=numbers['H1']+numbers['D']
    wHe=numbers['He3']+numbers['He4']
    wLi=numbers['Li6']+numbers['Li7']
    return dict(w=[wH,wHe,wLi],e=[wH,wHe,2*wHe,wLi,2*wLi,3*wLi],individual=numbers,
                normalization_binary64_repr=repr(norm),semantics='source binary64 owner inventory then exact represented real')


def membership(z,totals=SIMPLEX_TOTALS):
    z=[exact(x) for x in z]
    if len(z)!=6:raise ValueError('SIX_CHARGED_COORDINATES_REQUIRED')
    t=[exact(x) for x in totals]
    if len(t)!=3 or tuple(t)!=SIMPLEX_TOTALS:raise ValueError('SOURCE_FIXED_TOTALS_CHANGED')
    for block,total in zip(((0,),(1,2),(3,4,5)),t):
        if any(z[i]<0 for i in block) or sum((z[i] for i in block),Q(0))>total:
            raise ValueError('STATE_OUTSIDE_REDUCED_SIMPLEX')
    return z


def hgrad(fields):
    F={k:interval(fields[k]) for k in ('H','h0','href','a','Pi_m_norm','y2','omega_gamma','omega_nu')}
    if F['H'].lo<=0 or F['h0'].lo<=0 or F['href'].lo<=0 or F['a'].lo<=0 or F['omega_gamma'].lo<0 or F['omega_nu'].lo<0:
        raise ValueError('POSITIVE_H_H0_HREF_A_AND_NONNEGATIVE_OMEGA_REQUIRED')
    D=F['H']**2
    return {1:interval(-3)*F['h0']**2*F['Pi_m_norm']/D,
            2:F['href']**2*F['y2']/D,
            3:F['h0']**2*F['omega_gamma']/(interval(2)*D*F['a']**4),
           13:F['h0']**2*F['omega_nu']/(interval(2)*D*F['a']**4)}


def row_at_point(*,z,fields,nb,K,binding=SOURCE_BINDING):
    if binding!=SOURCE_BINDING:raise ValueError('SOURCE_BINDING_MISMATCH')
    z=membership(z);F={name:exact(value) for name,value in fields.items()}
    gg=hgrad(F);nb,K=exact(nb),exact(K)
    if nb<0 or K<0:raise ValueError('NONNEGATIVE_NB_AND_THOMSON')
    e=source_weights()['e'];H=F['H'];alpha=K*nb/H
    electron=sum((ei*zi for ei,zi in zip(e,z)),Q(0))
    out=[Q(0)]*N_COLUMNS
    for j in GEO_COMPACT:out[j]=-(alpha*electron)*gg[j].lo
    for j,ej in zip(CHARGED,e):out[j]=alpha*ej
    return dict(row=out,tau_rhs=alpha*electron,electron_over_nb=electron,
                structurally_nonzero_columns=sorted((*GEO_COMPACT,*CHARGED)),
                actual_THOMSON_source_constant_bound=False)


def row_box(*,fields,nb,K,weights_source=None,binding=SOURCE_BINDING):
    if binding!=SOURCE_BINDING:raise ValueError('SOURCE_BINDING_MISMATCH')
    nebox=interval(nb);kbox=interval(K)
    if nebox.lo<0 or kbox.lo<0:raise ValueError('NONNEGATIVE_NB_AND_THOMSON')
    gf=hgrad(fields);H=interval(fields['H']);e=source_weights()['e'];t=SIMPLEX_TOTALS
    density_max=e[0]*t[0]+max(e[1:3])*t[1]+max(e[3:])*t[2]
    alph=kbox*nebox/H
    electron=Interval(0,density_max)
    r=alph*electron
    row=[Interval(0,0) for _ in range(N_COLUMNS)]
    for j in GEO_COMPACT:row[j]= -r*gf[j]
    for j,ej in zip(CHARGED,e):row[j]=alph*interval(ej)
    nonzero=sorted((*GEO_COMPACT,*CHARGED))
    return dict(row=row,interval_rhs=r,nonzero=nonzero,zero=[j for j in range(N_COLUMNS) if j not in nonzero],
                source_weight_e=e,source_weight_w=source_weights()['w'],
                classification='CONDITIONAL_SYNTHETIC_SUPPLIED_FIELD_BOX',
                owner_THOMSON_prefactor_bound=False,actual_whole_corridor=False,full30_provider=False,
                has_physical_u33=False,physical_error_budget=None)
