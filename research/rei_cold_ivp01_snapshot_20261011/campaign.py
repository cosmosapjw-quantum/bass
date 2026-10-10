"""One stored-snapshot campaign. Decimal80 algebra only; no reference solver."""
import decimal, hashlib, json, math, pathlib, subprocess, sys
D=decimal.Decimal
decimal.getcontext().prec=80
HERE=pathlib.Path(__file__).resolve().parent
PRODUCER=pathlib.Path('/tmp/rei-cold-conditional-ivp01-20261011')
E=PRODUCER/'research/cold_conditional_ivp01_20261011/evidence'
BIN=HERE/'target/debug/examples/rei_cold_ivp01_snapshot_receiver'
TOL=64*sys.float_info.epsilon
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def select(data):
    found={}
    for item in data['native']:
        if item.get('kind')=='trajectory' and item.get('control')=='physical' and item.get('n')==32:
            i=item['id']
            if i not in range(4) or i in found: raise ValueError('INVALID_OR_DUPLICATE_ID')
            if len(item['epochs'])!=5: raise ValueError('MISSING_OR_DUPLICATE_EPOCH')
            if len({tuple(y) for y in item['epochs']})!=5: raise ValueError('DUPLICATE_EPOCH')
            found[i]=item['epochs']
    if set(found)!=set(range(4)): raise ValueError('MISSING_ID')
    return [(i,j,y) for i in range(4) for j,y in enumerate(found[i])]
def rel(a,b):
    if a==0 or b==0:
        assert a==b, ('EXACT_ZERO',a,b)
        return D(0)
    return abs(a-b)/max(abs(a),abs(b))
def main():
    data=json.loads((E/'RESULTS.json').read_text()); rows=select(data)
    ref=json.loads((E/'DECIMAL80_REFERENCE.json').read_text())['epochs']
    for mode in ['missing_id','duplicate_id','missing_epoch','duplicate_epoch']:
        bad=json.loads(json.dumps(data))
        targets=[x for x in bad['native'] if x.get('kind')=='trajectory' and x.get('control')=='physical' and x.get('n')==32]
        if mode=='missing_id': bad['native'].remove(targets[0])
        if mode=='duplicate_id': bad['native'].append(targets[0])
        if mode=='missing_epoch': targets[0]['epochs'].pop()
        if mode=='duplicate_epoch': targets[0]['epochs'][1]=targets[0]['epochs'][0]
        try: select(bad)
        except ValueError: pass
        else: raise AssertionError(mode)
    text=''.join(' '.join(repr(x) for x in y)+'\n' for _,_,y in rows)
    (HERE/'INPUT_ROWS.txt').write_text(text)
    receipt={'contract':'COLD_IVP01_BASS_SNAPSHOT_RECEIVER01','harness':'HARNESS_UNAVAILABLE','source_sha256':sha(HERE.parent.parent/'_rustcore/examples/rei_cold_ivp01_snapshot_receiver.rs'),'binary_sha256':sha(BIN),'producer_RESULTS_sha256':sha(E/'RESULTS.json'),'rows':20,'history_rows':0,'requested_model':'lower-tier coding agent','observed_model':'NOT_OBSERVED'}
    (HERE/'PRELAUNCH.json').write_text(json.dumps(receipt,indent=2)+'\n')
    run=subprocess.run([str(BIN)],input=text,text=True,capture_output=True,timeout=60)
    (HERE/'CAMPAIGN.stdout.log').write_text(run.stdout); (HERE/'CAMPAIGN.stderr.log').write_text(run.stderr)
    assert run.returncode==0,run.returncode
    values=[[float(x) for x in line.split()] for line in run.stdout.splitlines()]; assert len(values)==20
    outcomes=[]; maxerr=D(0); maxref=D(0)
    c=D.from_float(299792458.0); sigma=D.from_float(6.6524587e-29)
    for (i,j,y),v in zip(rows,values):
        assert len(y)==19 and len(v)==6
        oracle_ne=D.from_float(y[3]); oracle_q=c*sigma*oracle_ne
        errs=[rel(D.from_float(v[k]), oracle_ne if k<2 else oracle_q) for k in range(6)]
        assert max(errs)<=D.from_float(TOL),('BINARY_ORACLE',i,j,errs)
        assert v[2]==v[3] and v[4]==v[5]
        reference_ne=D.from_float(ref[i][j][3]); reference_q=c*sigma*reference_ne
        re=max(rel(oracle_ne,reference_ne),rel(oracle_q,reference_q)); assert re<=D('1e-10')
        maxerr=max(maxerr,max(errs)); maxref=max(maxref,re)
        outcomes.append({'id':i,'epoch_index':j,'tau_seconds':[0,2.5e13,5e13,7.5e13,1e14][j],'a':y[0],'nH_m3':y[2]+y[3],'xHII':y[3]/(y[2]+y[3]),'ne_reference_m3':y[3],'native':v,'Decimal80_q_s_inverse':str(oracle_q),'binary_relative_errors':[str(x) for x in errs],'producer_reference_relative_error':str(re)})
    result={'execution':'PASS','snapshot_rows':20,'history_rows':0,'max_binary_relative_error':str(maxerr),'max_producer_reference_relative_error':str(maxref),'controls':'neutral, double HII, a-only, width, unsupported, missing/duplicate id/epoch','scientific_admission':'PENDING_ASTRA_REVIEW','physical_unconditional_ivp':'HOLD','visibility_history':'NOT_PROVIDED','rows':outcomes}
    (HERE/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__': main()
