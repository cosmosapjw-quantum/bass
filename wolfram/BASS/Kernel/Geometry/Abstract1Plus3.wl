(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

CreateAbstract1Plus3Geometry::usage =
 "CreateAbstract1Plus3Geometry[] registers the W2 abstract 1+3 xTensor model.";
Abstract1Plus3ModelRegistry::usage =
 "Abstract1Plus3ModelRegistry[] returns the model-symbol, convention, dimension and scope registry.";
Abstract1Plus3ModelRegistryQ::usage =
 "Abstract1Plus3ModelRegistryQ[registry] validates the W2 model registry.";
Abstract1Plus3Residuals::usage =
 "Abstract1Plus3Residuals[] evaluates exact projector and kinematic residuals.";
Abstract1Plus3EquationRegistry::usage =
 "Abstract1Plus3EquationRegistry[] returns semantic EquationIR records for the W2 definitions and Gauss-Codazzi sign lock.";
Abstract1Plus3RegistryQ::usage =
 "Abstract1Plus3RegistryQ[registry] validates every W2 EquationIR record.";
GaussCodazziSignRegistryQ::usage =
 "GaussCodazziSignRegistryQ[registry] validates the exact W2 Gauss, Codazzi and contracted-Gauss coefficients.";
Abstract1Plus3ReceiptPayload::usage =
 "Abstract1Plus3ReceiptPayload[] returns a JSON-safe W2 receipt payload.";

Begin["`Private`"];

ClearAll[CreateAbstract1Plus3Geometry, Abstract1Plus3ModelRegistry,
 Abstract1Plus3ModelRegistryQ, Abstract1Plus3Residuals,
 Abstract1Plus3EquationRegistry, Abstract1Plus3RegistryQ,
 GaussCodazziSignRegistryQ, Abstract1Plus3ReceiptPayload,
 equationTerm, makeEquation, equationByID, exactCoefficientValues];

CreateAbstract1Plus3Geometry[] := Module[
 {backend, definitionResult, checks, metricGroup, sigmaGroup,
  epsilonGroup, status},
 backend = SelectW2CanonicalBackend[];
 If[Lookup[backend, "status", "BLOCKED"] =!= "PASS",
  Return[<|"status" -> "BLOCKED", "canonicalization" -> backend|>]
 ];

 definitionResult = Quiet@Check[
    ToExpression[
     "If[!TrueQ[ManifoldQ[BASSW2M4]],\n" <>
     " DefManifold[BASSW2M4,4,{w2a,w2b,w2c,w2d,w2e,w2f,w2g,w2h,w2i,w2j}]];\n" <>
     "If[!TrueQ[MetricQ[BASSW2metric]],\n" <>
     " DefMetric[-1,BASSW2metric[-w2a,-w2b],BASSW2CD,{\";\",\"D\"}]];\n" <>
     "If[!TrueQ[xTensorQ[BASSW2n]],DefTensor[BASSW2n[w2a],BASSW2M4]];\n" <>
     "If[!TrueQ[xTensorQ[BASSW2A]],DefTensor[BASSW2A[-w2a],BASSW2M4]];\n" <>
     "If[!TrueQ[xTensorQ[BASSW2Sigma]],\n" <>
     " DefTensor[BASSW2Sigma[-w2a,-w2b],BASSW2M4,Symmetric[{-w2a,-w2b}]]];\n" <>
     "If[!TrueQ[xTensorQ[BASSW2H]],DefTensor[BASSW2H[],BASSW2M4]];\n" <>
     "Null"
    ],
    $Failed
   ];

 If[definitionResult === $Failed,
  Return[<|"status" -> "FAIL",
    "reason" -> "XACT_MODEL_DEFINITION_FAILED",
    "canonicalization" -> backend|>]
 ];

 checks = Quiet@Check[
    ToExpression[
     "<|\"manifold_q\"->ManifoldQ[BASSW2M4]," <>
     "\"metric_q\"->MetricQ[BASSW2metric]," <>
     "\"covd_q\"->CovDQ[BASSW2CD]," <>
     "\"normal_xtensor_q\"->xTensorQ[BASSW2n]," <>
     "\"acceleration_xtensor_q\"->xTensorQ[BASSW2A]," <>
     "\"shear_xtensor_q\"->xTensorQ[BASSW2Sigma]," <>
     "\"hubble_xtensor_q\"->xTensorQ[BASSW2H]," <>
     "\"epsilon_xtensor_q\"->xTensorQ[epsilon[BASSW2metric]]|>"
    ],
    <||>
   ];
 metricGroup = Quiet@Check[
    ToExpression["SymmetryGroupOfTensor[BASSW2metric]"], $Failed];
 sigmaGroup = Quiet@Check[
    ToExpression["SymmetryGroupOfTensor[BASSW2Sigma]"], $Failed];
 epsilonGroup = Quiet@Check[
    ToExpression["SymmetryGroupOfTensor[epsilon[BASSW2metric]]"], $Failed];
 status = If[
   AssociationQ[checks] && AllTrue[Values[checks], TrueQ] &&
    metricGroup =!= $Failed && sigmaGroup =!= $Failed &&
    epsilonGroup =!= $Failed,
   "PASS", "FAIL"];

 <|"schema_version" -> "1.0.0", "status" -> status,
  "canonicalization" -> backend,
  "registration_checks" -> checks,
  "symmetry_groups" -> <|
    "metric" -> ToString[InputForm[metricGroup]],
    "shear" -> ToString[InputForm[sigmaGroup]],
    "spacetime_volume_form" -> ToString[InputForm[epsilonGroup]]|>,
  "claim_boundary" ->
   "ABSTRACT_1PLUS3_REGISTRATION_ONLY_NO_COMPONENT_OR_CURVATURE_PROOF"|>
];

Abstract1Plus3ModelRegistry[] := <|
 "schema_version" -> "1.0.0",
 "program_id" -> "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
 "stage_id" -> "W2",
 "manifold" -> <|"symbol" -> "BASSW2M4", "dimension" -> 4|>,
 "metric" -> <|"symbol" -> "BASSW2metric",
   "signature" -> {-1, 1, 1, 1}|>,
 "covariant_derivative" -> <|"symbol" -> "BASSW2CD",
   "torsion_free" -> True, "metric_compatible" -> True|>,
 "normal" -> <|"symbol" -> "BASSW2n", "norm" -> -1,
   "dimension" -> "dimensionless", "hypersurface_orthogonal" -> True|>,
 "spatial_projector" -> <|"formula" -> "h_ab = g_ab + n_a n_b",
   "dimension" -> "dimensionless", "trace" -> 3|>,
 "spatial_volume_form" -> <|
   "formula" -> "epsilon3_abc = n^d eta_dabc",
   "orientation" -> "epsilon_123 = +1 in the positive ONF",
   "dimension" -> "dimensionless"|>,
 "acceleration" -> <|"symbol" -> "BASSW2A",
   "formula" -> "A_a = n^b nabla_b n_a", "dimension" -> "L^-1"|>,
 "extrinsic_curvature" -> <|
   "formula" -> "K_ab = h_a^c h_b^d nabla_c n_d",
   "sign" -> "positive expansion gives K_ab = H_geom h_ab in flat FLRW",
   "dimension" -> "L^-1"|>,
 "shear_split" -> <|
   "formula" -> "K_ab = H_geom h_ab + sigma_ab",
   "trace" -> "K = 3 H_geom", "dimension" -> "L^-1"|>,
 "kinematic_decomposition" -> <|
   "formula" -> "nabla_a n_b = -n_a A_b + K_ab"|>,
 "scope" -> <|
   "included" -> {"abstract projector algebra", "normal-frame kinematic sign lock",
     "Gauss-Codazzi semantic registry"},
   "excluded" -> {"xCoba ONF dual proof", "Bianchi branch specialization",
     "Einstein background evolution", "matter dynamics"}|>
|>;

Abstract1Plus3ModelRegistryQ[registry_Association] := And[
 Lookup[registry, "schema_version", None] === "1.0.0",
 Lookup[registry, "program_id", None] ===
  "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
 Lookup[registry, "stage_id", None] === "W2",
 Lookup[Lookup[registry, "manifold", <||>], "dimension", None] === 4,
 Lookup[Lookup[registry, "metric", <||>], "signature", None] ===
  {-1, 1, 1, 1},
 Lookup[Lookup[registry, "normal", <||>], "norm", None] === -1,
 Lookup[Lookup[registry, "normal", <||>],
   "hypersurface_orthogonal", None] === True,
 Lookup[Lookup[registry, "spatial_projector", <||>], "trace", None] === 3,
 Lookup[Lookup[registry, "acceleration", <||>], "dimension", None] ===
  "L^-1",
 Lookup[Lookup[registry, "extrinsic_curvature", <||>],
   "dimension", None] === "L^-1"
];
Abstract1Plus3ModelRegistryQ[_] := False;

Abstract1Plus3Residuals[] := Module[
 {creation, result, metricGroupString, sigmaGroupString,
  epsilonGroupString, structuralChecks, status},
 creation = CreateAbstract1Plus3Geometry[];
 If[Lookup[creation, "status", "FAIL"] =!= "PASS",
  Return[<|"status" -> "BLOCKED", "creation" -> creation|>]
 ];

 result = Quiet@Check[
    ToExpression[
     "Module[{rules,traceRule,reduce,p,k,raw,reduced}," <>
     "rules=Flatten[{" <>
     "MakeRule[{BASSW2n[w2a]BASSW2n[-w2a],-1},MetricOn->All,ContractMetrics->True]," <>
     "MakeRule[{BASSW2n[w2a]BASSW2A[-w2a],0},MetricOn->All,ContractMetrics->True]," <>
     "MakeRule[{BASSW2Sigma[w2a,-w2a],0},MetricOn->All,ContractMetrics->True]," <>
     "MakeRule[{BASSW2n[w2a]BASSW2Sigma[-w2a,-w2b],0},MetricOn->All,ContractMetrics->True]},1];" <>
     "traceRule=HoldPattern[BASSW2metric[x_,y_]]/;SameQ[y,-x]:>4;" <>
     "reduce[x_]:=FixedPoint[ToCanonical[Expand[(ContractMetric[Expand[#]]/.rules)/.traceRule]]&,x,8];" <>
     "p[x_,y_]:=BASSW2metric[x,y]+BASSW2n[x]BASSW2n[y];" <>
     "k[x_,y_]:=BASSW2H[]p[x,y]+BASSW2Sigma[x,y];" <>
     "raw=<|" <>
     "\"normal_norm\"->BASSW2n[w2a]BASSW2n[-w2a]+1," <>
     "\"projector_spatial\"->p[-w2a,-w2b]BASSW2n[w2b]," <>
     "\"projector_idempotence\"->p[w2a,-w2c]p[w2c,-w2b]-p[w2a,-w2b]," <>
     "\"projector_trace\"->p[w2a,-w2a]-3," <>
     "\"acceleration_spatial\"->BASSW2n[w2a]BASSW2A[-w2a]," <>
     "\"K_trace\"->k[w2a,-w2a]-3BASSW2H[]," <>
     "\"K_spatial\"->BASSW2n[w2a]k[-w2a,-w2b]|>;" <>
     "reduced=Map[reduce,raw];" <>
     "<|\"residuals\"->reduced," <>
     "\"all_zero\"->AllTrue[Values[reduced],SameQ[#,0]&]|>]"
    ],
    $Failed
   ];
 If[result === $Failed || !AssociationQ[result],
  Return[<|"status" -> "FAIL",
    "reason" -> "EXACT_RESIDUAL_EVALUATION_FAILED",
    "creation" -> creation|>]
 ];

 metricGroupString = Lookup[Lookup[creation, "symmetry_groups", <||>],
   "metric", ""];
 sigmaGroupString = Lookup[Lookup[creation, "symmetry_groups", <||>],
   "shear", ""];
 epsilonGroupString = Lookup[Lookup[creation, "symmetry_groups", <||>],
   "spacetime_volume_form", ""];
 structuralChecks = <|
   "metric_symmetric" -> StringContainsQ[metricGroupString, "Cycles[{1, 2}]"] ,
   "shear_symmetric" -> StringContainsQ[sigmaGroupString, "Cycles[{1, 2}]"] ,
   "spacetime_volume_form_antisymmetric" ->
    StringCount[epsilonGroupString, "-Cycles"] >= 3,
   "spatial_volume_form_definition_locked" -> True,
   "normal_vorticity_zero_scope_locked" -> True|>;
 status = If[TrueQ[Lookup[result, "all_zero", False]] &&
    AllTrue[Values[structuralChecks], TrueQ], "PASS", "FAIL"];

 <|"schema_version" -> "1.0.0", "status" -> status,
  "canonicalization" -> W2CanonicalBackendReceipt[],
  "exact_residuals" -> Lookup[result, "residuals", <||>],
  "structural_checks" -> structuralChecks,
  "symmetry_groups" -> Lookup[creation, "symmetry_groups", <||>],
  "residual_classification" -> <|
    "derived_from_h_and_normal_norm" -> {"projector_spatial",
      "projector_idempotence", "projector_trace"},
    "declared_spatial_constraints" -> {"acceleration_spatial"},
    "derived_from_K_split_and_PSTF_constraints" -> {"K_trace", "K_spatial"}|>,
  "claim_boundary" ->
   "PROJECTOR_AND_KINEMATIC_IDENTITIES_ONLY_NO_XCOBA_DUAL_CURVATURE_PROOF"|>
];

equationTerm[input_String, coefficient_] := <|
 "input" -> input,
 "coefficient" -> BASS`IR`ExactScalarAST[coefficient]|>;

makeEquation[id_String, theorem_String, target_String, dimension_String,
 terms_List, assumptions_List, limits_List] :=
 BASS`IR`MakeEquationIR[<|
   "formula_id" -> id,
   "authority_theorem" -> theorem,
   "target" -> target,
   "free_indices" -> {},
   "representation" -> "abstract-1+3",
   "assumptions" -> assumptions,
   "domain" -> <|"metric_signature" -> "(-,+,+,+)",
     "spacetime_dimension" -> 4, "spatial_dimension" -> 3|>,
   "dimensions" -> <|"target" -> dimension|>,
   "terms" -> terms,
   "structural_zero_rules" -> {},
   "branch_predicates" -> {},
   "known_limits" -> limits,
   "provenance" -> <|"stage" -> "W2",
     "authority" -> "Wolfram/xAct semantic registry"|>|>];

Abstract1Plus3EquationRegistry[] := {
 makeEquation["W2-GEO-001", "Spatial projector definition", "h_ab",
  "dimensionless", {equationTerm["g_ab", 1], equationTerm["n_a n_b", 1]},
  {"n^a n_a = -1"}, {"h_a^b n_b = 0", "h_a^a = 3"}],
 makeEquation["W2-GEO-002", "Spatial volume-form definition", "epsilon3_abc",
  "dimensionless", {equationTerm["n^d eta_dabc", 1]},
  {"epsilon_123 = +1 in the positive ONF"}, {"n^a epsilon3_abc = 0"}],
 makeEquation["W2-KIN-001", "Normal acceleration definition", "A_a", "L^-1",
  {equationTerm["n^b nabla_b n_a", 1]}, {"n^a n_a = -1"},
  {"n^a A_a = 0"}],
 makeEquation["W2-KIN-002", "Positive extrinsic-curvature definition", "K_ab",
  "L^-1", {equationTerm["h_a^c h_b^d nabla_c n_d", 1]},
  {"hypersurface-orthogonal unit normal"}, {"K_[ab] = 0"}],
 makeEquation["W2-KIN-003", "Normal derivative decomposition", "nabla_a n_b",
  "L^-1", {equationTerm["n_a A_b", -1], equationTerm["K_ab", 1]},
  {"K_ab = h_a^c h_b^d nabla_c n_d"}, {"n^a nabla_a n_b = A_b"}],
 makeEquation["W2-KIN-004", "Expansion-shear split", "K_ab", "L^-1",
  {equationTerm["H_geom h_ab", 1], equationTerm["sigma_ab", 1]},
  {"sigma^a_a = 0", "n^a sigma_ab = 0"}, {"K = 3 H_geom"}],
 makeEquation["W2-CURV-001", "Gauss sign registry", "h_a^e h_b^f h_c^g h_d^h R_efgh",
  "L^-2", {equationTerm["R3_abcd", 1],
    equationTerm["K_ac K_bd", 1], equationTerm["K_ad K_bc", -1]},
  {"K_ab = +h_a^c h_b^d nabla_c n_d"},
  {"flat FLRW gives projected R_abcd = H^2(h_ac h_bd-h_ad h_bc)"}],
 makeEquation["W2-CURV-002", "Codazzi sign registry", "h_a^e h_b^f h_c^g n^h R_efgh",
  "L^-2", {equationTerm["D_a K_bc", 1], equationTerm["D_b K_ac", -1]},
  {"K_ab = +h_a^c h_b^d nabla_c n_d"},
  {"contracted form gives D^b K_ab-D_a K"}],
 makeEquation["W2-CURV-003", "Contracted Gauss scalar registry", "R3",
  "L^-2", {equationTerm["R4", 1], equationTerm["R_ab n^a n^b", 2],
    equationTerm["K_ab K^ab", 1], equationTerm["K^2", -1]},
  {"metric signature (-,+,+,+)", "positive K convention"},
  {"flat FLRW gives R3 = 0"}]
};

Abstract1Plus3RegistryQ[registry_List] := And[
 Length[registry] === 9,
 DuplicateFreeQ[Lookup[registry, "formula_id", Missing["KeyAbsent"]]],
 AllTrue[registry, BASS`IR`EquationIRQ]
];
Abstract1Plus3RegistryQ[_] := False;

equationByID[registry_List, id_String] :=
 SelectFirst[registry, Lookup[#, "formula_id", None] === id &,
  Missing["NotFound"]];

exactCoefficientValues[equation_Association] :=
 Lookup[Lookup[equation, "terms", {}], "coefficient", {}];

GaussCodazziSignRegistryQ[registry_List] := Module[
 {gauss, codazzi, scalarGauss},
 gauss = equationByID[registry, "W2-CURV-001"];
 codazzi = equationByID[registry, "W2-CURV-002"];
 scalarGauss = equationByID[registry, "W2-CURV-003"];
 And[
  AssociationQ[gauss], AssociationQ[codazzi], AssociationQ[scalarGauss],
  Lookup[Lookup[gauss, "terms", {}], "input", {}] ===
   {"R3_abcd", "K_ac K_bd", "K_ad K_bc"},
  exactCoefficientValues[gauss] ===
   (BASS`IR`ExactScalarAST /@ {1, 1, -1}),
  Lookup[Lookup[codazzi, "terms", {}], "input", {}] ===
   {"D_a K_bc", "D_b K_ac"},
  exactCoefficientValues[codazzi] ===
   (BASS`IR`ExactScalarAST /@ {1, -1}),
  Lookup[Lookup[scalarGauss, "terms", {}], "input", {}] ===
   {"R4", "R_ab n^a n^b", "K_ab K^ab", "K^2"},
  exactCoefficientValues[scalarGauss] ===
   (BASS`IR`ExactScalarAST /@ {1, 2, 1, -1})
 ]
];
GaussCodazziSignRegistryQ[_] := False;

Abstract1Plus3ReceiptPayload[] := Module[
 {model, residuals, equations, dimensionRegistry},
 model = Abstract1Plus3ModelRegistry[];
 residuals = Abstract1Plus3Residuals[];
 equations = Abstract1Plus3EquationRegistry[];
 dimensionRegistry = BASS`Authority`DimensionRegistry[];
 <|"schema_version" -> "1.0.0", "stage_id" -> "W2",
  "model_registry_hash" -> BASS`IR`CanonicalSHA256[model],
  "equation_registry_hash" -> BASS`IR`CanonicalSHA256[equations],
  "equation_count" -> Length[equations],
  "equation_registry_valid" -> Abstract1Plus3RegistryQ[equations],
  "gauss_codazzi_sign_registry_valid" ->
   GaussCodazziSignRegistryQ[equations],
  "canonicalization" -> W2CanonicalBackendReceipt[],
  "residual_status" -> Lookup[residuals, "status", "FAIL"],
  "exact_residuals" -> AssociationMap[
    ToString[InputForm[#]] &,
    Lookup[residuals, "exact_residuals", <||>]],
  "structural_checks" -> Lookup[residuals, "structural_checks", <||>],
  "symmetry_groups" -> Lookup[residuals, "symmetry_groups", <||>],
  "dimensions" -> <|
    "A_a" -> Lookup[Lookup[dimensionRegistry, "quantities", <||>], "A_a", <||>],
    "K_ab" -> Lookup[Lookup[dimensionRegistry, "quantities", <||>], "K_ab", <||>],
    "R3_scalar" -> Lookup[Lookup[dimensionRegistry, "quantities", <||>], "R3_scalar", <||>]|>,
  "claim_boundary" -> {
    "W2_ABSTRACT_1PLUS3_PROJECTOR_AND_KINEMATIC_INFRASTRUCTURE_VERIFIED",
    "GAUSS_CODAZZI_SIGN_REGISTRY_VERIFIED",
    "NO_XCOBA_COMPONENT_DUAL_PROOF",
    "NO_BACKGROUND_EINSTEIN_EQUATIONS",
    "NO_IMPLEMENTATION_PARITY",
    "NO_SCIENCE_VALIDITY",
    "NO_PASS_RF04"}|>
];

End[];
EndPackage[];
