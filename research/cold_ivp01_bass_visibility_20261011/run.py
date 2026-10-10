import hashlib,json,math,subprocess,time
from pathlib import Path
from decimal import Decimal,localcontext

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
EV=OUT/'evidence'; EV.mkdir(exist_ok=True)
C=json.loads((OUT/'CONTRACT.json').read_text())
P=Path(C['producer'])/'research/cold_conditional_ivp01_20261011'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x): (EV/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
for n,h in C['producer_hashes'].items():
 p=P/n if n=='CONTRACT.json' else P/'evidence'/n
 assert sha(p)==h,(n,sha(p),h)
for n,h in C['base_hashes'].items():
 b=subprocess.check_output(['git','show',C['base']+':'+n],cwd=ROOT)
 assert hashlib.sha256(b).hexdigest()==h,n
source={n:sha(ROOT/n) for n in ['_rustcore/src/microphysics/visibility.rs','_rustcore/examples/rei_cold_ivp01_finite_visibility.rs','_rustcore/Cargo.toml','_rustcore/Cargo.lock']}
save('SOURCE_PRELAUNCH.json',{'source_hashes':source,'contract_sha256':sha(OUT/'CONTRACT.json'),'base':C['base'],'tree':C['base_tree'],'harness':'HARNESS_UNAVAILABLE','runtime_requested':'lower-tier coding','runtime_observed':'not independently observed'})
def command(name,args,limit,input=None):
 start=time.time()
 r=subprocess.run(args,cwd=ROOT,input=input,text=True,capture_output=True,timeout=limit)
 (EV/(name+'.stdout.log')).write_text(r.stdout); (EV/(name+'.stderr.log')).write_text(r.stderr)
 save(name+'.receipt.json',{'command':args,'limit_seconds':limit,'elapsed_seconds':time.time()-start,'exit_code':r.returncode})
 assert r.returncode==0,(name,r.returncode)
 return r
command('build',['cargo','build','--offline','--locked','--manifest-path','_rustcore/Cargo.toml','--example','rei_cold_ivp01_finite_visibility'],600)
BIN=ROOT/'_rustcore/target/debug/examples/rei_cold_ivp01_finite_visibility'
save('BINARY_PRELAUNCH.json',{'binary':str(BIN),'sha256':sha(BIN),'sources':source})
command('targeted_test',['cargo','test','--offline','--locked','--manifest-path','_rustcore/Cargo.toml','--example','rei_cold_ivp01_finite_visibility'],120)
eps=2**-52
raw=[]; checks=[]; start=time.time()
def check(name,v,limit):
 checks.append({'name':name,'value':v,'limit':limit,'pass':v<=limit}); assert v<=limit,(name,v,limit)
def rel(a,b): return abs(a-b)/abs(b) if b else abs(a-b)
def invoke(name,edges,ys,tail=0.,reject=False):
 assert time.time()-start<60
 inp=str(tail)+'\n'+' '.join(map(repr,edges))+'\n'+'\n'.join(' '.join(map(repr,y)) for y in ys)+'\n'
 r=subprocess.run([str(BIN)],input=inp,text=True,capture_output=True,timeout=max(.1,60-(time.time()-start)))
 raw.append({'name':name,'input':inp,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 if reject: assert r.returncode!=0,name; return
 assert r.returncode==0,(name,r.stderr)
 o={line.split()[0]:list(map(float,line.split()[1:])) for line in r.stdout.splitlines()}
 with localcontext() as ctx:
  ctx.prec=80; D=Decimal.from_float
  ne=[D(float(y[2]+y[3]))*D(float(y[3]/(y[2]+y[3]))) for y in ys]
  q=[x*D(299792458.)*D(6.6524587e-29) for x in ne]
  qb=[(a+b)/2 for a,b in zip(q,q[1:])]
  tau=[D(float(tail))]*(len(edges)); l1=[Decimal(0)]*len(edges)
  for i in range(len(qb)-1,-1,-1):
   dt=D(float(edges[i+1]))-D(float(edges[i])); tau[i]=tau[i+1]+qb[i]*dt
   # compare_opacity consumes actual binary qbar and its actual doubled values.
   l1[i]=l1[i+1]+abs(D(o['qbar'][i])-D(float(2*o['qbar'][i])))*dt
  survival=[(-x).exp() for x in tau]; mass=[survival[i+1]-survival[i] for i in range(len(qb))]
  for key,ref,factor,absolute in [('q',q,64,False),('qbar',qb,64,False),('tau',tau,128,False),('survival',survival,64,True),('mass',mass,256,False)]:
   for i,(a,b) in enumerate(zip(o[key],ref)): check(f'{name}:{key}:{i}',abs(a-float(b)) if absolute else rel(a,float(b)),factor*eps)
  sb=[1-(-x).exp() for x in l1]; mb=[sb[i]+sb[i+1] for i in range(len(qb))]
  for key,ref in [('l1',l1),('survival_bound',sb),('mass_bound',mb)]:
   for i,(a,b) in enumerate(zip(o[key],ref)): check(f'{name}:{key}:{i}',rel(a,float(b)),64*eps)
  check(name+':conservation',abs(o['survival'][0]+sum(o['mass'])-math.exp(-tail)),64*eps)
 return o
try:
 data=json.loads((P/'evidence/RESULTS.json').read_text()); dec=json.loads((P/'evidence/DECIMAL80_REFERENCE.json').read_text())
 edges=[0.,2.5e13,5e13,7.5e13,1e14]; native=data['native']; results={}; comparisons=[]
 for ident in range(4):
  rows={r['n']:r for r in native if r['id']==ident and r['control']=='physical'}
  ys=rows[32]['epochs']; results[str(ident)]=invoke(f'id{ident}:n32',edges,ys)
  for n in [8,16]:
   o=invoke(f'id{ident}:n{n}',edges,rows[n]['epochs']); comparisons.append({'id':ident,'n':n,'depth_delta_from_n32':o['tau'][0]-results[str(ident)]['tau'][0]})
  o=invoke(f'id{ident}:3edge',edges[::2],ys[::2]); comparisons.append({'id':ident,'schedule':'3edge','depth_delta_from_5edge':o['tau'][0]-results[str(ident)]['tau'][0]})
  for i,y in enumerate(ys): check(f'producer_decimal:{ident}:{i}:ne',rel(y[3],dec['epochs'][ident][i][3]),1e-10)
 ys=next(r['epochs'] for r in native if r['id']==0 and r['n']==32 and r['control']=='physical')
 def transform(fn):
  z=[y[:] for y in ys]
  for y in z: fn(y)
  return z
 zero=transform(lambda y:y.__setitem__(3,0.)); z=invoke('zero',edges,zero); assert all(x==0 for x in z['q']+z['tau']+z['mass']) and all(x==1 for x in z['survival'])
 const=[ys[0][:] for _ in ys]; o=invoke('constant',edges,const)
 check('constant_analytic',rel(o['tau'][0],o['q'][0]*(edges[-1]-edges[0])),128*eps)
 double=transform(lambda y:(y.__setitem__(2,y[2]*2),y.__setitem__(3,y[3]*2),y.__setitem__(11,y[11]*2)))
 d=invoke('density_x2',edges,double)
 for i,q in enumerate(d['q']): check(f'density_x2:{i}',rel(q,2*results['0']['q'][i]),64*eps)
 a=invoke('a_only',edges,transform(lambda y:y.__setitem__(0,y[0]*2))); assert a==results['0']
 t=invoke('tail_0.25',edges,ys,.25)
 for i,s in enumerate(t['survival']): check(f'tail_scale:{i}',abs(s-results['0']['survival'][i]*math.exp(-.25)),64*eps)
 invoke('irregular',[0.,1e12,3e13,8e13,1e14],ys)
 invoke('length_mismatch',edges,ys[:-1],reject=True)
 for name,grid in [('duplicate',[0.,0.,5e13,7.5e13,1e14]),('reversed',[0.,3e13,2e13,7.5e13,1e14]),('nonfinite',[0.,float('nan'),5e13,7.5e13,1e14])]: invoke(name,grid,ys,reject=True)
 for tail in [-1.,float('nan'),float('inf')]: invoke('invalid_tail_'+str(tail),edges,ys,tail,reject=True)
 save('RESULTS.json',results); save('COMPARISONS.json',comparisons)
 save('VALIDATION.json',{'status':'PASS','checks':checks,'claim_ceiling':C['claim_ceiling'],'comparisons_are_diagnostics_only':True})
finally:
 save('CAMPAIGN_RAW.json',raw); save('CAMPAIGN_RECEIPT.json',{'elapsed_seconds':time.time()-start,'limit_seconds':60,'launches':1,'solver_launches':0,'binary_sha256':sha(BIN)})
