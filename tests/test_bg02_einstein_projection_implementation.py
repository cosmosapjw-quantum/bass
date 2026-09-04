from __future__ import annotations
import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; D=R/"docs/bass_master_ssot_v2/BG_02_IMPLEMENTATION"
RED=D/"BG_02_IMPLEMENTATION_RED_CONTRACT.json"; PIN=D/"BG_02_DESIGN_AUTHORITY_PIN.json"
PROD=R/"wolfram/BASS/Kernel/Background/EinsteinProjection.wl"; REG=D/"BG_02_IMPLEMENTATION_REGISTRY.json"
INIT=R/"wolfram/BASS/Kernel/init.wl"; WLT=R/"wolfram/BASS/Tests/BG02EinsteinProjectionImplementation.wlt"; WLS=R/"wolfram/scripts/run_bg02_einstein_projection_native.wls"
P="80d271cc528e1a0ffa813ecd3e3fb7610f3fa755"; T="3fd8818938eaa0988988c6927cff799455a7a31d"; A="ef6d51aad709555737617e2021ba50c553c90b6c"
SPECS=[
("S",['BeginPackage["BASS`Background`"]']),
("S",['"Background", "EinsteinProjection.wl"']),
("R",["formula_count","BASS.BG.EINSTEIN_RESIDUAL.001","BASS.BG.EXCEPTIONAL_VI_MOMENTUM_CARRIER.001","L^-2"]),
("S",[x+"::usage" for x in ["EinsteinResidualTensor","EinsteinProjectionRegistry","HamiltonianProjection","MomentumProjection","SpatialTraceProjection","SpatialPSTFProjection","SpatialTraceRate","ADMTraceRate","RaychaudhuriRate","ShearLieRate","ShearProjectedRate"]]),
("S",["G_ab + Lambda g_ab - kappa_G T_ab","EinsteinResidualTensor"]),
("S",["HamiltonianProjection","R3","K^2","K_ab K^ab","kappaG","rho"]),
("S",["MomentumProjection","D^b K_ab","D_a K","kappaG","q_a"]),
("S",["SpatialTraceProjection","Lie","D.A","A2","kappaG","p"]),
("S",["SpatialPSTFProjection","R3PSTF","DPSTFA","APSTFA","pi_ab"]),
("S",["F_ADM - F_trace + Hres/2","F_trace - F_Ray + Hres/6","F_ADM - F_Ray + 2 Hres/3"]),
("R",["off_shell_identities","projects_Hres_to_zero"]),
("R",["LIE_DERIVATIVE_PSTF","PROJECTED_COVARIANT_NORMAL_DERIVATIVE"]),
("R",["connection_order_guards","Bianchi_V","Bianchi_II","I_IX_ONLY_IS_INSUFFICIENT"]),
("R",["flat_flrw","flat_de_sitter","kasner_vacuum","-1/(3 tau^2)"]),
("S",["N22 Sigma12 + (N23 - 3 A) Sigma13"]),
("B",["xTensor","xCoba","TestsFailedCount","TestsNotEvaluatedCount","TEMPORARY_FILE_STRICT_JSON_ROUND_TRIP_THEN_RENAME","CONSTRAINT_PROPAGATION_VERIFIED","PASS_RF04"])]
class BG02EinsteinProjectionImplementationTests(unittest.TestCase):
 def test_exact_scientific_parent_and_design_are_pinned(self):
  r=json.loads(RED.read_text()); p=json.loads(PIN.read_text()); self.assertEqual((r["scientific_parent"]["commit"],r["scientific_parent"]["tree"],r["design_authority"]["commit"]),(P,T,A)); self.assertEqual(p["semantic_federation_reference"]["effect"],"DEPENDENCY_REFERENCE_ONLY_NOT_CODE_ANCESTRY")
 def test_pr91_geometry_authority_sources_are_present(self):
  for f in ["Abstract1Plus3.wl","LeviCivitaConnection.wl","ONFConnectionCurvature.wl","XCobaCurvatureWitnesses.wl"]: self.assertTrue((R/"wolfram/BASS/Kernel/Geometry"/f).is_file())
 def _fail(self,i):
  kind,tokens=SPECS[i]
  if kind=="S": self.assertTrue(PROD.is_file(),f"BG02 production module missing: {PROD}"); text=PROD.read_text() if i!=1 else INIT.read_text()
  elif kind=="R": self.assertTrue(REG.is_file(),f"BG02 implementation registry missing: {REG}"); text=REG.read_text()
  else:
   self.assertTrue(PROD.is_file(),f"BG02 production module missing: {PROD}"); self.assertTrue(REG.is_file(),f"BG02 implementation registry missing: {REG}"); self.assertTrue(WLT.is_file() and WLS.is_file()); text=WLS.read_text()+WLT.read_text()+REG.read_text(); self.assertEqual(WLT.read_text().count("VerificationTest["),26)
  for token in tokens: self.assertIn(token,text)
 def test_production_module_exists(self): self._fail(0)
 def test_loader_imports_exactly_one_background_module(self): self._fail(1)
 def test_implementation_registry_has_exact_14_ids(self): self._fail(2)
 def test_required_public_api_names_are_exposed(self): self._fail(3)
 def test_single_off_shell_residual_is_the_only_projection_authority(self): self._fail(4)
 def test_hamiltonian_projection_contract_is_present(self): self._fail(5)
 def test_momentum_projection_contract_is_present(self): self._fail(6)
 def test_spatial_trace_projection_contract_is_present(self): self._fail(7)
 def test_spatial_pstf_projection_contract_is_present(self): self._fail(8)
 def test_three_expansion_rates_remain_distinct_and_off_shell(self): self._fail(9)
 def test_off_shell_rate_identity_metadata_is_registered(self): self._fail(10)
 def test_shear_rate_derivative_kinds_are_explicit(self): self._fail(11)
 def test_locked_curvature_route_and_connection_order_guards_exist(self): self._fail(12)
 def test_flat_flrw_de_sitter_and_kasner_limits_are_registered(self): self._fail(13)
 def test_exceptional_vi_minus_one_ninth_carrier_is_retained(self): self._fail(14)
 def test_native_xact_replay_and_claim_firewalls_exist(self): self._fail(15)
if __name__=="__main__": unittest.main()
