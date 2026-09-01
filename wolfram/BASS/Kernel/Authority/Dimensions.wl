(* ::Package:: *)

BeginPackage["BASS`Authority`"];

DimensionRegistry::usage = "DimensionRegistry[] returns exact base-dimension exponent vectors.";
DimensionRegistryQ::usage = "DimensionRegistryQ[registry] validates the dimension registry.";

Begin["`Private`"];

ClearAll[DimensionRegistry, DimensionRegistryQ, exponentVectorQ];

exponentVectorQ[assoc_Association, bases_List] := And[
 Sort[Keys[assoc]] === Sort[bases],
 AllTrue[Values[assoc], IntegerQ[#] || RationalQ[#] &]
];

DimensionRegistry[] := Module[{z, bases},
 bases = {"L", "M", "T", "Theta"};
 z = AssociationThread[bases, ConstantArray[0, Length[bases]]];
 <|"schema_version" -> "1.1.0", "base_dimensions" -> bases,
  "quantities" -> <|
   "dimensionless" -> z,
   "n_a" -> z,
   "h_ab" -> z,
   "epsilon3_abc" -> z,
   "c" -> <|"L" -> 1, "M" -> 0, "T" -> -1, "Theta" -> 0|>,
   "hbar" -> <|"L" -> 2, "M" -> 1, "T" -> -1, "Theta" -> 0|>,
   "k_B" -> <|"L" -> 2, "M" -> 1, "T" -> -2, "Theta" -> -1|>,
   "G" -> <|"L" -> 3, "M" -> -1, "T" -> -2, "Theta" -> 0|>,
   "H_geom" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "A_a" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "K_ab" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "sigma_ab" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "aB_a" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "nB_ab" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "Omega_triad_a" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "kappa" -> <|"L" -> -1, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "R3_abcd" -> <|"L" -> -2, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "R3_scalar" -> <|"L" -> -2, "M" -> 0, "T" -> 0, "Theta" -> 0|>,
   "photon_energy" -> <|"L" -> 2, "M" -> 1, "T" -> -2, "Theta" -> 0|>,
   "energy_density" -> <|"L" -> -1, "M" -> 1, "T" -> -2, "Theta" -> 0|>,
   "temperature" -> <|"L" -> 0, "M" -> 0, "T" -> 0, "Theta" -> 1|>|>|>
];

DimensionRegistryQ[registry_Association] := Module[{bases, quantities},
 bases = Lookup[registry, "base_dimensions", Missing["KeyAbsent"]];
 quantities = Lookup[registry, "quantities", Missing["KeyAbsent"]];
 And[MemberQ[{"1.0.0", "1.1.0"}, Lookup[registry, "schema_version", None]],
  ListQ[bases], DuplicateFreeQ[bases], AssociationQ[quantities],
  AllTrue[Values[quantities], exponentVectorQ[#, bases] &],
  Lookup[Lookup[quantities, "H_geom", <||>], "L", None] === -1,
  Lookup[Lookup[quantities, "A_a", <||>], "L", None] === -1,
  Lookup[Lookup[quantities, "K_ab", <||>], "L", None] === -1,
  Lookup[Lookup[quantities, "R3_scalar", <||>], "L", None] === -2,
  Lookup[Lookup[quantities, "kappa", <||>], "L", None] === -1]
];
DimensionRegistryQ[_] := False;

End[];
EndPackage[];
