import sys,numpy as np
from pathlib import Path
f=Path(sys.argv[1]);x=np.genfromtxt(f,names=True,delimiter=',');m=(x['epoch']==1)&(x['ell']==3);v=np.linalg.norm(x['Bre'][m]+1j*x['Bim'][m])
print('zero B3 floor',v);assert v<1e-22
