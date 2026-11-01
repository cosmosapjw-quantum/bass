"""Original-source physical checks for retarded exactly-one Thomson-scatter S0."""
import csv,gzip,json,math,sys,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from retarded_once import (
    source_histories,incoming_photon_packets,outgoing_characteristic,
    parallel_rotation,post_hi_optical_depth,scatter_contribution,
    gauss_scatter_times,original_linear_grid,sig_hi_vec,
    gauss_birth_direction_grid,screen,C,SIG_T,END,BIRTH_EV,THRESHOLD,HERE,sha
)
from s0_source_photon_thomson import model_epoch,outgoing_gain,sigma_hi

class SourcePhysical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h=source_histories()
        cls.bi=cls.h["S0_BI"]
        cls.fl=cls.h["S0_FLRW"]

    def test_original_HHe_charge_and_source_lock(self):
        self.assertEqual(len(self.bi.ne),16001)
        self.assertEqual(len(self.bi.original),16000)
        self.assertGreater(min(self.bi.nhi),0.0)

    def test_vectorized_original_He_HI_clock_interpolator(self):
        ts=np.array((0.,2.31e12,5.001e12,9.75e12,END))
        for h in self.h.values():
            a=original_linear_grid(h.nhi,ts)
            b=np.array([h.linear(h.nhi,float(t)) for t in ts])
            self.assertTrue(np.allclose(a,b,rtol=2e-15,atol=0))

    def test_verner95_original_HI_frozen_parameters(self):
        test=[12.3,13.599,13.6,13.61,13.67,13.7,20]
        for E in test:
            self.assertAlmostEqual(float(sig_hi_vec([E])[0]),sigma_hi(E),delta=2e-30)

    def test_outgoing_energy_direction_is_exact_null(self):
        o=np.array((.31,.41,math.sqrt(1-.31**2-.41**2)))
        s,R,J=outgoing_characteristic(self.bi,o,2e12,END)
        H=np.array(self.bi.H)
        expected=s*np.exp(-H*(END-2e12))
        self.assertLess(np.linalg.norm(expected/np.linalg.norm(expected)-o),5e-15)
        self.assertAlmostEqual(R,np.linalg.norm(expected),delta=2e-15)
        self.assertGreater(J,0)
        self.assertGreater(R,0)
        self.assertLessEqual(R,1)

    def test_FLRW_null_sky_jacobian(self):
        for o in ((0,0,1),(.35,.54,math.sqrt(1-.35**2-.54**2))):
            s,R,J=outgoing_characteristic(self.fl,o,3e12,END)
            self.assertAlmostEqual(J,1,delta=4e-14)
            self.assertTrue(np.allclose(s,o,atol=3e-15,rtol=0))

    def test_Jacobian_tangent_area_direct_finite_perturbation(self):
        from numpy.linalg import norm
        o=np.array((.35,.41,math.sqrt(1-.35**2-.41**2)))
        ns,R,J=outgoing_characteristic(self.bi,o,1e12,END)
        th,ph=screen(ns)
        D=np.exp(-np.array(self.bi.H)*(END-1e12))
        def mapdir(q):
            v=D*q
            return v/norm(v)
        eps=3e-5
        derivth=(mapdir((ns+eps*th)/norm(ns+eps*th))-mapdir((ns-eps*th)/norm(ns-eps*th)))/(2*eps)
        derivph=(mapdir((ns+eps*ph)/norm(ns+eps*ph))-mapdir((ns-eps*ph)/norm(ns-eps*ph)))/(2*eps)
        area=norm(np.cross(derivth,derivph))
        self.assertAlmostEqual(J,1/area,delta=2e-8)

    def test_parallel_transport_exact_FLRW_null(self):
        vec=(.42,.51,math.sqrt(1-.42**2-.51**2))
        self.assertAlmostEqual(parallel_rotation(self.fl,vec,8e12),0.,delta=1e-15)
        self.assertGreater(abs(parallel_rotation(self.bi,vec,8e12)),1e-7)
        self.assertEqual(parallel_rotation(self.bi,vec,0),0.)

    def test_outgoing_HI_domain_split(self):
        s=np.array((.4,.5,math.sqrt(1-.4**2-.5**2)))
        x=post_hi_optical_depth(self.bi,np.array([12.38,13.59,13.6,13.7]),s,6e12,END,8)
        self.assertTrue(np.all(x>=0))
        self.assertEqual(float(x[0]),0.)
        self.assertEqual(float(x[1]),0.)
        self.assertGreater(float(x[-1]),0)
        self.assertTrue(np.all(post_hi_optical_depth(self.bi,[13.7,13.3],s,END,END)==0))

    def test_outgoing_HI_symmetry_in_FLRW(self):
        e=[13.61,13.65,13.7]
        vals=[]
        for n in ((1,0,0),(0,1,0),(.3,.4,math.sqrt(.75))):
            vals.append(post_hi_optical_depth(self.fl,e,n,6e12,END,8))
        for v in vals[1:]:self.assertTrue(np.allclose(v,vals[0],atol=3e-17,rtol=0))

    def test_incoming_source_cohort_explicit_and_positive(self):
        E,w,n,b=incoming_photon_packets(self.bi,2.5e12,16,8,16,8)
        self.assertEqual(len(E),len(w))
        self.assertGreater(len(E),16*8*16)
        self.assertTrue(np.all(w>0))
        self.assertLessEqual(np.max(b),2.5e12)
        self.assertGreaterEqual(np.min(b),0)
        self.assertTrue(np.all(E<=BIRTH_EV+1e-13))
        self.assertTrue(np.all(E>=BIRTH_EV*math.exp(-1.01e-14*2.5e12)-1e-12))

    def test_local_Thomson_source_matches_original_PR317(self):
        h=self.bi;s=2.5e12;n_birth=16;nmu=8;nphi=16
        packet=incoming_photon_packets(h,s,n_birth,nmu,nphi,8)
        p=model_epoch(h,s,n_birth,nmu,nphi,8)
        mat=tuple(x for rr in p["source_matrix_3x3"] for x in rr)
        for mu,phi in ((.23,.74),(-.42,1.2)):
            v=math.sqrt(1-mu**2)
            no=(v*math.cos(phi),v*math.sin(phi),mu)
            I,Q,U,N,et,tt,maxhi=scatter_contribution(h,packet,s,s,no)
            I0,Q0,U0,_=outgoing_gain(mat,p["pre_first_scatter_unscattered_u_ev_per_H"],h.linear(h.ne,s),mu,phi)
            for a,b in ((I,I0),(Q,Q0),(U,U0)):
                self.assertAlmostEqual(a,b,delta=4e-13*max(abs(I0),1e-23))

    def test_sky_integrated_local_gain_equals_scattering_energy_rate(self):
        h=self.bi;s=2.5e12
        packets=incoming_photon_packets(h,s,8,8,16,8)
        predicted=C*SIG_T*h.linear(h.ne,s)*np.dot(packets[0],packets[1])
        measured=0.
        for _,_,n,mu,phi,w in gauss_birth_direction_grid(8,16):
            I,_,_,_,_,_,_=scatter_contribution(h,packets,s,s,n)
            measured+=4*math.pi*w*I
        self.assertAlmostEqual(measured/predicted,1.,delta=1e-12)

    def test_direct_directional_Stokes_positive(self):
        h=self.bi;s=2.5e12;t=END;pack=incoming_photon_packets(h,s,12,8,16,8)
        for n in ((1.,0.,0.),(0.,0.,1.),(.31,.41,math.sqrt(1-.31**2-.41**2))):
            I,Q,U,N,bt,tt,ht=scatter_contribution(h,pack,s,t,n)
            self.assertGreater(I,0)
            self.assertGreater(N,0)
            self.assertLess(math.hypot(Q,U),I)
            self.assertTrue(math.isfinite(ht))
            self.assertGreaterEqual(bt,0)
            self.assertLessEqual(bt,s*I*(1+1e-10))

    def test_FLRW_pol_null_local_and_retarded(self):
        h=self.fl;s=2.5e12;t=5e12
        packets=incoming_photon_packets(h,s,12,8,16,8)
        for n in ((1,0,0),(.31,.41,math.sqrt(1-.31**2-.41**2))):
            I,Q,U,N,bt,tt,ht=scatter_contribution(h,packets,s,t,n)
            self.assertLess(math.hypot(Q,U)/I,3e-11)

    def test_gaussian_scattering_clock_weights_exact_constant(self):
        for t in (5e12,END):
            for n in (4,8,12):
                nodes=gauss_scatter_times(t,n)
                self.assertAlmostEqual(sum(w for _,w in nodes),t,delta=.01)
                self.assertAlmostEqual(sum(s*w for s,w in nodes),t*t/2,delta=t*t*1e-14)

    def test_original_claim_gates_remain_locked(self):
        r=json.loads((HERE/"results"/"RESULT.json").read_text())
        self.assertEqual(r["original_F08"],"HOLD")
        self.assertFalse(r["source_original_F08_photon_state_equivalence"])
        self.assertEqual(r["rei_central"],"28/88_REPORTED")
        self.assertEqual(r["new_rei_canonical_nodes"],0)
        self.assertEqual(r["production"],"HOLD")

    def test_actual_science_rows_and_LoS_chronology(self):
        r=json.loads((HERE/"results"/"RESULT.json").read_text())
        p=HERE/"results"/"RETARDED_ONCE_THOMSON_OBSERVER_STOKES.csv.gz"
        q=HERE/"results"/"RETARDED_ONCE_SCATTER_TIME_CHRONOLOGY.csv.gz"
        self.assertEqual(sha(p),r["sky_sha256"])
        self.assertEqual(sha(q),r["chronology_sha256"])
        with gzip.open(p,"rt",newline="") as f:rows=list(csv.DictReader(f))
        with gzip.open(q,"rt",newline="") as f:chr=list(csv.DictReader(f))
        self.assertEqual(len(rows),r["sky_rows"])
        self.assertEqual(len(chr),r["chronology_rows"])
        for row in rows:
            I,Q,U,N=map(float,(row["I1_ev_per_H_sr"],row["Q1_ev_per_H_sr"],
                       row["U1_ev_per_H_sr"],row["N1_photons_per_H_sr"]))
            self.assertGreater(I,0);self.assertGreater(N,0)
            self.assertGreaterEqual(I*(1+1e-11),math.hypot(Q,U))
            self.assertAlmostEqual(math.hypot(Q,U)/I,float(row["P1_over_I1"]),delta=3e-13)
            self.assertTrue(0<=float(row["mean_birth_time_s"])<=float(row["mean_scatter_time_s"])<=float(row["observer_time_s"]))

if __name__=="__main__": unittest.main()
