"""Parent PR164 original source crosscheck, run from BASS PR167.
No source rewrite or checkpoint mutation. Parent Git blob immutable.
"""
import hashlib,importlib.util,unittest,pathlib,sys
import numpy as np
from kinetic_equilibrium import FD96Equilibrium

ROOT=pathlib.Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'rei_einstein_tangent_20261016/kinetic_tangent.py'
SHA='1cab2bf7eab5a306ab207206ca3a0fc793dc9163'

class ParentAgreement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=ORIGINAL.read_bytes()
        got=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()
        assert got==SHA,(got,SHA)
        spec=importlib.util.spec_from_file_location('PR164_LOCKED',ORIGINAL)
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        cls.model=mod

    def test_real_parent_moments_parity(self):
        for m in (3.,30.,300.):
            source=self.model.MassiveFD96(m)
            core=FD96Equilibrium(m)
            for x in (0.,.6,1.35):
                for b,A in ((-.08,-1.),(0.,0.),(.05,.4),(.13,2.)):
                    lhs=core.stress(x,b,A)
                    rhs=source.moments(x,b,A)
                    np.testing.assert_allclose(
                        [lhs.rho,lhs.pbar,lhs.delta,lhs.chi_b,lhs.delta_A],
                        [rhs.rho,rhs.pbar,rhs.delta,rhs.chi,rhs.delta_A],
                        rtol=7e-13,atol=4e-14)

    def test_parent_susceptibility_sign(self):
        for m in (3.,30.,300.):
            source=self.model.MassiveFD96(m)
            core=FD96Equilibrium(m)
            for A in (-1.,-.3,.3,2.):
                b=core.equilibrium(.8,A).b_star
                self.assertLess(source.moments(.8,b,A).chi,0.)

if __name__=='__main__':unittest.main()
