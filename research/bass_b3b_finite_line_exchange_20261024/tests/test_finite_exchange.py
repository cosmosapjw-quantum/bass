"""Small discriminating synthetic fixtures; real unchanged owners/receivers."""
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction
import itertools
import math
from pathlib import Path
import sys
import unittest
import warnings
import numpy as np
from scipy.integrate import quad

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
import finite_exchange as fx
from finite_exchange import owner, core, kinetic

METRICS = {}


def make_line(x=.3, f=0., N=1e9, H=1e-18, S=None):
    card = owner.CARDS['H_LYA_EFFECTIVE_2P']
    return owner.LineState(card.id, card.population_scope, N*(1-x), N*x, H, f,
        owner.shear_fixtures()['rotated'] if S is None else S,
        'SYNTHETIC_FROZEN_FINITE_LINE_FIXTURE')


def duration(line, omega):
    F = 1 + (line.card.g+1)*line.f_plus
    k = 8*math.pi*line.H_s_inv/(line.N*line.card.wavelength_m**3)
    return omega / (k*F*F/line.card.g)


def positive_original_rate_integrals(line, ledger):
    """Independent quadrature of original down/up rate times dt/dv.

    Neither the a/r formula nor gross antiderivative is used in this oracle.
    """
    g, f, N = line.card.g, line.f_plus, line.N
    F = 1+(g+1)*f
    xe = g*f/F
    k = 8*math.pi*line.H_s_inv/(N*line.card.wavelength_m**3)
    def integrand(v, channel):
        x = xe + (line.x-xe)*math.exp(-v)
        # Absorption-start x must not be cancelled by xe + (-xe)*exp(-v).
        if line.x == 0:
            x = xe * (-math.expm1(-v))
        d = g-(g+1)*x
        original = N*k*((1+f)*x if channel == 0 else g*f*(1-x))/d
        dt_dv = d/(k*F)
        return original * dt_dv
    return [quad(lambda v: integrand(v,c), 0, ledger['v'], epsabs=1e-25,
                 epsrel=3e-13, limit=80)[0] for c in (0,1)]


def transaction_fixture(line=None, occupied=False, L=1e25, Pstar=1e-26):
    line = line or make_line()
    scale = core.FixedScale(L)
    identity = fx.Identity('REC_LINE01_DETACHED', line.card_id, line.population_scope,
                           'synthetic-stock-epoch-0', scale, Pstar)
    population = fx.PopulationStock(identity, line.n_u_m3, line.n_l_m3)
    photons = fx.PhotonStock.vacuum(identity)
    if occupied:
        directions, weights = fx.cubature14()
        photons = fx.PhotonStock(identity, directions*.6, weights*.002, np.zeros(14))
    rho, flux, pressure, pi = fx.photon_moments(photons)
    excitation = scale.density_factor*line.card.energy_J*line.n_u_m3
    h = line.H_s_inv*L/scale.c
    state = core.State(h, h*line.S, np.diag([.003,.004,.005]),
                       np.zeros(3), .12, np.array([excitation+.003, rho, .007]),
                       np.array([[0.,0.,0.], flux, [.0001,0.,0.]]))
    source = core.Source(np.array([.0002, pressure, .0007]),
                         np.array([core.stf([.00001,-.00002,0.,0.,0.]), pi,
                                   core.stf([.00003,.00002,0.,0.,0.])]))
    return dict(line=line, source_identity=identity, state_identity=identity,
                state=state, source=source, population=population, photons=photons,
                scale=scale, Pstar=Pstar, dt_s=duration(line,.7), transfer_id='physical-0')


