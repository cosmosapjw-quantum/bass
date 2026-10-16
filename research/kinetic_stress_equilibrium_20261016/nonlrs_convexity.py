"""Manufactured positive reflection-even diagonal source, not FD96 continuum."""
import numpy as np
from scipy.optimize import minimize

q=np.eye(3)
w=np.array([1.2,.8,1.0])
m=3.0
B=np.array([[1.,0.],[0.,1.],[-1.,-1.]])

def energy(beta):
    kinetic=q*q*np.exp(-2*np.asarray(beta))[None,:]
    return float(w@np.sqrt(m*m+kinetic.sum(axis=1)))

def pressure_hessian(beta):
    kinetic=q*q*np.exp(-2*np.asarray(beta))[None,:]
    E=np.sqrt(m*m+kinetic.sum(axis=1))
    P=np.sum(w[:,None]*kinetic/E[:,None],axis=0)
    H=np.zeros((3,3))
    for j in range(len(q)):
        H+=w[j]*(np.diag(2*kinetic[j]/E[j])-np.outer(kinetic[j],kinetic[j])/E[j]**3)
    return P,H

def beta2(u):
    return np.array([u[0],u[1],-u[0]-u[1]])

def main():
    rng=np.random.default_rng(24);lowest=float('inf')
    for _ in range(300):
        beta=rng.uniform(-1,1,3);p,h=pressure_hessian(beta)
        vals=np.linalg.eigvalsh(B.T@h@B)
        lowest=min(lowest,float(vals.min()))
        assert vals.min()>0
        for i in range(3):
            v=np.zeros(3);v[i]=2e-5
            estimate=(energy(beta+v)-energy(beta-v))/(4e-5)
            assert abs(estimate+p[i])<1e-9
    sol=minimize(lambda u:energy(beta2(u)),[0.,0.],method='BFGS',tol=1e-12)
    root=beta2(sol.x)
    P,_=pressure_hessian(root)
    assert np.max(np.abs(B.T@P))<3e-8
    print({'lowest_constrained_hessian_eigen':lowest,
           'root_beta':root.tolist(),'root_energy':energy(root),
           'isotropic_coordinate_energy':energy(np.zeros(3))})

if __name__=='__main__':main()
