(* ::Package:: *)

BeginPackage["BASS`IR`"];

SharedFramePhotonFormulaIDs::usage =
 "SharedFramePhotonFormulaIDs[] returns the exact six-formula REC/REI/HTT union.";
SharedFramePhotonEquationIRRegistry::usage =
 "SharedFramePhotonEquationIRRegistry[] returns six convention-locked EquationIR records.";
SharedFramePhotonInternalDependencyEdges::usage =
 "SharedFramePhotonInternalDependencyEdges[] returns the four dependencies inside the six-formula export.";
SharedFramePhotonExternalDependencyEdges::usage =
 "SharedFramePhotonExternalDependencyEdges[] returns the three dependencies on the canonical geometry registry.";
SharedFramePhotonSemanticExport::usage =
 "SharedFramePhotonSemanticExport[] returns the SYNC-MAP-02E owned-formula export.";
SharedFramePhotonSemanticExportQ::usage =
 "SharedFramePhotonSemanticExportQ[export] validates formula identities, hashes, dependencies and scope.";
SharedFramePhotonAlgebraChecks::usage =
 "SharedFramePhotonAlgebraChecks[] independently verifies convention-sensitive Lorentz and photon-flow identities.";

Begin["`Private`"];

ClearAll[
 SharedFramePhotonFormulaIDs, SharedFramePhotonEquationIRRegistry,
 SharedFramePhotonInternalDependencyEdges, SharedFramePhotonExternalDependencyEdges,
 SharedFramePhotonSemanticExport, SharedFramePhotonSemanticExportQ,
 SharedFramePhotonAlgebraChecks, sharedIR, sharedRecord,
 sharedDependenciesFor, sharedHashStringQ, sharedAllTrueQ
];

SharedFramePhotonFormulaIDs[] := {
 "BASS.FRAME.ABERRATED_DIRECTION.001",
 "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
 "BASS.FRAME.DOPPLER_FACTOR.001",
 "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
 "BASS.PHOTON.DIRECTION_FLOW.001",
 "BASS.PHOTON.ENERGY_DRIFT.001"
};

sharedIR[spec_Association] := BASS`IR`MakeEquationIR[Join[
 <|"provenance" -> <|
    "stage" -> "SYNC-MAP-02E",
    "owner" -> "bass",
    "source_path" -> "wolfram/BASS/Kernel/IR/SharedFramePhotonExport.wl"
   |>|>,
 spec
]];