class GrossTests(unittest.TestCase):
    def test_positive_original_rate_quadrature(self):
        rows=[]
        f=.1; xe=3*f/(1+4*f)
        for name,x,f,omega in [('emission',.4,0.,.8),('absorption_start',0.,.1,.5),
                ('near_LTE',xe+1e-12,.1,.6),('LTE',xe,.1,.6),
                ('absorption',.05,.1,.8),('tiny_absorption',0.,.1,1e-12)]:
            line=make_line(x,f)
            ledger=fx.gross_counts(line,duration(line,omega))
            oracle=positive_original_rate_integrals(line,ledger)
            errs=[]
            for key,ref in zip(('down_m3','up_m3'),oracle):
                if ref:
                    error=abs(ledger[key]-ref)/ref
                    self.assertLess(error,3e-12)
                else:
                    error=abs(ledger[key]-ref);self.assertEqual(error,0)
                errs.append(error)
            self.assertLess(abs(ledger['gross_difference_residual_over_gross']),1e-14)
            rows.append(dict(case=name,down=ledger['down_m3'],up=ledger['up_m3'],
                             net=ledger['net_m3'],oracle=oracle,relative_errors=errs))
        METRICS['positive_original_rate_quadrature']=rows

    def test_LTE_clock_and_gross(self):
        f=.125; xe=3*f/(1+4*f);line=make_line(xe,f)
        dt=duration(line,.9);out=fx.gross_counts(line,dt)
        self.assertEqual(out['owner_map']['u'],0.)
        self.assertAlmostEqual(out['v'],.9)
        expected=line.N*out['k_line_s_inv']*f*(1+f)*dt
        self.assertLess(abs(out['down_m3']/expected-1),5e-16)
        self.assertLess(abs(out['up_m3']/expected-1),5e-16)
        self.assertEqual(out['net_m3'],0.)

    def test_tiny_r_Decimal_cancellation_oracle(self):
        rows=[]
        with localcontext() as context:
            context.prec=110
            for v in (1e-4,1e-12,1e-40,1e-100):
                dv=Decimal.from_float(v)
                reference=dv-1+(-dv).exp()
                # At v=1e-100 this cancellation requires >200 digits.
                if v<1e-50:
                    context.prec=250;reference=dv-1+(-dv).exp()
                a,r,bound,terms=fx.a_and_r(v)
                error=float(abs(Decimal.from_float(r)-reference)/reference)
                self.assertLess(error,5e-16)
                rows.append(dict(v=v,r=r,relative_error=error,next_term_bound=bound,terms=terms))
        METRICS['Decimal_r_oracle']=rows

    def test_absorption_start_retains_quadratic_down(self):
        line=make_line(0.,.1)
        first=fx.gross_counts(line,duration(line,1e-12))
        second=fx.gross_counts(line,duration(line,2e-12))
        self.assertGreater(first['down_m3'],0.)
        self.assertAlmostEqual(second['down_m3']/first['down_m3'],4.,places=10)

    def test_zero_and_empty_and_donor(self):
        for x,dtfactor in [(.3,0.),(0.,2.),(.3,1e4)]:
            line=make_line(x)
            out=fx.gross_counts(line,duration(line,dtfactor))
            self.assertEqual(out['up_m3'],0.)
            self.assertGreaterEqual(out['down_m3'],0.)
            self.assertLessEqual(out['down_m3'],line.n_u_m3)
            self.assertEqual(out['net_m3'],out['down_m3'])
            if x==0 or dtfactor==0:self.assertEqual(out['down_m3'],0.)

    def test_full_two_half_map_and_counts(self):
        rows=[]
        for x,f in [(.4,0.),(.05,.1),(3*.1/1.4,.1)]:
            line=make_line(x,f);dt=duration(line,.9)
            full=fx.gross_counts(line,dt)
            half1=fx.gross_counts(line,dt/2)
            x1=half1['owner_map']['x1']
            nextline=replace(line,n_u_m3=line.N*x1,n_l_m3=line.N*(1-x1))
            half2=fx.gross_counts(nextline,dt/2)
            self.assertLess(abs(full['owner_map']['x1']-half2['owner_map']['x1']),1e-15)
            residuals={}
            for key in ('down_m3','up_m3','net_m3'):
                scale=max(abs(full[key]),1.)
                err=abs(full[key]-half1[key]-half2[key])/scale
                self.assertLess(err,4e-15);residuals[key]=err
            rows.append(dict(x=x,f=f,count_residuals=residuals))
        METRICS['semigroup']=rows

    def test_owner_domain_guards(self):
        for updates in (dict(n_u_m3=9e8,n_l_m3=1e8),dict(S=np.diag([-1.,.5,.5])),
                        dict(owner_mode='native'),dict(native_line_owner_active=True),
                        dict(population_scope='whole_n2')):
            with self.subTest(updates=updates),self.assertRaises(ValueError):
                replace(make_line(),**updates)
        with self.assertRaises(ValueError):
            fx.gross_counts(make_line(H=1e9),1.)
        with self.assertRaises(ValueError):fx.gross_counts(make_line(),-1.)


