import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import numpy as np
import pytest
from restart import compose,rebase,dump_checkpoint,load_checkpoint

def test_affine_reward_composition():
 a=(np.array([[.5,.1],[0,.4]]),np.array([1.,2.]),np.array([[2.,3.]]),np.array([4.]))
 b=(np.array([[.2,0],[.1,.3]]),np.array([3.,1.]),np.array([[5.,7.]]),np.array([6.]))
 c=compose(a,b)
 assert c is not None, 'Missing affine population AND accumulated reward composition'
 p=np.array([2.,4.]); z=np.array([11.])
 pa=a[0]@p+a[1]; za=z+a[2]@p+a[3]
 assert np.allclose(c[0]@p+c[1],b[0]@pa+b[1],rtol=0,atol=1e-14)
 assert np.allclose(z+c[2]@p+c[3],za+b[2]@pa+b[3],rtol=0,atol=1e-14)

def test_binomial_rebase():
 v=rebase(np.array([2.,3.,5.]),.25,.75,0,0)
 assert v is not None, 'Missing global-clock moment rebase'
 assert np.allclose(v,[2.,2.75,4.0625],rtol=0,atol=1e-14)

def state():
 return dict(identity=dict(source='S',frame='FLRW',clock='global',V0='1'),step=7,t=.7,dt=.1,y=[.1,.2,123.456],attempted_work=28,pending=False)

def test_checkpoint_retains_rewards_and_work():
 s=state(); r=load_checkpoint(dump_checkpoint(s),s['identity'])
 assert r is not None, 'Missing retained hidden-state/reward checkpoint'
 assert r==s
 assert [float(x).hex() for x in r['y']]==[float(x).hex() for x in s['y']]

@pytest.mark.parametrize('kind',['source','frame','clock','V0'])
def test_identity_mismatch_refused(kind):
 s=state(); changed=dict(s['identity']);changed[kind]='different'
 with pytest.raises(ValueError):load_checkpoint(dump_checkpoint(s),changed)

def test_pending_transaction_refused():
 s=state();s['pending']=True
 with pytest.raises(ValueError):dump_checkpoint(s)
