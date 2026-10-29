"""CE1-H C8 isolated MPFR residual worker. Not a native subagent."""
import sys,json,hashlib,time
from bianchi.nonperturbative.einstein_tabulated_source import TabulatedRadiation
from bianchi.nonperturbative.einstein_error_budget import rk4_path
from bianchi.nonperturbative.einstein_interval import residual_taylor_mpfr

def sha(a):return hashlib.sha256(a.tobytes()).hexdigest()

def main(panel):
 t=time.perf_counter()
 s=TabulatedRadiation([0,.5,1],[0,.25,.75,1],[[.1,.25,.05],[.2,.15,.15]],refinement=16,backend='python_oracle')
 p=rk4_path(s,s.initial_state(),.08,4,backend='python_oracle')
 d=residual_taylor_mpfr(s,p,panel,subcells=1)
 return {'panel':panel,'defect':d,'elapsed_sec':time.perf_counter()-t,
 'path_sha256':sha(p.states)+':'+sha(p.coefficients)+':'+sha(p.times),
 'source_sha256':sha(s.n)+':'+sha(s.mass)}

if __name__=='__main__':
 assert len(sys.argv)==2
 print(json.dumps(main(int(sys.argv[1]))))
