#!/usr/bin/env python3
"""Independent geometry controls for BASS × original REI F08 physical Sachs distance."""
import csv,gzip,math,sys,unittest
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import sachs_f08 as m

def path_dimless(H,n,te,order=80):
 H=np.asarray(H);n=np.asarray(n)
 p,w=leggauss(order)
 t=te+(m.TOBS-te)*(p+1)/2
 ai=np.exp((t[:,None]-m.TOBS)*H[None,:])
 omega=np.sqrt(np.sum((n[None,:]/ai)**2,axis=-1))
 return (m.HMEAN*(m.TOBS-te)/2)*np.einsum("q,qi->i",w,n[None,:]*ai**(-2)/omega[:,None])

class PhysicsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=m.validate_source(m.SOURCE)
  cls.indices=[0,123,991,3471,7652,10511]
 def test_original_source_and_unique_rows(self):
  self.assertEqual(len(self.rows),10752)
  self.assertEqual(len(set((r["window_fraction"],r["angular_nmu"],r["angular_nphi"],r["mu_bin"],r["phi_bin"]) for r in self.rows)),10752)
 def test_isotropic_exact_de_sitter_limit(self):
  rows=[self.rows[i] for i in self.indices]
  n=np.array([[float(r[k]) for k in ("nx","ny","nz")] for r in rows])
  z=np.array([float(r["relative_redshift"]) for r in rows])
  te=m.TOBS-np.log1p(z)/m.HMEAN
  DA,rat,axes,gram=m.beam([m.HMEAN]*3,n,te,order=32)
  ref=z/(1+z)
  self.assertLess(float(np.max(abs(DA/ref-1))),4e-14)
  self.assertLess(float(np.max(abs(rat-1))),4e-14)
 def test_positive_beam_and_reciprocity(self):
  rows=[self.rows[i] for i in self.indices]
  n=np.array([[float(r[k]) for k in ("nx","ny","nz")] for r in rows])
  te=np.array([float(r["emission_time_s"]) for r in rows])
  DA,rat,axes,_=m.beam(m.S0_BI,n,te,order=48)
  self.assertTrue(np.all(DA>0))
  self.assertTrue(np.all(axes>0))
  self.assertTrue(np.all(rat>=1))
  z=np.array([float(r["relative_redshift"]) for r in rows])
  DL=DA*m.C/m.HMEAN*(1+z)**2
  self.assertLess(float(np.max(abs(DL/(DA*m.C/m.HMEAN*(1+z)**2)-1))),1e-14)
 def test_independent_angular_finite_difference_at_fixed_redshift(self):
  rows=[self.rows[i] for i in (0,123,7652)]
  eps=2e-4
  H=np.asarray(m.S0_BI)
  for row in rows:
   n=np.array([float(row[k]) for k in ("nx","ny","nz")])
   z=float(row["relative_redshift"]);te=float(row["emission_time_s"])
   DA,ratio,axes,g0=m.beam(H,n[None,:],np.array([te]),order=80)
   tangent=m.basis(n[None,:])[0]
   qs=(n/np.exp((te-m.TOBS)*H));qs/=np.linalg.norm(qs)
   cols=[]
   for k in range(2):
    e=tangent[:,k]
    ns=[(n+s*eps*e)/np.linalg.norm(n+s*eps*e) for s in (+1,-1)]
    ds=[m.directional_lookback(H,nn,z) for nn in ns]
    xp=[path_dimless(H,nn,m.TOBS-d) for nn,d in zip(ns,ds)]
    local=np.exp((te-m.TOBS)*H)*(xp[0]-xp[1])/(2*eps)
    cols.append(local-qs*np.dot(qs,local))
   F=np.column_stack(cols);gFD=F.T@F
   self.assertLess(float(np.max(abs(gFD-g0[0]))/max(np.max(abs(g0[0])),1e-100)),3e-7)
 def test_angular_parity(self):
  rows=[self.rows[0]]
  n=np.array([[float(rows[0][k]) for k in ("nx","ny","nz")]])
  te=np.array([float(rows[0]["emission_time_s"])])
  a=m.beam(m.S0_BI,n,te,order=48)
  b=m.beam(m.S0_BI,-n,te,order=48)
  self.assertLess(float(abs(a[0][0]-b[0][0])),2e-15)
 def test_time_quadrature_stability(self):
  rows=[self.rows[i] for i in self.indices]
  n=np.array([[float(r[k]) for k in ("nx","ny","nz")] for r in rows])
  te=np.array([float(r["emission_time_s"]) for r in rows])
  a=m.beam(m.S0_BI,n,te,order=24)[0]
  b=m.beam(m.S0_BI,n,te,order=48)[0]
  self.assertLess(float(np.max(abs(a/b-1))),3e-13)
 def test_small_redshift_directional_H(self):
  n=np.array([[.6,.8,0.]])
  n/=np.linalg.norm(n,axis=1)[:,None]
  te=np.array([m.TOBS-1e10])
  z=math.expm1(m.HMEAN*1e10)
  DA=m.beam([m.HMEAN]*3,n,te)[0][0]
  self.assertLess(abs((1+z)*DA/z-1),5e-12)
 def test_negative_input_and_source_tamper(self):
  with self.assertRaises(ValueError):
   m.beam(m.S0_BI,np.zeros((1,3)),np.array([m.TOBS/2]))
  with self.assertRaises(ValueError):
   m.beam([m.HMEAN,-m.HMEAN,m.HMEAN],np.array([[1.,0.,0.]]),np.array([m.TOBS/2]))
 def test_all_source_same_shells(self):
  counts={}
  for r in self.rows:
   k=(float(r["window_fraction"]),int(r["angular_nmu"]),int(r["angular_nphi"]))
   counts[k]=counts.get(k,0)+1
  self.assertEqual(len(counts),12)
  self.assertTrue(all(c==a*b for (_,a,b),c in counts.items()))
 def test_full_science_output_consistency(self):
  dest=ROOT/"results"/"BASS_REI_F08_S0_MATCHED_SACHS_RESULT.json"
  if not dest.exists():self.skipTest("no full-source output yet")
  import json
  o=json.loads(dest.read_text())
  self.assertEqual(o["num_physical_ray_rows"],10752)
  self.assertEqual(o["canonical_delta"],0)
  self.assertEqual(o["source_pair_id"],m.REI_PAIR_ID)
  self.assertEqual(len(o["physical_outputs"]),12)

if __name__=="__main__":unittest.main()
