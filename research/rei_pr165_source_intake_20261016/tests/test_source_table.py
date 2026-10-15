"""Strict PR164 BASS -> native REI read-only geometry interface tests.

Tests are run in this ChatGPT container; no local Desktop Commander or NCP run.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"source_pr164"))
from source_table import BackgroundTable, SourceTableError, H0, AREF, AEND, XRANGE
from kinetic_tangent import EinsteinTangent

class SourceTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basedir=ROOT/"source_pr164"
        cls.table=BackgroundTable(cls.basedir/"PRODUCER_RECEIPT.json",cls.basedir/"PROPOSED_REI_BACKGROUND.csv")

    def _modified(self,case="SIGNED_PLUS",key="Sigma",value="-1",update_hash=True,index=0):
        temp=tempfile.TemporaryDirectory()
        p=pathlib.Path(temp.name)
        cp=p/"PROPOSED_REI_BACKGROUND.csv";mp=p/"PRODUCER_RECEIPT.json"
        with (self.basedir/"PROPOSED_REI_BACKGROUND.csv").open() as f:
            inp=list(csv.DictReader(f))
        [r for r in inp if r["case"]==case][index][key]=str(value)
        with cp.open("w",newline="") as f:
            wr=csv.DictWriter(f,fieldnames=list(inp[0]),lineterminator="\n")
            wr.writeheader();wr.writerows(inp)
        m=json.loads((self.basedir/"PRODUCER_RECEIPT.json").read_text())
        if update_hash:m["csv_sha256"]=hashlib.sha256(cp.read_bytes()).hexdigest()
        mp.write_text(json.dumps(m,indent=2))
        return temp,mp,cp

    def test_positive_source_inventory_and_clock(self):
        r=self.table.export_receipt()
        self.assertEqual(r["source_knot_rows"],968)
        self.assertEqual(len(r["case_names"]),8)
        self.assertLess(r["max_independent_row_raychaudhuri_relative"],3e-12)
        self.assertLess(r["max_producer_vs_integral_clock_relative"],5e-10)

    def test_native_geometry_signed_shear_and_volume(self):
        for name,(nodes,segs,times) in self.table.samples.items():
            for x in [0.,segs[0].right.x/2.,XRANGE/2.,XRANGE]:
                p=self.table.point_at_x(name,x)
                self.assertAlmostEqual(p.a_perp*p.a_perp*p.a_parallel/p.a**3,1.,delta=1e-12)
                self.assertAlmostEqual(p.sigma_signed,p.s_per_s/p.h_per_s,delta=1e-14)
                self.assertAlmostEqual(p.Sigma,math.sqrt(3)*abs(p.sigma_signed),delta=1e-13)
                self.assertAlmostEqual(p.H_perp_per_s,p.h_per_s-p.s_per_s,delta=5e-31)
                self.assertAlmostEqual(p.H_parallel_per_s,p.h_per_s+2*p.s_per_s,delta=5e-31)
                native=p.as_native_background_point()
                self.assertEqual(native["sigma"],p.sigma_signed)
                self.assertGreater(native["h_flrw_per_s"],0)

    def test_signed_orientation_and_zero_shear_limit(self):
        t=self.table
        self.assertEqual(t.point_at_x("COLD_FLRW",XRANGE).Sigma,0.)
        self.assertEqual(t.point_at_x("WARM_ISOTROPIC",XRANGE).Sigma,0.)
        self.assertGreater(t.point_at_x("SIGNED_PLUS",0.).sigma_signed,0.)
        self.assertLess(t.point_at_x("SIGNED_MINUS",0.).sigma_signed,0.)
        self.assertAlmostEqual(t.point_at_x("SIGNED_MINUS",0.).Sigma,
                               t.point_at_x("SIGNED_PLUS",0.).Sigma,delta=5e-16)

    def test_interpolated_kinematic_identity_and_positive_clock(self):
        for name,(nodes,segs,times) in self.table.samples.items():
            for i in (0,12,34,58,83,119):
                seg=segs[i]
                x=seg.left.x+.32895*seg.span
                p=self.table.point_at_x(name,x)
                b,h,s,_=seg.state(x)
                self.assertEqual(s,p.s_per_s)
                eps=1e-5*seg.span
                bp=self.table.point_at_x(name,x+eps).b
                bm=self.table.point_at_x(name,x-eps).b
                self.assertLess(abs((bp-bm)/(2*eps)-s/h),3e-10)
                tp=seg.dt_integral(x+eps)
                tm=seg.dt_integral(x-eps)
                self.assertLess(abs((tp-tm)/(2*eps)*h-1),8e-10)
                self.assertGreater(tp,tm)

    def test_proper_time_inversion_with_no_checkpoint_reuse(self):
        for name,(nodes,segs,times) in self.table.samples.items():
            for ratio in (0.,.01,.11,.51,.89,1.):
                t=times[-1]*ratio
                point=self.table.point_at_time(name,t)
                self.assertLess(abs(point.time_s-t)/max(t,1.),5e-13)
                self.assertLess(abs(self.table.point_at_x(name,point.x).time_s-t)/max(t,1.),5e-13)
                self.assertGreater(point.h_per_s,0)

    def test_midpoint_independent_pr164_dense_ode_oracle(self):
        for case,(nodes,segs,times) in self.table.samples.items():
            params=next(z["params"] for z in self.table.info["cases_receipt"] if z["case"]==case)
            model=EinsteinTangent(**params)
            sol=model.solution(n=121)
            for i in (0,20,41,70,119):
                seg=segs[i];x=.5*(seg.left.x+seg.right.x)
                b,v,T=sol.sol(x)[:3]
                _,h,_,_=model.field(x,b,v)
                p=self.table.point_at_x(case,x)
                self.assertLess(abs(p.b-b),5e-11)
                self.assertLess(abs(p.h_per_s/h-1),3e-10)
                self.assertLess(abs(p.s_per_s-model.href*v)/model.href,2e-9)
                self.assertLess(abs(p.time_s-T/model.href)/(T/model.href),8e-10)

    def test_reject_changed_csv_sha(self):
        a,p,c=self._modified(update_hash=False)
        with a,self.assertRaisesRegex(SourceTableError,"CSV_SHA256_MISMATCH"):
            BackgroundTable(p,c)

    def test_reject_changed_sigma_even_if_attacker_resigns_checksum(self):
        a,p,c=self._modified()
        with a,self.assertRaisesRegex(SourceTableError,"SIGMA_MAGNITUDE_MISMATCH"):
            BackgroundTable(p,c)

    def test_reject_wrong_signed_sigma(self):
        a,p,c=self._modified(key="signed_s_over_H",value=0.1234)
        with a,self.assertRaisesRegex(SourceTableError,"SIGN_OF_SHEAR_MISMATCH"):
            BackgroundTable(p,c)

    def test_reject_bad_hamiltonian(self):
        a,p,c=self._modified(key="H_mean_per_s",value=1e-19)
        with a,self.assertRaises(SourceTableError):BackgroundTable(p,c)

    def test_reject_late_cold_one_percent_hamiltonian_excess(self):
        temp=tempfile.TemporaryDirectory()
        with temp:
            folder=pathlib.Path(temp.name)
            csv_path=folder/"PROPOSED_REI_BACKGROUND.csv"
            receipt_path=folder/"PRODUCER_RECEIPT.json"
            with (self.basedir/"PROPOSED_REI_BACKGROUND.csv").open(newline="") as handle:
                rows=list(csv.DictReader(handle))
            row=[r for r in rows if r["case"]=="COLD_FLRW"][-1]
            changed_h=float(row["H_mean_per_s"])*math.sqrt(1.01)
            row["H_mean_per_s"]=str(changed_h)
            row["H_perp_per_s"]=str(changed_h)
            row["H_parallel_per_s"]=str(changed_h)
            with csv_path.open("w",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=list(rows[0]),lineterminator="\n")
                writer.writeheader();writer.writerows(rows)
            receipt=json.loads((self.basedir/"PRODUCER_RECEIPT.json").read_text())
            receipt["csv_sha256"]=hashlib.sha256(csv_path.read_bytes()).hexdigest()
            receipt_path.write_text(json.dumps(receipt,indent=2))
            with self.assertRaisesRegex(SourceTableError,"EINSTEIN_HAMILTONIAN"):
                BackgroundTable(receipt_path,csv_path)

    def test_reject_fake_isotropic_cold_history(self):
        a,p,c=self._modified(case="WARM_ISOTROPIC",key="massive_rho_norm",value=1e5)
        with a,self.assertRaisesRegex(SourceTableError,"EINSTEIN_HAMILTONIAN"):
            BackgroundTable(p,c)

    def test_reject_producer_clock_reversal(self):
        a,p,c=self._modified(key="proper_elapsed_s",value=-1.,index=1)
        with a,self.assertRaisesRegex(SourceTableError,"NONMONOTONE_CLOCK"):
            BackgroundTable(p,c)

    def test_reject_unphysical_pressure(self):
        a,p,c=self._modified(case="MASS3_A_PLUS",key="massive_pbar_norm",value=-20.)
        with a,self.assertRaisesRegex(SourceTableError,"KINETIC_PRESSURE_CONE"):
            BackgroundTable(p,c)

    def test_no_extrapolation_or_unknown_case(self):
        for f in (lambda:self.table.point_at_x("COLD_FLRW",-1e-6),
                  lambda:self.table.point_at_x("COLD_FLRW",XRANGE+1e-6),
                  lambda:self.table.point_at_time("COLD_FLRW",-1.),
                  lambda:self.table.point_at_time("UNKNOWN",0.),
                  lambda:self.table.point_at_time("COLD_FLRW",1e22)):
            with self.assertRaises(SourceTableError):f()

if __name__=="__main__":unittest.main(verbosity=2)
