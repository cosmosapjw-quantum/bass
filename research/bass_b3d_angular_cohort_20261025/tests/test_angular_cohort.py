"""Focused angular polynomial, physical packet and interface checks only."""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import angular_cohort as ac
ROOT=Path(__file__).resolve().parents[1]

def require(condition,message):
    if not condition:raise AssertionError(message)

def reject(call):
    try:call()
    except ValueError:return
    raise AssertionError('invalid input was accepted')

def odd_factorial(n):return math.prod(range(n,0,-2))

def sphere_monomial(i,j,k):
    if any(v%2 for v in [i,j,k]):return 0.
    return odd_factorial(i-1)*odd_factorial(j-1)*odd_factorial(k-1)/odd_factorial(i+j+k+1)

def main():
    receipts=[]
    for row in json.loads((ROOT/'results/SOURCE_COPIES.json').read_text()):
        require(hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()==row['sha256'],'parent source changed')
        require(hashlib.sha256((ROOT/row['destination']).read_bytes()).hexdigest()==row['sha256'],'copied source changed')
    for name,degree in [('Q14',5),('Q26',7)]:
        n,w=ac.rule(name);require(np.min(w)>0,'positive weights');require(abs(np.sum(w)-1)<=ac.ROUND,'normalized weights')
        maxpoly=0.
        for i in range(degree+1):
            for j in range(degree+1-i):
                for k in range(degree+1-i-j):
                    err=abs(np.dot(w,n[:,0]**i*n[:,1]**j*n[:,2]**k)-sphere_monomial(i,j,k));maxpoly=max(maxpoly,err)
        require(maxpoly<=ac.ROUND,'claimed polynomial exactness')
        if name=='Q14':
            defects=[np.dot(w,n[:,0]**6)-1/7,np.dot(w,n[:,0]**4*n[:,1]**2)-1/35,np.dot(w,np.prod(n*n,axis=1))-1/105]
            require(np.max(np.abs(np.array(defects)-[4/315,-2/315,4/315]))<=ac.ROUND,'degree-six defects')
        for label,S in ac.SOURCES.items():
            birth=ac.moments(S,np.eye(3),n,w)
            residual=max(abs(birth['F']-1),ac.tensor_difference(birth['P'],np.eye(3)/3+2*S/15),max(abs(v) for v in birth['flux']))
            require(residual<=ac.ROUND,'birth identities')
            C=ac.transport(1.);value=ac.moments(S,C,n,w);require(abs(np.trace(value['P'])-value['F'])/value['F']<=ac.ROUND,'trace P=F')
            co=ac.moments(ac.O@S@ac.O.T,ac.O@C@ac.O.T,n@ac.O.T,w)
            O4=np.eye(4);O4[1:,1:]=ac.O
            covariance=ac.tensor_difference(co['T'],O4@np.array(value['T'])@O4.T)/value['F']
            require(covariance<=ac.ROUND,'co-rotating covariance')
            packet=ac.packet_check(S,C,name)
            require(max(v for k,v in packet.items() if k.endswith('error'))<=ac.ROUND,'actual packet mapping')
            require(packet['minimum_weight']>0 and packet['maximum_energy_over_birth']<1,'positive redward packets')
            receipts.append(dict(rule=name,source=label,polynomial_maximum_absolute_error=maxpoly,birth_error=residual,covariance_error=covariance,packet=packet))
    for S,C in [(np.diag([1.,0,0]),np.eye(3)),(np.diag([-1.1,.55,.55]),np.eye(3)),(np.full((3,3),np.nan),np.eye(3)),(np.eye(3,dtype=complex)*1j,np.eye(3)),(np.zeros((3,3)),np.diag([1.,0,1.])),(np.zeros((3,3)),np.full((3,3),np.inf))]:reject(lambda S=S,C=C:ac.validate(S,C))
    iso=ac.moments(np.zeros((3,3)),np.eye(3),*ac.sphere_rule(16))
    require(abs(iso['F']-1)<=ac.ROUND and ac.tensor_difference(iso['P'],np.eye(3)/3)<=ac.ROUND,'isotropic limit')
    out=dict(status='PASS_SCOPED_TESTS',rules=receipts,source_copies_exact=True,rejections=6,new_IVPs=0)
    (ROOT/'results/TEST_RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps(out))

if __name__=='__main__':main()
