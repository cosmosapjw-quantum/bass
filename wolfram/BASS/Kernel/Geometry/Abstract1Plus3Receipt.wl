(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

Begin["`Private`"];

Clear[Abstract1Plus3ReceiptPayload];

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
  "exact_residuals" -> Map[
    ToString[InputForm[#]] &,
    Lookup[residuals, "exact_residuals", <||>]],
  "structural_checks" -> Lookup[residuals, "structural_checks", <||>],
  "symmetry_groups" -> Lookup[residuals, "symmetry_groups", <||>],
  "dimensions" -> <|
    "A_a" -> Lookup[Lookup[dimensionRegistry, "quantities", <||>],
      "A_a", <||>],
    "K_ab" -> Lookup[Lookup[dimensionRegistry, "quantities", <||>],
      "K_ab", <||>],
    "R3_scalar" -> Lookup[Lookup[dimensionRegistry, "quantities", <||>],
      "R3_scalar", <||>]|>,
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