class AngularTests(unittest.TestCase):
    def test_exact_rational_degree_five(self):
        """Use sign parity and rational even powers; no irrational arithmetic."""
        nodes=[]
        for i in range(3):
            for sign in (-1,1):
                row=[0,0,0];row[i]=sign;nodes.append((row,Fraction(1,15),False))
        nodes += [(row,Fraction(3,40),True) for row in itertools.product((-1,1),repeat=3)]
        checked=0
        for total in range(6):
            for exponents in itertools.product(range(total+1),repeat=3):
                if sum(exponents)!=total:continue
                if any(e%2 for e in exponents):
                    # Pairing one sign shows exact zero, including odd degree.
                    numerator=sum(w*math.prod(s**e for s,e in zip(n,exponents))
                                  for n,w,corner in nodes)
                    self.assertEqual(numerator,0);checked+=1;continue
                actual=sum(w*math.prod(Fraction(s)**e for s,e in zip(n,exponents))
                           /(3**(total//2) if corner else 1) for n,w,corner in nodes)
                expected=Fraction(1)
                for e in exponents:
                    expected *= math.prod(range(1,e,2))
                expected /= math.prod(range(1,total+2,2))
                self.assertEqual(actual,expected);checked+=1
        METRICS['exact_rational_monomials_through_degree5']=checked

    def test_rotated_STF_and_packet_moments(self):
        directions,A=fx.cubature14()
        S=owner.shear_fixtures()['rotated']
        q=1+np.einsum('ni,ij,nj->n',directions,S,directions)
        weights=A*q
        self.assertTrue(np.all(weights>0))
        # Fourteen terms, q dot products, and sqrt(3) normalization: a modest
        # floating arithmetic bound; the preceding rational oracle is exact.
        floating_tolerance=32*np.finfo(float).eps
        np.testing.assert_allclose(weights.sum(),1.,rtol=0,atol=floating_tolerance)
        np.testing.assert_allclose(weights@directions,0,rtol=0,atol=floating_tolerance)
        actual=np.einsum('n,ni,nj->ij',weights,directions,directions)
        expected=np.eye(3)/3+2*S/15
        np.testing.assert_allclose(actual,expected,rtol=0,atol=floating_tolerance)
        METRICS['rotated_angular_tensor_max_residual']=float(np.max(abs(actual-expected)))


class TransactionTests(unittest.TestCase):
    def test_large_finite_depletion_preserves_owner_endpoint(self):
        kwargs=transaction_fixture()
        kwargs['dt_s']=duration(kwargs['line'],50.)
        alpha_E=kwargs['scale'].density_factor*kwargs['line'].card.energy_J
        kwargs['state'].rho[0]=alpha_E*kwargs['population'].n_u_m3
        before=kwargs['state'].pack().copy()
        ledger=fx.gross_counts(kwargs['line'],kwargs['dt_s'])
        expected_upper=kwargs['line'].N*ledger['owner_map']['x1']
        expected_excitation=alpha_E*expected_upper
        self.assertGreater(expected_upper,0.)
        self.assertGreater(expected_excitation,0.)
        # This is the independently demonstrated cancellation case.
        self.assertEqual(kwargs['population'].n_u_m3-ledger['net_m3'],0.)
        out=fx.commit_emission(**kwargs)
        self.assertEqual(out['population'].n_u_m3,expected_upper)
        self.assertEqual(out['state'].rho[0],expected_excitation)
        self.assertLessEqual(abs(out['line'].x/ledger['owner_map']['x1']-1),2*np.finfo(float).eps)
        self.assertLessEqual(out['residuals']['owner_endpoint_relative'],2*np.finfo(float).eps)
        self.assertLess(abs(out['residuals']['total_energy_over_gross']),fx.ROUND_FACTOR)
        np.testing.assert_array_equal(kwargs['state'].pack(),before)
        METRICS['large_finite_depletion_omega50']=dict(owner_x1=ledger['owner_map']['x1'],
            expected_upper_m3=expected_upper,committed_upper_m3=out['population'].n_u_m3,
            expected_excitation=expected_excitation,committed_atomic_rho=out['state'].rho[0],
            residuals=out['residuals'])
        # A finite positive remainder must also be rejected when the owner's
        # endpoint itself underflows, or cannot coexist with constant energy.
        kwargs=transaction_fixture();kwargs['dt_s']=duration(kwargs['line'],1000.)
        with self.assertRaisesRegex(ArithmeticError,'endpoint underflowed'):
            fx.commit_emission(**kwargs)
        kwargs=transaction_fixture();kwargs['dt_s']=duration(kwargs['line'],50.)
        with self.assertRaisesRegex(ArithmeticError,'endpoint sector excitation unrepresentable'):
            fx.commit_emission(**kwargs)

    def test_finite_real_state_and_source_admission(self):
        checked=[]
        for target,field in [('state','h'),('state','alpha'),('state','sigma'),
                ('state','n'),('state','a'),('state','rho'),('state','flux'),
                ('source','pressure'),('source','pi'),('source','energy_transfer'),
                ('source','momentum_transfer')]:
            kwargs=transaction_fixture()
            obj=kwargs[target]
            value=getattr(obj,field)
            if value is None:
                value=np.zeros(3 if field=='energy_transfer' else (3,3))
            if np.ndim(value)==0:
                setattr(obj,field,complex(value,.01))
            else:
                value=np.asarray(value,dtype=complex).copy()
                value.flat[0]+=.01j
                setattr(obj,field,value)
            before_state=kwargs['state'].pack().copy()
            before_source=[np.array(getattr(kwargs['source'],label),copy=True)
                if getattr(kwargs['source'],label) is not None else None
                for label in ('pressure','pi','energy_transfer','momentum_transfer')]
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                with self.subTest(target=target,field=field),self.assertRaises(ValueError):
                    fx.commit_emission(**kwargs)
            self.assertEqual(caught,[])
            np.testing.assert_array_equal(kwargs['state'].pack(),before_state)
            for label,previous in zip(('pressure','pi','energy_transfer','momentum_transfer'),before_source):
                if previous is None:self.assertIsNone(getattr(kwargs['source'],label))
                else:np.testing.assert_array_equal(getattr(kwargs['source'],label),previous)
            checked.append(target+'.'+field)
        METRICS['finite_real_rejections_without_warnings']=checked

    def test_actual_core_kinetic_vacuum_occupied(self):
        rows=[]
        for occupied in (False,True):
            kwargs=transaction_fixture(occupied=occupied)
            before=kwargs['state'].pack().copy();oldp=kwargs['source'].pressure.copy()
            out=fx.commit_emission(**kwargs)
            np.testing.assert_array_equal(kwargs['state'].pack(),before)
            np.testing.assert_array_equal(kwargs['source'].pressure,oldp)
            self.assertEqual(len(out['photons'].w),14+(14 if occupied else 0))
            self.assertTrue(np.all(out['photons'].w>0))
            self.assertLess(out['population'].n_u_m3,kwargs['population'].n_u_m3)
            np.testing.assert_array_equal(out['state'].n,kwargs['state'].n)
            np.testing.assert_array_equal(out['state'].sigma,kwargs['state'].sigma)
            np.testing.assert_array_equal(out['state'].a,kwargs['state'].a)
            self.assertEqual(out['state'].h,kwargs['state'].h)
            self.assertEqual(out['state'].alpha,kwargs['state'].alpha)
            self.assertEqual(out['state'].rho[2],kwargs['state'].rho[2])
            np.testing.assert_array_equal(out['state'].flux,kwargs['state'].flux)
            self.assertEqual(out['source'].pressure[0],kwargs['source'].pressure[0])
            np.testing.assert_array_equal(out['source'].pi[0],kwargs['source'].pi[0])
            self.assertEqual(out['source'].pressure[2],kwargs['source'].pressure[2])
            np.testing.assert_array_equal(out['source'].pi[2],kwargs['source'].pi[2])
            p,pi,U,J=out['source'].arrays(3)
            self.assertTrue(np.all(U==0));self.assertTrue(np.all(J==0))
            self.assertEqual(out['pi_kind'],'STATE_STRESS_NOT_PIRATE')
            self.assertLess(abs(out['residuals']['total_energy_over_gross']),fx.ROUND_FACTOR)
            self.assertLess(abs(out['residuals']['constraint_change_over_gross']),fx.ROUND_FACTOR)
            rows.append(dict(occupied=occupied,residuals=out['residuals'],tolerances=out['tolerance'],
                constraints_before=out['constraints_before'].tolist(),
                constraints_after=out['constraints_after'].tolist(),
                donor_before=kwargs['population'].n_u_m3,donor_after=out['population'].n_u_m3,
                photon_increase=out['ledger']['net_m3']))
        METRICS['actual_finite_transaction']=rows

    def test_zero_update_true_vacuum(self):
        for kwargs in (transaction_fixture(),transaction_fixture(make_line(0.))):
            kwargs['dt_s']=0.
            out=fx.commit_emission(**kwargs)
            self.assertEqual(len(out['photons'].w),0)
            np.testing.assert_array_equal(out['state'].pack(),kwargs['state'].pack())
            self.assertEqual(out['population'].n_u_m3,kwargs['population'].n_u_m3)

    def test_scale_L2_rate_L3_and_Pstar(self):
        first=transaction_fixture();second=transaction_fixture(L=2e25,Pstar=3e-26)
        a=fx.commit_emission(**first);b=fx.commit_emission(**second)
        drho1=a['state'].rho[1]-first['state'].rho[1]
        drho2=b['state'].rho[1]-second['state'].rho[1]
        self.assertAlmostEqual(drho2/drho1,4.,places=14)
        E=first['line'].card.energy_J;D=a['ledger']['net_m3'];dt=first['dt_s']
        scale=first['scale'];kappa=8*math.pi*scale.G/scale.c**4
        average_rate=kappa*scale.length_m**3/scale.c*E*D/dt
        integrated=average_rate*(scale.c*dt/scale.length_m)
        self.assertLess(abs(integrated/drho1-1),5e-16)
        c=transaction_fixture(Pstar=3e-26);out=fx.commit_emission(**c)
        self.assertLess(abs(out['state'].rho[1]/a['state'].rho[1]-1),5e-16)
        METRICS['scale_conversion']=dict(finite_L2_ratio=drho2/drho1,
            rate_L3_ratio=8.,integrated_rate_relative_error=abs(integrated/drho1-1))

    def test_duplicate_physical_key_ignores_representation(self):
        kwargs=transaction_fixture();out=fx.commit_emission(**kwargs)
        for k in ('line','state','source','population','photons'):kwargs[k]=out[k]
        changed=replace(kwargs['source_identity'],representation='another_display')
        kwargs['source_identity']=changed;kwargs['state_identity']=changed
        kwargs['population']=replace(kwargs['population'],identity=changed)
        kwargs['photons']=replace(kwargs['photons'],identity=changed)
        with self.assertRaisesRegex(ValueError,'already charged'):fx.commit_emission(**kwargs)

    def test_identity_and_geometry_failures_leave_inputs(self):
        cases=[]
        for field,value in [('owner','WRONG_OWNER'),('card_id','H_LYA_J1HALF'),
                ('population_scope','other_scope'),('epoch','stale_epoch'),
                ('frame','boosted'),('clock','observer_dt'),('Pstar',2e-26),
                ('scale',core.FixedScale(2e25))]:
            cases.append(('state_identity',field,value))
        for target,field,value in cases:
            kwargs=transaction_fixture();before=kwargs['state'].pack().copy()
            kwargs[target]=replace(kwargs[target],**{field:value})
            with self.subTest(field=field),self.assertRaises(ValueError):fx.commit_emission(**kwargs)
            np.testing.assert_array_equal(kwargs['state'].pack(),before)
        for target,field,value in [('source_identity','frame','boosted'),
                                   ('source_identity','clock','observer_dt'),
                                   ('population','n_u_m3',.5)]:
            kwargs=transaction_fixture();kwargs[target]=replace(kwargs[target],**{field:value})
            with self.assertRaises(ValueError):fx.commit_emission(**kwargs)
        for field in ('h','sigma'):
            kwargs=transaction_fixture();setattr(kwargs['state'],field,getattr(kwargs['state'],field)*1.1)
            with self.assertRaises(ValueError):fx.commit_emission(**kwargs)

    def test_photon_consistency_energy_and_f_commit_guards(self):
        for kind in ('photon_rho','photon_flux','photon_p','photon_pi','insufficient_energy','incoming_transfer'):
            kwargs=transaction_fixture(occupied=True)
            if kind=='photon_rho':kwargs['state'].rho[1]*=1.01
            elif kind=='photon_flux':kwargs['state'].flux[1,0]+=.001
            elif kind=='photon_p':kwargs['source'].pressure[1]*=1.01
            elif kind=='photon_pi':kwargs['source'].pi[1]=core.stf([.001,-.001,0.,0.,0.])
            elif kind=='insufficient_energy':kwargs['state'].rho[0]=0.
            else:kwargs['source'].energy_transfer=np.array([.001,-.001,0.])
            before=kwargs['state'].pack().copy()
            with self.subTest(kind=kind),self.assertRaises(ValueError):fx.commit_emission(**kwargs)
            np.testing.assert_array_equal(kwargs['state'].pack(),before)
        kwargs=transaction_fixture(make_line(.3,.1));before=kwargs['state'].pack().copy()
        self.assertGreater(fx.gross_counts(kwargs['line'],kwargs['dt_s'])['up_m3'],0.)
        with self.assertRaisesRegex(ValueError,'prescribed boundary'):fx.commit_emission(**kwargs)
        np.testing.assert_array_equal(kwargs['state'].pack(),before)

    def test_tiny_population_and_sector_advance_reject(self):
        kwargs=transaction_fixture();kwargs['dt_s']=duration(kwargs['line'],1e-20)
        ledger=fx.gross_counts(kwargs['line'],kwargs['dt_s'])
        self.assertNotEqual(ledger['owner_map']['dx'],0.)
        self.assertEqual(ledger['owner_map']['x1'],kwargs['line'].x)
        with self.assertRaisesRegex(ArithmeticError,'unrepresentable'):fx.commit_emission(**kwargs)
        kwargs=transaction_fixture();kwargs['state'].rho[0]=1e100
        with self.assertRaisesRegex(ArithmeticError,'unrepresentable'):
            fx.commit_emission(**kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
