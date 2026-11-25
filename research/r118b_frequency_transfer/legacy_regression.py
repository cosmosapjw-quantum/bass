"""Re-run R118-A spectral output and verify the default projected CLI."""
import json,pathlib,subprocess,sys,os,hashlib
exe=pathlib.Path(sys.argv[1]).resolve();src=pathlib.Path(sys.argv[2]).resolve();dense=pathlib.Path(sys.argv[3]).resolve();out=pathlib.Path(sys.argv[4]).resolve();out.mkdir(exist_ok=False)
env=dict(os.environ,RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
r=json.loads((src/'RESULTS.json').read_text());d=json.loads((dense/'RESULTS.json').read_text());result={}
for name in ('he_I','thermal_stronger_L12'):
 c=next(x for x in r['cases'] if x['case']==name)
 cmd=list(c['command']);cmd[0]=str(exe);p=out/name;cmd[cmd.index('--out')+1]=str(p)
 subprocess.run(cmd,env=env,check=True,capture_output=True)
 files=['modes.tsv','cl.tsv','los_modes.tsv','los_cl.tsv','diagnostics.tsv','lie_constants.tsv','thermochemistry.tsv','coupled_stages.tsv','spectral_history.tsv','spectral_normal.tsv','spectral_observer.tsv','spectral_modes.tsv']
 parity={n:(p/n).read_bytes()==(src/name/n).read_bytes() for n in files if (src/name/n).is_file()}
 assert all(parity.values());result[name]=dict(command=cmd,byte_equal=parity)
c=next(x for x in d['cases'] if x['case']=='dense_projected_sdirk2')
cmd=list(c['command']);cmd[0]=str(exe);p=out/'default_projected';cmd[cmd.index('--out')+1]=str(p);i=cmd.index('--frequency-collision');del cmd[i:i+2]
subprocess.run(cmd,env=env,check=True,capture_output=True)
parity={f:(p/f).read_bytes()==(dense/c['case']/f).read_bytes() for f in ['frequency_history.tsv','frequency_rays.tsv','frequency_cells.tsv']}
assert all(parity.values());result['default_projected']=dict(command=cmd,byte_equal=parity)
(out/'REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v['byte_equal'] for k,v in result.items()})
