(* ::Package:: *)

BeginPackage["BASS`Authority`"];

MakeProvenanceEnvelope::usage = "MakeProvenanceEnvelope[programID, stageID, source, inputs] creates provenance.";
ProvenanceEnvelopeQ::usage = "ProvenanceEnvelopeQ[envelope] validates provenance.";

Begin["`Private`"];

ClearAll[MakeProvenanceEnvelope, ProvenanceEnvelopeQ];

MakeProvenanceEnvelope[programID_String, stageID_String,
 source_Association, inputs_Association] := <|
 "schema_version" -> "1.0.0", "program_id" -> programID,
 "stage_id" -> stageID,
 "generated_at_utc" -> DateString[TimeZoneConvert[Now, 0], "ISODateTime"],
 "wolfram_version" -> $Version, "system_id" -> $SystemID,
 "source" -> source, "inputs" -> inputs|>;

ProvenanceEnvelopeQ[envelope_Association] := And[
 Lookup[envelope, "schema_version", None] === "1.0.0",
 StringQ[Lookup[envelope, "program_id", None]],
 StringQ[Lookup[envelope, "stage_id", None]],
 StringQ[Lookup[envelope, "generated_at_utc", None]],
 StringQ[Lookup[envelope, "wolfram_version", None]],
 StringQ[Lookup[envelope, "system_id", None]],
 AssociationQ[Lookup[envelope, "source", None]],
 AssociationQ[Lookup[envelope, "inputs", None]]
];
ProvenanceEnvelopeQ[_] := False;

End[];
EndPackage[];
