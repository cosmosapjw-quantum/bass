"""Verify pre-R118-C frequency output exactly on two earlier paths."""
import json,pathlib,subprocess,os,sys
exe,src,out=map(pathlib.Path,sys.argv[1:4]);out.mkdir(exist_ok=False)
r=json.loads((src/'RESULTS.json').read_text());env=dict(os.environ,RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
result={}
for name in ('cold_f128','projected_r117_he_I','early_host_line'):
 c=next(q for q in r['cases'] if q['case']==name)
 cmd=list(c['command']);cmd[0]=str(exe.resolve());dest=out/name;cmd[cmd.index('--out')+1]=str(dest)
 subprocess.run(cmd,env=env,capture_output=True,check=True)
 files=['modes.tsv','cl.tsv','los_modes.tsv','los_cl.tsv','diagnostics.tsv','lie_constants.tsv','thermochemistry.tsv','coupled_stages.tsv','frequency_history.tsv','frequency_cells.tsv','frequency_rays.tsv','frequency_line_velocity.tsv','spectral_history.tsv','spectral_normal.tsv','spectral_observer.tsv']
 parity={f:(dest/f).read_bytes()==(src/name/f).read_bytes() for f in files if (src/name/f).exists()}
 assert all(parity.values())
 result[name]=parity;print(name,parity)
(out/'REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n')
