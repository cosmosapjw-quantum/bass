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
   FileNameJoin[{root, "Geometry", "StructureConstants.wl"}],
   FileNameJoin[{root, "Geometry", "FrameCovariance.wl"}],
   FileNameJoin[{root, "Geometry", "CanonicalizationBackend.wl"}],
   FileNameJoin[{root, "Geometry", "Abstract1Plus3.wl"}],
   FileNameJoin[{root, "Geometry", "Abstract1Plus3Receipt.wl"}],
   FileNameJoin[{root, "Bianchi", "TypeSpec.wl"}],
   FileNameJoin[{root, "Bianchi", "Witnesses.wl"}],
   FileNameJoin[{root, "Geometry", "LeviCivitaConnection.wl"}],
   FileNameJoin[{root, "Geometry", "ONFConnectionCurvature.wl"}],
   FileNameJoin[{root, "Geometry", "XCobaCurvatureWitnesses.wl"}],
   FileNameJoin[{root, "IR", "SemanticFormulaExport.wl"}],
   FileNameJoin[{root, "IR", "RECRelationClassification.wl"}],
   FileNameJoin[{root, "IR", "RECRelationClassificationValidationFix1.wl"}]
 };
 Scan[Get, sources];
]
