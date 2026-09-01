(* ::Package:: *)

BeginPackage["BASS`Bianchi`"];

BianchiWitnessLabels::usage =
 "BianchiWitnessLabels[] returns the ordered ALG-01 witness keys.";
BianchiWitness::usage =
 "BianchiWitness[key] returns the canonical exact witness state for a supported ALG-01 key.";
WitnessRegistry::usage =
 "WitnessRegistry[] returns the ordered association of all canonical ALG-01 witnesses.";
BianchiWitnessQ::usage =
 "BianchiWitnessQ[key,witness] validates a canonical witness against its branch predicate.";
ExceptionalVIm1over9ConstraintResidual::usage =
 "ExceptionalVIm1over9ConstraintResidual[witness] returns the determinant and momentum-constraint residuals.";
ExceptionalShearSurvivalQ::usage =
 "ExceptionalShearSurvivalQ[witness] checks nonzero Sigma13 and Sigma23 in the exceptional constraint surface.";

Begin["`Private`"];

ClearAll[zeroQ, nonzeroQ, vector3Q, matrix3Q, symmetric3Q,
 BianchiWitnessLabels, witnessRegistry, BianchiWitness, WitnessRegistry,
 commonWitnessQ, BianchiWitnessQ, ExceptionalVIm1over9ConstraintResidual,
 ExceptionalShearSurvivalQ];

zeroQ[x_] := TrueQ[PossibleZeroQ[Together[x]]];
nonzeroQ[x_] := TrueQ[FullSimplify[x != 0]];
vector3Q[x_] := ListQ[x] && Dimensions[x] === {3};
matrix3Q[x_] := MatrixQ[x] && Dimensions[x] === {3, 3};
symmetric3Q[x_] := matrix3Q[x] && TrueQ[FullSimplify[x == Transpose[x]]];

BianchiWitnessLabels[] := {"I", "II", "V", "IX", "VI_-1/9"};

witnessRegistry[] := <|
 "I" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "I", "a" -> {0, 0, 0},
   "n" -> ConstantArray[0, {3, 3}],
   "sigma" -> ConstantArray[0, {3, 3}],
   "claim_boundary" -> "CANONICAL_EXACT_WITNESS_ONLY"|>,
 "II" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "II", "a" -> {0, 0, 0},
   "n" -> DiagonalMatrix[{1, 0, 0}],
   "sigma" -> ConstantArray[0, {3, 3}],
   "claim_boundary" -> "CANONICAL_EXACT_WITNESS_ONLY"|>,
 "V" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "V", "a" -> {1, 0, 0},
   "n" -> ConstantArray[0, {3, 3}],
   "sigma" -> ConstantArray[0, {3, 3}],
   "claim_boundary" -> "CANONICAL_EXACT_WITNESS_ONLY"|>,
 "IX" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "IX", "a" -> {0, 0, 0},
   "n" -> IdentityMatrix[3],
   "sigma" -> ConstantArray[0, {3, 3}],
   "claim_boundary" -> "CANONICAL_EXACT_WITNESS_ONLY"|>,
 "VI_-1/9" -> <|
   "schema_version" -> "1.0.0", "stage_id" -> "ALG_01",
   "registry_key" -> "VI_-1/9", "public_label" -> "VI_h",
   "a" -> {1, 0, 0},
   "n" -> {{0, 0, 0}, {0, 2, 3}, {0, 3, 0}},
   "sigma" -> {{0, 0, 2}, {0, 0, 3}, {2, 3, 0}},
   "free_shear_slots" -> {"sigma_13", "sigma_23"},
   "claim_boundary" -> "CANONICAL_EXACT_WITNESS_ONLY"|>
|>;

BianchiWitness[key_String] :=
 Lookup[witnessRegistry[], key,
  Failure["UnsupportedBianchiWitness", <|"key" -> key|>]];
BianchiWitness[_] := Failure["InvalidBianchiWitnessKey", <||>];