SharedFramePhotonEquationIRRegistry[] := SortBy[
 {
  sharedIR[<|
    "formula_id" -> "BASS.FRAME.DOPPLER_FACTOR.001",
    "authority_theorem" ->
     "Exact Lorentz Doppler factor in outward-sky and future-photon charts",
    "target" -> "D",
    "free_indices" -> {},
    "representation" -> "local-Lorentz-frame-transform",
    "assumptions" -> {
      "metric signature (-,+,+,+)",
      "beta^2<1",
      "n_sky^a=-e^a",
      "gamma=(1-beta^2)^(-1/2)"
     },
    "domain" -> <|
      "velocity_domain" -> "open unit ball beta^2<1",
      "input_direction" -> "unit outward sky direction n_sky=-e",
      "chart_adapter" ->
       "D=gamma(1+beta.n_sky)=gamma(1-beta.e)"
     |>,
    "dimensions" -> <|"target" -> "1"|>,
    "terms" -> {
      <|
       "input" -> "gamma*(1+beta_dot_n_sky)",
       "coefficient" -> BASS`IR`ExactScalarAST[1]
      |>
     },
    "structural_zero_rules" -> {
      "D>0 for beta^2<1 and unit n_sky"
     },
    "branch_predicates" -> {
      "branch-independent local frame theorem"
     },
    "known_limits" -> {
      "beta=0 implies D=1",
      "future-photon chart gives gamma*(1-beta_dot_e)"
     }
   |>],

  sharedIR[<|
    "formula_id" -> "BASS.FRAME.ABERRATED_DIRECTION.001",
    "authority_theorem" ->
     "Exact regular Lorentz aberration map for an outward sky direction",
    "target" -> "n_sky_tilde^a",
    "free_indices" -> {"a"},
    "representation" -> "local-Lorentz-frame-transform",
    "assumptions" -> {
      "metric signature (-,+,+,+)",
      "beta^2<1",
      "n_sky.n_sky=1",
      "n_sky=-e",
      "D=gamma(1+beta.n_sky)"
     },
    "domain" -> <|
      "velocity_domain" -> "open unit ball beta^2<1",
      "input_direction" -> "unit outward sky direction",
      "regular_coefficient" ->
       "(gamma-1)/beta^2=gamma^2/(gamma+1)"
     |>,
    "dimensions" -> <|"target" -> "1"|>,
    "terms" -> {
      <|
       "input" ->
        "[n_sky+(gamma+gamma^2*beta_dot_n_sky/(gamma+1))*beta]/doppler_factor",
       "coefficient" -> BASS`IR`ExactScalarAST[1]
      |>
     },
    "structural_zero_rules" -> {
      "n_sky_tilde.n_sky_tilde=1",
      "inverse map is obtained by beta->-beta with chart exchange"
     },
    "branch_predicates" -> {
      "branch-independent local frame theorem"
     },
    "known_limits" -> {
      "beta=0 implies n_sky_tilde=n_sky",
      "linear limit n_sky_tilde=n_sky+beta-(beta.n_sky)n_sky+O(beta^2)"
     }
   |>],

  sharedIR[<|
    "formula_id" -> "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
    "authority_theorem" ->
     "Exact Lorentz solid-angle Jacobian on the celestial sphere",
    "target" -> "dOmega_tilde",
    "free_indices" -> {},
    "representation" -> "local-Lorentz-frame-transform",
    "assumptions" -> {
      "beta^2<1",
      "D=gamma(1+beta.n_sky)",
      "proper orientation-preserving sky chart"
     },
    "domain" -> <|
      "measure" -> "oriented solid angle on the unit sky",
      "input_direction" -> "outward sky direction"
     |>,
    "dimensions" -> <|"target" -> "1"|>,
    "terms" -> {
      <|
       "input" -> "doppler_factor^(-2)*dOmega",
       "coefficient" -> BASS`IR`ExactScalarAST[1]
      |>
     },
    "structural_zero_rules" -> {
      "Jacobian is positive for beta^2<1"
     },
    "branch_predicates" -> {
      "branch-independent local frame theorem"
     },
    "known_limits" -> {
      "beta=0 implies dOmega_tilde=dOmega"
     }
   |>],

  sharedIR[<|
    "formula_id" ->
     "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
    "authority_theorem" ->
     "Doppler-weight-one pullback of a positive Planck blackbody temperature field",
    "target" -> "T_tilde(n_sky_tilde)",
    "free_indices" -> {},
    "representation" -> "local-Lorentz-frame-transform",
    "assumptions" -> {
      "strictly positive Planckian thermodynamic temperature",
      "nu_tilde=D*nu",
      "Doppler weight d=1",
      "n_sky is the inverse-aberrated source direction"
     },
    "domain" -> <|
      "observable" -> "blackbody thermodynamic temperature only",
      "excluded" ->
       "general specific intensity foregrounds and spectral distortions"
     |>,
    "dimensions" -> <|"target" -> "temperature"|>,
    "terms" -> {
      <|
       "input" ->
        "doppler_factor*temperature(n_sky_of_n_sky_tilde)",
       "coefficient" -> BASS`IR`ExactScalarAST[1]
      |>
     },
    "structural_zero_rules" -> {
      "T_tilde>0 whenever T>0"
     },
    "branch_predicates" -> {
      "branch-independent output transform; not global matter tilt"
     },
    "known_limits" -> {
      "beta=0 implies T_tilde=T",
      "Planck argument h*nu/(k_B*T) is invariant"
     }
   |>],

  sharedIR[<|
    "formula_id" -> "BASS.PHOTON.ENERGY_DRIFT.001",
    "authority_theorem" ->
     "Exact homogeneous null-geodesic photon energy drift",
    "target" -> "R=D_s ln epsilon_gamma",
    "free_indices" -> {},
    "representation" ->
     "homogeneous-normal-frame-photon-phase-space",
    "assumptions" -> {
      "p^a=(epsilon_gamma/c)(n^a+e^a)",
      "e.e=1",
      "K_ab=H_geom h_ab+sigma_ab",
      "rates are per physical length s=c t"
     },
    "domain" -> <|
      "energy" -> "positive photon energy epsilon_gamma",
      "direction" -> "future photon propagation direction e",
      "background" -> "spatially homogeneous"
     |>,
    "dimensions" -> <|"target" -> "L^-1"|>,
    "terms" -> {
      <|
       "input" -> "H_geom",
       "coefficient" -> BASS`IR`ExactScalarAST[-1]
      |>,
      <|
       "input" -> "sigma_ab*e^a*e^b",
       "coefficient" -> BASS`IR`ExactScalarAST[-1]
      |>
     },
    "structural_zero_rules" -> {},
    "branch_predicates" -> {
      "all admitted Bianchi branches; no inhomogeneous perturbations"
     },
    "known_limits" -> {
      "FLRW limit sigma_ab=0 gives R=-H_geom",
      "Minkowski limit H_geom=sigma_ab=0 gives R=0"
     }
   |>],

  sharedIR[<|
    "formula_id" -> "BASS.PHOTON.DIRECTION_FLOW.001",
    "authority_theorem" ->
     "Exact homogeneous null-geodesic direction flow on the unit sphere",
    "target" -> "V^a=D_s e^a",
    "free_indices" -> {"a"},
    "representation" ->
     "homogeneous-normal-frame-photon-phase-space",
    "assumptions" -> {
      "e.e=1",
      "sigma_ab is spatial symmetric trace-free",
      "aB^a and nB_ab are Bianchi structure variables",
      "Omega_triad^a is triad rotation",
      "epsilon_123=+1",
      "rates are per physical length s=c t"
     },
    "domain" -> <|
      "direction" -> "future photon propagation direction e",
      "tangent_space" -> "T_e S^2",
      "background" -> "spatially homogeneous"
     |>,
    "dimensions" -> <|"target" -> "L^-1"|>,
    "terms" -> {
      <|
       "input" ->
        "(sigma_bc*e^b*e^c+aB_b*e^b)*e^a",
       "coefficient" -> BASS`IR`ExactScalarAST[1]
      |>,
      <|
       "input" -> "sigma^a_b*e^b",
       "coefficient" -> BASS`IR`ExactScalarAST[-1]
      |>,
      <|
       "input" -> "aB^a",
       "coefficient" -> BASS`IR`ExactScalarAST[-1]
      |>,
      <|
       "input" -> "epsilon^a_bc*Omega_triad^b*e^c",
       "coefficient" -> BASS`IR`ExactScalarAST[1]
      |>,
      <|
       "input" -> "epsilon^a_bc*e^b*nB^c_d*e^d",
       "coefficient" -> BASS`IR`ExactScalarAST[-1]
      |>
     },
    "structural_zero_rules" -> {"e_a V^a=0"},
    "branch_predicates" -> {
      "all admitted Bianchi branches; aB is not normal four-acceleration"
     },
    "known_limits" -> {
      "Bianchi I with sigma=Omega=0 gives V=0",
      "FLRW gives V=0"
     }
   |>]
 },
 Lookup[#, "formula_id", ""] &
];

SharedFramePhotonInternalDependencyEdges[] := SortBy[
 {
  <|
   "from" -> "BASS.FRAME.ABERRATED_DIRECTION.001",
   "to" -> "BASS.FRAME.DOPPLER_FACTOR.001",
   "relation" -> "depends_on"
  |>,
  <|
   "from" -> "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001",
   "to" -> "BASS.FRAME.DOPPLER_FACTOR.001",
   "relation" -> "depends_on"
  |>,
  <|
   "from" -> "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
   "to" -> "BASS.FRAME.DOPPLER_FACTOR.001",
   "relation" -> "depends_on"
  |>,
  <|
   "from" -> "BASS.FRAME.BLACKBODY_TEMPERATURE_PULLBACK.001",
   "to" -> "BASS.FRAME.ABERRATED_DIRECTION.001",
   "relation" -> "depends_on"
  |>
 },
 {Lookup[#, "from", ""], Lookup[#, "to", ""]} &
];

SharedFramePhotonExternalDependencyEdges[] := SortBy[
 {
  <|
   "from" -> "BASS.PHOTON.ENERGY_DRIFT.001",
   "to" -> "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
   "relation" -> "depends_on"
  |>,
  <|
   "from" -> "BASS.PHOTON.DIRECTION_FLOW.001",
   "to" -> "BASS.GEO.STRUCTURE_CONSTANTS.001",
   "relation" -> "depends_on"
  |>,
  <|
   "from" -> "BASS.PHOTON.DIRECTION_FLOW.001",
   "to" -> "BASS.GEO.EXTRINSIC_CURVATURE_SHEAR_SPLIT.001",
   "relation" -> "depends_on"
  |>
 },
 {Lookup[#, "from", ""], Lookup[#, "to", ""]} &
];

sharedDependenciesFor[id_String] := Sort@Lookup[
 Select[
  Join[
   SharedFramePhotonInternalDependencyEdges[],
   SharedFramePhotonExternalDependencyEdges[]
  ],
  Lookup[#, "from", None] === id &
 ],
 "to",
 {}
];

sharedRecord[ir_Association] := <|
 "formula_id" -> Lookup[ir, "formula_id", Missing["FormulaID"]],
 "owner" -> "bass",
 "authority_effect" -> "AUTHORITATIVE_DERIVATION",
 "status" -> "SYMBOLIC_VERIFIED_FORMULA_EXPORT",
 "source_path" ->
  "wolfram/BASS/Kernel/IR/SharedFramePhotonExport.wl",
 "semantic_hash" -> BASS`IR`FormulaSemanticSHA256[ir],
 "equation_ir" -> ir,
 "dependencies" -> sharedDependenciesFor[Lookup[ir, "formula_id", ""]],
 "allowed_consumer_modes" -> {
   "PINNED_IMPORT", "INDEPENDENT_ORACLE", "ADAPTER_SPECIALIZATION"
  }
|>;

SharedFramePhotonSemanticExport[] := Module[{records},
 records = sharedRecord /@ SharedFramePhotonEquationIRRegistry[];
 BASS`IR`CanonicalizeData@<|
  "schema_version" -> "1.0.0",
  "program_id" ->
   "BIANCHI-WOLFRAM-FOUR-REPOSITORY-FEDERATION-20260902",
  "stage_id" -> "SYNC_MAP_02E_SHARED_FRAME_PHOTON_EXPORT",
  "owner" -> "bass",
  "source_repository" -> "cosmosapjw-quantum/bass",
  "source_parent_commit" ->
   "9e39e2468b9efec05f33b9945de02fe2c8c6a66d",
  "contract_red_commit" ->
   "d4770f872addc9b73712babb44c675fbda2a19cb",
  "convention_hash" ->
   "e12258405c1c2ec296839524f5169e03441715b3acaaff1cef9de28bfa490a70",
  "predecessors" -> <|
    "sync_map_02b" -> <|
      "pull_request" -> 95,
      "commit" -> "f1eab555b42ebfaa3aa9d4021e097750aa0dfd96",
      "role" -> "REC active-relation classification"
     |>,
    "sync_map_02c" -> <|
      "pull_request" -> 98,
      "commit" -> "9e39e2468b9efec05f33b9945de02fe2c8c6a66d",
      "role" -> "complete active REI relation classification"
     |>,
    "sync_map_02d" -> <|
      "pull_request" -> 97,
      "commit" -> "7006aaab27834af37d5034f8f1e50943fe85c0f3",
      "role" -> "HTT local-boost and processed-response classification"
     |>
   |>,
  "formula_count" -> Length[records],
  "formulas" -> records,
  "internal_dependency_edges" ->
   SharedFramePhotonInternalDependencyEdges[],
  "external_dependency_edges" ->
   SharedFramePhotonExternalDependencyEdges[],
  "coverage" -> <|
    "included" -> {
      "exact local Lorentz Doppler and aberration formulas",
      "solid-angle Jacobian and positive blackbody temperature pullback",
      "exact homogeneous photon energy and direction characteristic generators",
      "outward-sky n_sky=-e convention adapter",
      "formula-level semantic hashes and dependency closure"
     },
    "excluded" -> {
      "finite electron tilt collision",
      "global matter tilt dynamics",
      "recombination and reionization microphysics",
      "background-provider implementation",
      "hierarchy truncation and numerical solver",
      "mask beam estimator response and inference"
     }
   |>,
  "claim_boundary" ->
   "SIX_FORMULA_EQUATIONIR_EXPORT_ONLY_NO_CONSUMER_EQUIVALENCE_FINITE_TILT_GLOBAL_TILT_BACKGROUND_PROVIDER_OR_SCIENCE_PROMOTION"
 |>
];

sharedHashStringQ[value_] := StringQ[value] &&
 StringLength[value] === 64 &&
 StringMatchQ[value, HexadecimalCharacter ..];
sharedAllTrueQ[association_Association] :=
 And @@ (TrueQ /@ Values[association]);
sharedAllTrueQ[_] := False;

SharedFramePhotonAlgebraChecks[] := Module[
 {b2, mu, gamma, coefficient, doppler, numeratorNorm,
  e, sigma, aB, nB, omega, qSigma, directionFlow,
  frameFormulaIDs, backgroundFormulaIDs},
 gamma = 1/Sqrt[1-b2];
 coefficient = gamma + gamma^2 mu/(gamma + 1);
 doppler = gamma (1 + mu);
 numeratorNorm = 1 + 2 coefficient mu + coefficient^2 b2;
 e = {e1, e2, e3};
 sigma = {
   {s11, s12, s13},
   {s12, s22, s23},
   {s13, s23, -s11 - s22}
  };
 aB = {a1, a2, a3};
 nB = {
   {n11, n12, n13},
   {n12, n22, n23},
   {n13, n23, n33}
  };
 omega = {o1, o2, o3};
 qSigma = e.sigma.e;
 directionFlow =
  (qSigma + aB.e) e - sigma.e - aB + Cross[omega, e] -
   Cross[e, nB.e];
 frameFormulaIDs = Select[
   SharedFramePhotonFormulaIDs[], StringStartsQ[#, "BASS.FRAME."] &];
 backgroundFormulaIDs = {
   "BASS.BG.HAMILTONIAN_PROJECTION.001",
   "BASS.BG.MOMENTUM_PROJECTION.001",
   "BASS.BG.SPATIAL_TRACE_PROJECTION.001",
   "BASS.BG.SPATIAL_PSTF_PROJECTION.001",
   "BASS.MATTER.SOURCE.ENVELOPE.001"
  };
 <|
  "aberrated_direction_unit_norm" -> TrueQ@FullSimplify[
    numeratorNorm/doppler^2 == 1,
    0 <= b2 < 1 && -Sqrt[b2] <= mu <= Sqrt[b2]
   ],
  "parallel_axis_fixed" -> TrueQ@FullSimplify[
    (1 + gamma Sqrt[b2] + gamma^2 b2/(gamma + 1))/
      (gamma (1 + Sqrt[b2])) == 1,
    0 <= b2 < 1
   ],
  "antiparallel_axis_fixed" -> TrueQ@FullSimplify[
    (-1 + gamma Sqrt[b2] - gamma^2 b2/(gamma + 1))/
      (gamma (1 - Sqrt[b2])) == -1,
    0 <= b2 < 1
   ],
  "future_photon_and_outward_sky_doppler_charts" -> TrueQ@Simplify[
    gamma (1 + betaDotNSky) == gamma (1 - betaDotE),
    betaDotNSky == -betaDotE
   ],
  "solid_angle_power_minus_two" ->
   SharedFramePhotonEquationIRRegistry[][[
     First@FirstPosition[
       Lookup[SharedFramePhotonEquationIRRegistry[], "formula_id"],
       "BASS.FRAME.SOLID_ANGLE_JACOBIAN.001"
      ]
    ]]["terms"][[1, "input"]] ===
    "doppler_factor^(-2)*dOmega",
  "blackbody_planck_argument_invariant" -> TrueQ@Simplify[
    (doppler nu)/(doppler temperature) == nu/temperature
   ],
  "direction_flow_tangent" -> TrueQ@Simplify[
    e.directionFlow == 0,
    Element[Variables[{e, sigma, aB, nB, omega}], Reals] && e.e == 1
   ],
  "energy_drift_FLRW_limit" -> TrueQ@Simplify[-H - 0 == -H],
  "frame_and_background_exports_disjoint" ->
   Intersection[frameFormulaIDs, backgroundFormulaIDs] === {}
 |>
];

SharedFramePhotonSemanticExportQ[export_Association] := Module[
 {formulas, ids, records, internal, external, expectedInternal,
  expectedExternal, included, recalculatedHashes},
 formulas = Lookup[export, "formulas", Missing["Formulas"]];
 internal = Lookup[export, "internal_dependency_edges", Missing["Internal"]];
 external = Lookup[export, "external_dependency_edges", Missing["External"]];
 If[!ListQ[formulas] || !ListQ[internal] || !ListQ[external],
  Return[False]
 ];
 ids = Lookup[formulas, "formula_id", Missing["FormulaID"]];
 records = Lookup[formulas, "equation_ir", Missing["EquationIR"]];
 expectedInternal = SharedFramePhotonInternalDependencyEdges[];
 expectedExternal = SharedFramePhotonExternalDependencyEdges[];
 included = Lookup[Lookup[export, "coverage", <||>], "included", {}];
 recalculatedHashes = BASS`IR`FormulaSemanticSHA256 /@ records;
 And[
  Lookup[export, "schema_version", None] === "1.0.0",
  Lookup[export, "stage_id", None] ===
   "SYNC_MAP_02E_SHARED_FRAME_PHOTON_EXPORT",
  Lookup[export, "owner", None] === "bass",
  Lookup[export, "formula_count", None] === 6,
  Length[formulas] === 6,
  Sort[ids] === Sort[SharedFramePhotonFormulaIDs[]],
  DuplicateFreeQ[ids],
  AllTrue[records, BASS`IR`EquationIRQ],
  AllTrue[Lookup[formulas, "semantic_hash", None], sharedHashStringQ],
  Lookup[formulas, "semantic_hash", None] === recalculatedHashes,
  AllTrue[formulas,
   Lookup[#, "owner", None] === "bass" &&
   Lookup[#, "authority_effect", None] ===
    "AUTHORITATIVE_DERIVATION" &&
   Lookup[#, "status", None] ===
    "SYMBOLIC_VERIFIED_FORMULA_EXPORT" &
  ],
  internal === expectedInternal,
  external === expectedExternal,
  Length[internal] === 4,
  Length[external] === 3,
  FreeQ[export, _Real],
  FreeQ[
   ToLowerCase@StringRiffle[included, "\n"],
   "finite electron tilt" | "global matter tilt" |
    "recombination" | "reionization" | "numerical solver" |
    "hierarchy truncation" | "likelihood" | "inference"
  ],
  sharedAllTrueQ[SharedFramePhotonAlgebraChecks[]],
  Lookup[export, "claim_boundary", None] ===
   "SIX_FORMULA_EQUATIONIR_EXPORT_ONLY_NO_CONSUMER_EQUIVALENCE_FINITE_TILT_GLOBAL_TILT_BACKGROUND_PROVIDER_OR_SCIENCE_PROMOTION"
 ]
];
SharedFramePhotonSemanticExportQ[_] := False;

End[];
EndPackage[];
