(* ::Package:: *)

BeginPackage["BASS`Geometry`"];

SelectW2CanonicalBackend::usage =
 "SelectW2CanonicalBackend[] selects and records the deterministic W2 tensor canonicalization backend.";
W2CanonicalBackendReceipt::usage =
 "W2CanonicalBackendReceipt[] returns the canonicalization selection receipt.";
W2Canonicalize::usage =
 "W2Canonicalize[expr] canonicalizes an xTensor expression using the recorded W2 backend.";

Begin["`Private`"];

ClearAll[SelectW2CanonicalBackend, W2CanonicalBackendReceipt,
 W2Canonicalize, $w2CanonicalBackendReceipt];

$w2CanonicalBackendReceipt = Missing["NotSelected"];

SelectW2CanonicalBackend[] := Module[{loaded},
 loaded = MemberQ[$Packages, "xAct`xTensor`"] &&
   MemberQ[$Packages, "xAct`xPerm`"];
 If[!TrueQ[loaded],
  $w2CanonicalBackendReceipt = <|
    "schema_version" -> "1.0.0",
    "status" -> "BLOCKED",
    "reason" -> "XACT_XTENSOR_OR_XPERM_NOT_LOADED",
    "selected_backend" -> "none",
    "external_accelerator_selected" -> False,
    "selection_is_explicit" -> True|>;
  Return[$w2CanonicalBackendReceipt]
 ];

 (* W2 is a symbolic-authority lane.  It deliberately uses xPerm's
    pure-Wolfram canonicalizer so the formula identity does not depend on a
    session-specific external MathLink executable. *)
 xAct`xPerm`$xpermQ = False;
 $w2CanonicalBackendReceipt = <|
   "schema_version" -> "1.0.0",
   "status" -> "PASS",
   "reason" -> "DETERMINISTIC_HEADLESS_AUTHORITY_POLICY",
   "selected_backend" -> "pure-wolfram",
   "external_xperm_package_loaded" ->
    MemberQ[$Packages, "xAct`xPerm`"],
   "external_accelerator_selected" -> False,
   "selection_is_explicit" -> True,
   "xperm_q_after_selection" -> xAct`xPerm`$xpermQ,
   "claim_boundary" ->
    "CANONICALIZATION_BACKEND_ONLY_NO_TENSOR_OR_PHYSICS_AUDIT"|>;
 $w2CanonicalBackendReceipt
];

W2CanonicalBackendReceipt[] :=
 If[AssociationQ[$w2CanonicalBackendReceipt],
  $w2CanonicalBackendReceipt,
  SelectW2CanonicalBackend[]
 ];

W2Canonicalize[expr_] := Module[{receipt, result},
 receipt = W2CanonicalBackendReceipt[];
 If[Lookup[receipt, "status", "BLOCKED"] =!= "PASS",
  Return[Failure["CanonicalBackendUnavailable", receipt]]
 ];
 result = Catch[
   Quiet@Check[
     Block[{xAct`xPerm`$xpermQ = False},
      xAct`xTensor`ToCanonical[expr]
     ],
     $Failed
   ],
   _,
   Function[{value, tag},
    Failure["CanonicalizationThrow", <|
      "value" -> ToString[InputForm[value]],
      "tag" -> ToString[InputForm[tag]]|>]
   ]
  ];
 If[result === Null || result === $Failed,
  Failure["CanonicalizationFailed", <|
    "expression" -> ToString[InputForm[expr]],
    "backend" -> receipt|>],
  result
 ]
];

End[];
EndPackage[];