WitnessRegistry[] := witnessRegistry[];

commonWitnessQ[key_String, witness_Association] := Module[{a, n, sigma},
 a = Lookup[witness, "a", Missing["KeyAbsent", "a"]];
 n = Lookup[witness, "n", Missing["KeyAbsent", "n"]];
 sigma = Lookup[witness, "sigma", Missing["KeyAbsent", "sigma"]];
 And[
  Lookup[witness, "schema_version", None] === "1.0.0",
  Lookup[witness, "stage_id", None] === "ALG_01",
  Lookup[witness, "registry_key", None] === key,
  Lookup[witness, "claim_boundary", None] ===
   "CANONICAL_EXACT_WITNESS_ONLY",
  vector3Q[a], symmetric3Q[n], symmetric3Q[sigma],
  zeroQ[Tr[sigma]], AllTrue[Flatten[Dot[n, a]], zeroQ]
 ]
];

ExceptionalVIm1over9ConstraintResidual[witness_Association] :=
 Module[{a, n, sigma, A, n22, n23, n33, sigma12, sigma13},
  a = Lookup[witness, "a", ConstantArray[Indeterminate, 3]];
  n = Lookup[witness, "n", ConstantArray[Indeterminate, {3, 3}]];
  sigma = Lookup[witness, "sigma", ConstantArray[Indeterminate, {3, 3}]];
  If[! vector3Q[a] || ! matrix3Q[n] || ! matrix3Q[sigma],
   Return[Failure["InvalidExceptionalWitness", <||>]]];
  A = a[[1]]; n22 = n[[2, 2]]; n23 = n[[2, 3]]; n33 = n[[3, 3]];
  sigma12 = sigma[[1, 2]]; sigma13 = sigma[[1, 3]];
  Together /@ {
    9 A^2 + n22 n33 - n23^2,
    n22 sigma12 + (n23 - 3 A) sigma13
  }
 ];
ExceptionalVIm1over9ConstraintResidual[_] :=
 Failure["InvalidExceptionalWitness", <||>];

ExceptionalShearSurvivalQ[witness_Association] := Module[{sigma, residual},
 sigma = Lookup[witness, "sigma", Missing["KeyAbsent", "sigma"]];
 residual = ExceptionalVIm1over9ConstraintResidual[witness];
 And[symmetric3Q[sigma], ! FailureQ[residual],
  AllTrue[residual, zeroQ], nonzeroQ[sigma[[1, 3]]],
  nonzeroQ[sigma[[2, 3]]]]
];
ExceptionalShearSurvivalQ[_] := False;

BianchiWitnessQ[key_String, witness_Association] := Module[
 {a, n, inertia, common},
 common = commonWitnessQ[key, witness];
 If[! TrueQ[common], Return[False]];
 a = witness["a"]; n = witness["n"];
 inertia = SymmetricInertia[n];
 Switch[key,
  "I",
   StructureClass[a] === "A" && MatrixRank[n] === 0,
  "II",
   StructureClass[a] === "A" && MatrixRank[n] === 1,
  "V",
   StructureClass[a] === "B" && MatrixRank[n] === 0,
  "IX",
   StructureClass[a] === "A" && MatrixRank[n] === 3 &&
    MemberQ[{{3, 0, 0}, {0, 3, 0}}, inertia],
  "VI_-1/9",
   StructureClass[a] === "B" &&
    AllTrue[a[[{2, 3}]], zeroQ] && nonzeroQ[a[[1]]] &&
    AllTrue[Flatten[n[[1 ;; 1]]], zeroQ] &&
    AllTrue[n[[All, 1]], zeroQ] &&
    TrueQ[FullSimplify[TransverseDeterminant[n] < 0]] &&
    TrueQ[SignedH[a, n] === -1/9] && ExceptionalShearSurvivalQ[witness],
  _, False]
];
BianchiWitnessQ[_, _] := False;

End[];
EndPackage[];
