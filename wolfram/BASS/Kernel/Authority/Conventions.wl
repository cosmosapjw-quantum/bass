(* ::Package:: *)

BeginPackage["BASS`Authority`"];

ConventionLock::usage = "ConventionLock[] returns the exact project convention association.";
ConventionRequiredKeys::usage = "ConventionRequiredKeys[] returns required top-level keys.";
ConventionLockQ::usage = "ConventionLockQ[lock] validates non-negotiable conventions.";

Begin["`Private`"];

ClearAll[ConventionLock, ConventionRequiredKeys, ConventionLockQ];

ConventionRequiredKeys[] := {
 "schema_version", "program_id", "metric_signature",
 "spacetime_dimension", "spatial_dimension", "spatial_orientation",
 "normal_congruence", "time_derivative", "photon_momentum",
 "observed_direction", "extrinsic_curvature", "riemann_convention",
 "screen_orientation", "project_spin", "pstf_normalization",
 "units", "frequency_variable", "claim_boundary"
};

ConventionLock[] := <|
 "schema_version" -> "1.0.0",
 "program_id" -> "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
 "metric_signature" -> {-1, 1, 1, 1},
 "spacetime_dimension" -> 4,
 "spatial_dimension" -> 3,
 "spatial_orientation" -> <|"epsilon_123" -> 1|>,
 "normal_congruence" -> <|"norm" -> -1,
   "projector" -> "h_ab = g_ab + n_a n_b"|>,
 "time_derivative" -> <|"operator" -> "D0",
   "definition" -> "D0 = (1/c) partial_t", "length_parameter" -> "s = c t"|>,
 "photon_momentum" -> <|
   "definition" -> "p^a = (epsilon_gamma/c) (n^a + e^a)",
   "direction_norm" -> 1, "normal_orthogonality" -> 0|>,
 "observed_direction" -> <|"relation" -> "n_hat_obs = -e"|>,
 "extrinsic_curvature" -> <|
   "definition" -> "K_ab = H_geom h_ab + sigma_ab", "shear_trace" -> 0|>,
 "riemann_convention" -> <|
   "definition" -> "[nabla_a,nabla_b] v^c = R_abd^c v^d",
   "authority" -> "xAct convention adapter must be checked explicitly"|>,
 "screen_orientation" -> <|"triad" -> "(u,v,e) positively oriented",
   "cross_product" -> "u cross v = e",
   "stokes_v" -> "V = -2 u^a A_ab v^b"|>,
 "project_spin" -> <|"project_field" -> "P = Q + i U",
   "spin_weight" -> -2, "rotation" -> "P -> exp(-2 i psi) P"|>,
 "pstf_normalization" -> <|"symmetrization_weight" -> "unit",
   "trace_removal" -> "spatial PSTF"|>,
 "units" -> <|"natural_units_default" -> False,
   "explicit_constants" -> {"c", "hbar", "k_B", "G"},
   "geometric_rates_dimension" -> "L^-1"|>,
 "frequency_variable" -> <|"photon_energy" -> "epsilon_gamma",
   "bolometric_map" -> "apply only once"|>,
 "claim_boundary" ->
  "CONVENTION_INFRASTRUCTURE_ONLY_NO_BACKGROUND_OR_SCIENCE_PROMOTION"|>;

ConventionLockQ[lock_Association] := And[
 SubsetQ[Keys[lock], ConventionRequiredKeys[]],
 Lookup[lock, "schema_version", None] === "1.0.0",
 Lookup[lock, "metric_signature", None] === {-1, 1, 1, 1},
 Lookup[lock, "spacetime_dimension", None] === 4,
 Lookup[lock, "spatial_dimension", None] === 3,
 Lookup[Lookup[lock, "spatial_orientation", <||>], "epsilon_123", None] === 1,
 Lookup[Lookup[lock, "normal_congruence", <||>], "norm", None] === -1,
 Lookup[Lookup[lock, "observed_direction", <||>], "relation", None] ===
  "n_hat_obs = -e",
 Lookup[Lookup[lock, "project_spin", <||>], "spin_weight", None] === -2,
 Lookup[Lookup[lock, "units", <||>], "natural_units_default", None] === False,
 Lookup[Lookup[lock, "units", <||>], "geometric_rates_dimension", None] ===
  "L^-1"
];
ConventionLockQ[_] := False;

End[];
EndPackage[];
