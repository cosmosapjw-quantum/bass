(* Canonical typed SymIR v2 candidate export; SymIR v1 is not read or written. *)
BeginPackage["BASS`GenericBianchiCandidate`"];

BASSBuildSymIRV2::usage = "BASSBuildSymIRV2[spec,derived,adapters,sourceHashes] builds an unpromoted typed candidate.";

Begin["`Private`"];

BASSTensor[id_String, array_, domains_List, variance_List, symmetries_List] := Module[{encoded = BASSEncodeSparse[array]},
  <|
    "entries" -> encoded["entries"],
    "id" -> id,
    "index_domains" -> domains,
    "shape" -> encoded["shape"],
    "symmetries" -> Sort[symmetries],
    "variance" -> variance
  |>
];

BASSPass[name_String, version_String, inputHash_String, output_] := <|
  "input_hash" -> inputHash,
  "output_hash" -> BASSSHA256UTF8[BASSCanonicalJSON[output]],
  "pass_name" -> name,
  "pass_version" -> version
|>;

BASSBuildSymIRV2[canonicalSpec_Association, derived_Association, adapters_List, sourceHashes_Association] := Module[
  {specHash, orientationHash, tensors, expressions, dependencyDAG, cse, coreReceipt},
  specHash = BASSSHA256UTF8[BASSCanonicalJSON[canonicalSpec]];
  orientationHash = BASSSHA256UTF8[BASSCanonicalJSON[canonicalSpec["convention"]["epsilon_orientation"]]];
  tensors = SortBy[{
    BASSTensor["C", BASSDecodeSparse[canonicalSpec["structure_constants"], {3, 3, 3}], {"spatial", "spatial", "spatial"}, {"up", "down", "down"}, {"antisymmetric(lower_1,lower_2)"}],
    BASSTensor["Gamma3", derived["connection3"], {"spatial", "spatial", "spatial"}, {"up", "down", "down"}, {}],
    BASSTensor["Ricci3", derived["ricci3"], {"spatial", "spatial"}, {"down", "down"}, {"symmetric(0,1)"}],
    BASSTensor["S3", derived["tracefree_ricci3"], {"spatial", "spatial"}, {"down", "down"}, {"symmetric(0,1)", "tracefree(0,1)"}],
    BASSTensor["a", derived["a"], {"spatial"}, {"down"}, {}],
    BASSTensor["n", derived["n"], {"spatial", "spatial"}, {"up", "up"}, {"symmetric(0,1)"}]
  }, Lookup[#, "id"] &];
  expressions = SortBy[derived["typed_blocks"], Lookup[#, "id"] &];
  dependencyDAG = Join[
    Map[<|"dependencies" -> {}, "id" -> #|> &, {
      "C", "Gamma4", "Ricci4", "Sigma", "W", "a", "anisotropic_stress",
      "distribution", "heat_flux", "metric", "n", "normal", "p", "pressure",
      "q", "rho_u", "spatial_projector", "u"
    }],
    {
      <|"dependencies" -> {"C"}, "id" -> "Gamma3"|>,
      <|"dependencies" -> {"C"}, "id" -> "connection_from_structure"|>,
      <|"dependencies" -> {"C", "Gamma3"}, "id" -> "Ricci3"|>,
      <|"dependencies" -> {"C", "Gamma3"}, "id" -> "spatial_ricci"|>,
      <|"dependencies" -> {"Ricci3"}, "id" -> "S3"|>,
      <|"dependencies" -> {"anisotropic_stress", "heat_flux", "pressure", "rho_u", "spatial_projector", "u"}, "id" -> "matter_decomposition"|>,
      <|"dependencies" -> {"Ricci4", "metric"}, "id" -> "einstein_tensor"|>,
      <|"dependencies" -> {"einstein_tensor", "matter_decomposition", "normal"}, "id" -> "hamiltonian_constraint"|>,
      <|"dependencies" -> {"einstein_tensor", "matter_decomposition", "normal"}, "id" -> "momentum_constraint"|>,
      <|"dependencies" -> {"Gamma4", "distribution", "p"}, "id" -> "massless_characteristic_liouville"|>,
      <|"dependencies" -> {"Sigma", "W", "n", "q"}, "id" -> "n_evolution"|>,
      <|"dependencies" -> {"Sigma", "W", "a", "q"}, "id" -> "a_evolution"|>
    }
  ];
  cse = {
    <|"expr" -> <|"args" -> {<|"args" -> {}, "op" -> "Ref", "value" -> "Ricci3"|>}, "op" -> "Trace"|>, "id" -> "t000_spatial_scalar_curvature"|>
  };
  coreReceipt = <|"tensors" -> tensors, "expressions" -> expressions|>;
  BASSCanonicalValue @ <|
    "adapters" -> adapters,
    "assumptions" -> Sort[{
      "dimension(spatial) == 3",
      "metric signature == (-,+,+,+)",
      "structure constants are exact and spatially homogeneous",
      "n is symmetric and n.a == 0",
      "all specialization predicates are exact invariants"
    }],
    "authority_status" -> "CANDIDATE_UNPROMOTED_FORMULA_BYTES_ABSENT",
    "convention_hash" -> canonicalSpec["convention_hash"],
    "cse_temporaries" -> cse,
    "dependency_dag" -> dependencyDAG,
    "expressions" -> expressions,
    "formula_source_hashes" -> KeySort[sourceHashes],
    "historical_formula" -> <|
      "is_dag_parent" -> False,
      "label_sha256" -> "3ecf0dbc8b47a8af83da81e9ed37823b6922e139e420c5bfa2e071b6bbabe361",
      "status" -> "UNRESOLVED_REFERENCE"
    |>,
    "orientation_hash" -> orientationHash,
    "pass_receipts" -> SortBy[{
      BASSPass["exact_spec_validation", "1", specHash, canonicalSpec],
      BASSPass["generic_frame_derivation", "1", specHash, coreReceipt],
      BASSPass["exact_adapter_specialization", "1", specHash, adapters],
      BASSPass["typed_symir_v2_export", "1", BASSSHA256UTF8[BASSCanonicalJSON[coreReceipt]], <|"schema" -> "symir-v2-candidate-1", "spec_hash" -> specHash|>]
    }, {Lookup[#, "pass_name"] &, Lookup[#, "pass_version"] &}],
    "schema_version" -> "symir-v2-candidate-1",
    "selected_oracle" -> <|"spatial_scalar_curvature" -> BASSEncodeExact[derived["scalar_curvature3"]]|>,
    "spec_hash" -> specHash,
    "spec_id" -> canonicalSpec["spec_id"],
    "tensors" -> tensors
  |>
];

End[];
EndPackage[];
