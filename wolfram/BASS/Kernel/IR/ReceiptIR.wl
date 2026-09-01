(* ::Package:: *)

BeginPackage["BASS`IR`"];

StageStatusVocabulary::usage = "StageStatusVocabulary[] returns the fail-closed status vocabulary.";
MakeStageReceipt::usage = "MakeStageReceipt[stageID,status,tests,provenance,claims] constructs a receipt.";
StageReceiptQ::usage = "StageReceiptQ[receipt] validates a stage receipt.";

Begin["`Private`"];

ClearAll[StageStatusVocabulary, MakeStageReceipt, StageReceiptQ];
StageStatusVocabulary[] := {"PASS", "FAIL", "BLOCKED", "NOT_RUN"};
MakeStageReceipt[stageID_String, status_String, tests_Association,
 provenance_Association, claims_Association] := BASS`IR`CanonicalizeData @ <|
 "schema_version" -> "1.0.0",
 "program_id" -> "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
 "stage_id" -> stageID, "status" -> status, "tests" -> tests,
 "provenance" -> provenance, "claims" -> claims|>;
StageReceiptQ[receipt_Association] := And[
 Lookup[receipt, "schema_version", None] === "1.0.0",
 Lookup[receipt, "program_id", None] === "BASS-MASTER-SSOT-V2-WOLFRAM-XACT-20260901",
 StringQ[Lookup[receipt, "stage_id", None]],
 MemberQ[StageStatusVocabulary[], Lookup[receipt, "status", None]],
 AssociationQ[Lookup[receipt, "tests", None]],
 AssociationQ[Lookup[receipt, "provenance", None]],
 AssociationQ[Lookup[receipt, "claims", None]]];
StageReceiptQ[_] := False;

End[];
EndPackage[];
