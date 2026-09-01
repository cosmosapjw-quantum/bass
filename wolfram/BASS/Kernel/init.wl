(* ::Package:: *)

Module[{root, sources},
 root = DirectoryName[$InputFileName];
 sources = {
   FileNameJoin[{root, "Authority", "Environment.wl"}],
   FileNameJoin[{root, "Authority", "Conventions.wl"}],
   FileNameJoin[{root, "Authority", "Dimensions.wl"}],
   FileNameJoin[{root, "Authority", "Provenance.wl"}],
   FileNameJoin[{root, "IR", "CanonicalSerialization.wl"}],
   FileNameJoin[{root, "IR", "ExactScalarAST.wl"}],
   FileNameJoin[{root, "IR", "EquationIR.wl"}],
   FileNameJoin[{root, "IR", "ReceiptIR.wl"}],
   FileNameJoin[{root, "Bianchi", "BranchPredicates.wl"}],
   FileNameJoin[{root, "Bianchi", "BianchiTypeSpec.wl"}],
   FileNameJoin[{root, "Bianchi", "WitnessRegistry.wl"}],
   FileNameJoin[{root, "Geometry", "StructureConstants.wl"}],
   FileNameJoin[{root, "Geometry", "CartanConnection.wl"}],
   FileNameJoin[{root, "Geometry", "RiemannConventionAdapter.wl"}]
 };
 Scan[Get, sources];
]
