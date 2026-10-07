"""Independent Decimal-70 validation of the actual BASS/REI native bridge."""
from decimal import Decimal as D, getcontext
from pathlib import Path
import argparse, hashlib, itertools, json, subprocess, time
getcontext().prec=70
C=D('299792458'); SIGMA=D('6.6524587e-29'); SCALE=D('1e6'); TOL=D('2e-12')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    commands=[];cases=[]
    densities=[('1e-4','8.3e-6'),('.01','.003'),('0','1e-5'),('.001','0')]
    fractions=[('0','0','0'),('1','0','0'),('.2','.3','.4'),('1','0','1')]
    rays=[(['0','0','0'],['1','0','0']),(['.6','0','0'],['1','0','0']),(['.6','0','0'],['-1','0','0']),(['.6','0','0'],['0','1','0'])]
    for kind,nh,f,ray in itertools.product(['HHE','FT03'],densities,fractions,rays):
        b,e=ray;tokens=['snapshot',kind,*nh,*f,'1e-12','0','0','0','0',*b,*e];commands.append(' '.join(tokens));cases.append((nh,f,b,e))
    invalid=[]
    base=['snapshot','HHE','1e-4','8.3e-6','.2','.3','.4','1e-12','0','0','0','0','0','0','0','1','0','0']
    changes=[{2:'-1'},{2:'NaN'},{2:'0',3:'0'},{4:'1.1'},{5:'.8',6:'.4'},{7:'-1'},{8:'-1'},{11:'-1'},{12:'1'},{15:'0'},{2:'1e303'},{4:'0',5:'0',6:'0',15:'0'}]
    for mods in changes:
        t=base.copy()
        for k,v in mods.items():t[k]=v
        invalid.append(' '.join(t))
    commands+=invalid
    run=subprocess.run([a.native],input='\n'.join(commands)+'\n',capture_output=True,text=True,timeout=30)
    lines=run.stdout.splitlines(); checks=0;failures=[];maxima={};records=[]
    def truth(v,name,case):
        nonlocal checks
        checks+=1
        if not v:failures.append(dict(check=name,case=case))
    def close(got,want,scale,name,case):
        got=D(str(got));want=D(str(want));scale=abs(D(str(scale)));err=abs(got-want)/scale if scale else (D(0) if got==want else D('Infinity'))
        maxima[name]=max(maxima.get(name,D(0)),err);truth(err<=TOL,name,case)
    truth(run.returncode==0,'native exit0','batch');truth(len(lines)==len(commands),'line count','batch')
    for i,(nh,f,b,e) in enumerate(cases):
        z=json.loads(lines[i],parse_float=D);truth(z.get('ok') is True,'valid snapshot accepted',i)
        if not z.get('ok'):continue
        nh,nhe=map(D,nh);x,y,w=map(D,f);b=list(map(D,b));e=list(map(D,e));ne=nh*x+nhe*(y+2*w);gamma=1/(1-sum(v*v for v in b)).sqrt();dop=gamma*(1-sum(v*u for v,u in zip(b,e)));q=ne*SCALE*C*SIGMA*dop
        for key,want in [('ne_source_cm3',ne),('ne_m3',ne*SCALE),('doppler',dop),('q_s_inverse',q)]:close(z[key],want,want,key,i)
        truth(z['physical_admission'] is False,'physical claim ceiling',i);records.append(json.loads(lines[i]))
    for j in range(len(cases),len(commands)):
        z=json.loads(lines[j]);truth(z.get('ok') is False,'invalid snapshot rejected',j)
    # Independent wrong formulas: missing SI density conversion, D squared, atomic 1/gamma, wrong HeIII charge.
    ne=D('1e-4')*D('.2')+D('8.3e-6')*(D('.3')+2*D('.4'));q=ne*SCALE*C*SIGMA*D('.5')
    wrong={'missing_1e6':q/SCALE,'D_twice':q*D('.5'),'atomic_clock':q*D('.8')/D('.5'),'HeIII_charge1':(D('1e-4')*D('.2')+D('8.3e-6')*(D('.3')+D('.4')))*SCALE*C*SIGMA*D('.5')}
    for name,v in wrong.items():truth(abs(v-q)/q>TOL,'negative control '+name,'analytic')
    result=dict(schema_version='1.0',experiment_id='BASS-REI-E2',status='PASS' if not failures else 'FAIL',checks=checks,native_calls=len(commands),valid_snapshot_points=len(cases),invalid_snapshot_points=len(invalid),precision_digits=70,tolerance=str(TOL),max_scaled_errors={k:str(v) for k,v in maxima.items()},failures=failures,native_binary_sha256=hashlib.sha256(Path(a.native).read_bytes()).hexdigest(),oracle_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='actual source snapshot validation and charge/unit/ray-rate composition, not FT03 temperature admission or finite-T Thomson validity',timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    (out/'INDEPENDENT_BRIDGE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(out/'INDEPENDENT_BRIDGE_CASES.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if not failures else 1)
if __name__=='__main__':main()
