"""Bounded reproducibility/physical falsification for frozen KM2N photons.
Run with: python -m unittest discover -s . -p test_first_scatter_joint.py -v
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from scipy.integrate import quad

import first_scatter_joint as f

class KM2JointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((f.OUT/'KM2_FIRST_SCATTER_JOINT_RESULTS.json').read_text())
        cls.rec={(v['gl'],v['k']):v for v in cls.data['data']}

    def test_frozen_source_hashes(self):
        self.assertEqual(len(f.ORIGINAL_SHA256),9)
        for name,expected in f.ORIGINAL_SHA256.items():
            self.assertEqual(f.sha256(f.SOURCE/name),expected,name)
        self.assertEqual(self.data['source_head'],f.ORIGINAL_KM2N_HEAD)

    def test_reject_forged_input_even_valid_npz_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'KM2K_PACKETS_GL12_GLT8.npz').write_bytes(b'forged-npz')
            with mock.patch.object(f,'SOURCE',root):
                with self.assertRaises(ArithmeticError):
                    f.data_inputs(12)

    def test_joint_counts_and_owner_progress(self):
        self.assertEqual(self.data['time_pairs'],29120)
        self.assertEqual(self.data['ray_snapshots'],4000)
        self.assertEqual(len(self.data['data']),10)
        self.assertEqual(self.data['new_Einstein_IVPs'],0)
        self.assertEqual(self.data['upper_dag'],'9/15 scoped/source_mapped')
        self.assertEqual(self.data['new_upper_completed'],0)
        self.assertFalse(self.data['production_ready'])
        self.assertFalse(self.data['merge_ready'])

    def test_source_moments_reconstruct_original_for_multiple_source_times(self):
        for gl in (12,16):
            pack,opt,ledger,_=f.data_inputs(gl)
            for j in (1,8,21,40):
                M,My,gap=f.photon_source_moments(pack,opt,ledger,j)
                self.assertLess(gap,4e-12)
                self.assertEqual(M.shape,(j*8,3,3))
                self.assertEqual(My.shape,(j*8,3,3))
                self.assertTrue(np.isfinite(My).all())
                self.assertGreater(float(np.trace(M.sum(axis=0))),0)

    def test_full_ray_screen_reconstruction_against_original_source(self):
        for gl in (12,16):
            with np.load(f.OUT/f'KM2_FIRST_SCATTER_JOINT_GL{gl}_U40.npz',allow_pickle=False) as actual:
                with np.load(f.SOURCE/f'KM2N_ONCE_POL_SCREEN_GL{gl}_U40.npz',allow_pickle=False) as orig:
                    got=actual['screen_first_scattered_bolometric']
                    source=orig['screen_bolometric_first_one']
                    self.assertLess(float(np.max(abs(got-source))/np.max(abs(source))),6e-12)
                    self.assertLess(float(np.max(abs(actual['source_binned_screen'].sum(axis=0)-got)) / np.max(abs(got))),3e-12)
                    self.assertLess(float(np.min(np.linalg.eigvalsh(got))),1e-10)

    def test_true_emission_precedes_first_scatter(self):
        with (f.OUT/'KM2_FIRST_SCATTER_EMISSION_SCATTER_PAIRS.csv').open(newline='') as data:
            rows=list(csv.DictReader(data))
        self.assertEqual(len(rows),29120)
        for row in rows:
            self.assertGreater(float(row['u_scatter']),float(row['u_emission']))
            self.assertGreater(float(row['contribution_rho']),0)
            self.assertLessEqual(float(row['u_scatter']),float(row['u_observer']))

    def test_source_energy_and_polarization_owner_reconciliation(self):
        for rec in self.data['data']:
            self.assertLess(rec['rho_relative_gap'],1e-11)
            self.assertLess(rec['joint_mass_relative_gap'],4e-12)
            self.assertLess(rec['rest_source_moment_gap'],4e-12)
            self.assertLess(rec['linear_polarization_relative_difference'],1e-11)
            self.assertAlmostEqual(sum(x['fraction'] for x in rec['emission_groups']),1.0,delta=3e-12)
            self.assertLess(rec['finite_frequency_bin_centroid_absolute_gap'],.5/1200)
            self.assertLess(rec['mean_emission_time'],rec['mean_scatter_time'])
            self.assertLess(rec['mean_scatter_time'],rec['u_obs'])

    def test_GL12_GL16_agree_on_source_chronology(self):
        for k in f.SNAPSHOTS:
            a=self.rec['GL12',k]; b=self.rec['GL16',k]
            self.assertLess(abs(a['mean_emission_time']-b['mean_emission_time']),5e-10)
            self.assertLess(abs(a['mean_scatter_time']-b['mean_scatter_time']),5e-10)
            self.assertLess(abs(a['emission_scatter_time_correlation']-b['emission_scatter_time_correlation']),1e-9)

    def test_source_epoch_group_polarization_not_a_single_hazard_kernel(self):
        x=self.rec['GL16',40]
        frac=[z['fraction'] for z in x['emission_groups']]
        pol=[z['mean_pol'] for z in x['emission_groups']]
        self.assertTrue(all(z>0 for z in frac))
        self.assertLess(abs(sum(frac)-1),1e-12)
        self.assertGreater(pol[0],pol[-1])
        self.assertGreater(x['emission_scatter_time_correlation'],.5)
        # Separate, physically differently conditioned fixed-ray opacity hazard:
        # the former treats a photon already present; this one includes an actual
        # source and a gain into the tagged observer ray.
        hazard_only_mean=0.1785083546659884
        self.assertGreater(abs(x['mean_scatter_time']-hazard_only_mean),0.002)

    def test_source_log_frequency_age_signal(self):
        vals=self.rec['GL16',40]['emission_group_logfrequency_centroids']
        self.assertEqual(len(vals),5)
        self.assertTrue(all(v is not None for v in vals))
        self.assertLess(vals[0],vals[-1])
        self.assertLess(self.rec['GL16',40]['finite_frequency_bin_centroid_absolute_gap'],4e-6)

    def test_constant_rate_exactly_one_emission_scatter_analytic_control(self):
        # Exact analytic double time integral for constant rest j, loss nu and no expansion.
        U=.25;nu=9.;j=2.e-8
        integral,err=quad(lambda te: j*nu*(U-te)*math.exp(-nu*(U-te)),0,U,
                          epsabs=1e-15,epsrel=1e-12)
        exact=j/nu*(1-(1+nu*U)*math.exp(-nu*U))
        self.assertLess(abs(integral/exact-1),2e-14)
        self.assertLess(err,1e-15)

    def test_bad_survival_sign_is_falsified_by_true_physics(self):
        # A deliberately corrupted positive exponential cannot reproduce the finite
        # original KM2N 1-scattered observer tensor in the same strict setup.
        pack,op,ledger,orig=f.data_inputs(12)
        scatters={j:f.photon_source_moments(pack,op,ledger,j) for j in range(1,41)}
        true=f.compute_one(12,40,pack,op,ledger,orig,scatters)[0]
        tau=ledger['tau'];n=ledger['w'][40];mu=ledger['mu'];U=float(ledger['time'][40])
        # Corrupt exactly one physical factor, retaining all other operators.
        wrong=0.
        for jj in range(1,41):
            M=scatters[jj][0].sum(axis=0)
            F=ledger['F'][jj];D=ledger['D'][jj];ratio=mu[40]/mu[jj]
            w=(1 if jj==40 else 4 if jj%2 else 2)*(U/40)/3
            malformed=f.ALPHA*ledger['nu'][jj]*w*ratio**4*np.exp(+(tau[40]-tau[jj]))*D**(-3)
            screen=np.einsum('nac,ab,nbd->ncd',F,M,F,optimize=True)
            wrong+=float(n@(malformed*np.trace(screen,axis1=-1,axis2=-2)))
        self.assertGreater(abs(wrong/true['rho_exactly_one']-1),0.1)

if __name__=='__main__':unittest.main()
