import json,pathlib,subprocess,os,sys
exe,p,d=map(pathlib.Path,sys.argv[1:]);d.mkdir(exist_ok=False)
r=json.loads((p/'RESULTS.json').read_text());out={}
for name in ('cold_f128','r117_he_I','early_line_f128','redist_t32'):
 c=next(x for x in r['cases'] if x['case']==name)
 cmd=list(c['command']);cmd[0]=str(exe.resolve());new=d/name;old=p/name
 cmd[cmd.index('--out')+1]=str(new)
 subprocess.run(cmd,env=dict(os.environ,RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),check=True,capture_output=True)
 parity={f.name:(new/f.name).read_bytes()==f.read_bytes() for f in old.glob('*.tsv')}
 assert all(parity.values()),(name,parity)
 out[name]=dict(command=cmd,byte_equal=parity)
(d/'REGRESSION.json').write_text(json.dumps(out,indent=2)+'\n')
