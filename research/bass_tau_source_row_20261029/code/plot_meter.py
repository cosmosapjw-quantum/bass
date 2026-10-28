"""Separate capped plot only; no scientific recomputation."""
from pathlib import Path
import subprocess,resource,time,os,sys,json
P=Path(__file__).resolve().parents[1]
def lim():
 resource.setrlimit(resource.RLIMIT_CPU,(8,9))
 resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
def main():
 cmd=[sys.executable,'-I',str(P/'code/plot_saved.py')]
 t=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
 try:
  c=subprocess.run(cmd,capture_output=True,text=True,timeout=25,preexec_fn=lim,env=dict(os.environ,MPLBACKEND='Agg',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
  code=c.returncode;out=c.stdout;err=c.stderr;timeout=False
 except subprocess.TimeoutExpired as e:
  code=124;timeout=True;out=str(e.stdout or '');err=str(e.stderr or '')
 after=resource.getrusage(resource.RUSAGE_CHILDREN);cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime);wall=time.monotonic()-t
 (P/'evidence/PLOT.stdout').write_text(out);(P/'evidence/PLOT.stderr').write_text(err)
 receipt={'exit':code,'timeout':timeout,'child_cpu_s':cpu,'child_wall_s':wall,'cpu_cap':8,'wall_cap':25,'plot_only':True,'science_reexecution':False}
 (P/'evidence/PLOT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt));print(out[-900:]);
 if code!=0:print(err[-1200:],file=sys.stderr);raise SystemExit(code)
if __name__=='__main__':main()
