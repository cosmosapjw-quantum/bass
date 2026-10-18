"""Source-only positive time quadrature; not reactive chemistry order claims."""
import math
import unittest
from source_oracle import Case
from deposition import gauss2_cases,simulate,continuum_reference
class GaussBirthTests(unittest.TestCase):
    def setUp(self):
        self.geometry=lambda x:(.03*math.sin(x),1e-16*math.exp(-1.5*x),.03*math.cos(x)*1e-16*math.exp(-1.5*x))
        self.c=Case('GL2',.2,0.,1e-16,0.,1.,qmin=1.,nmu=32,nseg=8,nenergy=64)
    def test_two_positive_births_per_panel(self):
        q=gauss2_cases(self.c,self.geometry,.2,.8,4)
        self.assertEqual(len(q),8,'GL2 must use both birth times, not call the midpoint path')
        self.assertTrue(all(v.dt>0 for v in q))
        self.assertTrue(all(a.x<b.x for a,b in zip(q,q[1:])))
    def test_fourth_order_source_energy_not_chemistry(self):
        x0,x1=.2,.8
        reference=continuum_reference(self.c,self.geometry,x0,x1)
        errors=[]
        for n in (4,8,16):
            births=gauss2_cases(self.c,self.geometry,x0,x1,n)
            r=simulate(births,x1,self.geometry(x1)[0])
            errors.append(abs(r['inventory_u']-reference['inventory_u']))
            self.assertLess(abs(r['energy_residual'])/r['ledger_u'],2e-14)
        self.assertGreater(errors[0]/errors[1],14.)
        self.assertGreater(errors[1]/errors[2],14.)
    def test_no_hidden_extra_volume_on_weights(self):
        q=gauss2_cases(self.c,self.geometry,.2,.8,4)
        for c in q:self.assertAlmostEqual(c.dt*self.geometry(c.x)[1],(.8-.2)/8,places=14)
if __name__=='__main__':unittest.main(verbosity=2)
