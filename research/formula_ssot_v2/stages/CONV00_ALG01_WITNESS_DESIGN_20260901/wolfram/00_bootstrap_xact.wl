(* ::Package:: *)
ClearAll[BASSXActBootstrap];
Options[BASSXActBootstrap] = {
  "SourceURL" -> "https://xact.es/download/xAct_1.3.0.tgz",
  "ExpectedSHA256" -> "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be",
  "ArchivePath" -> Automatic
};
BASSXActBootstrap[OptionsPattern[]] := Module[
  {url=OptionValue["SourceURL"], expected=ToLowerCase@OptionValue["ExpectedSHA256"],
   supplied=OptionValue["ArchivePath"], root, archive, actual, extracted, capability},
  root=CreateDirectory@FileNameJoin[{$TemporaryDirectory,"bass-xact-"<>StringTake[CreateUUID[],8]}];
  archive=FileNameJoin[{root,"xAct_1.3.0.tgz"}];
  If[supplied===Automatic,URLDownload[url,archive],CopyFile[ExpandFileName[supplied],archive,OverwriteTarget->True]];
  actual=ToLowerCase@FileHash[archive,"SHA256","HexString"];
  If[actual=!=expected,Return@Failure["XActHashMismatch",<|"Expected"->expected,"Actual"->actual|>]];
  extracted=ExtractArchive[archive,root]; PrependTo[$Path,root];
  Get["xAct`xTensor`"]; Get["xAct`xCoba`"]; Get["xAct`xTras`"];
  ToExpression["xAct`xTensor`DefManifold[MALG01,3,{ia,ib,ic,id,ie,iff}]"];
  ToExpression["xAct`xTensor`DefCovD[DALG01[-ia],{\"|\",\"D\"}]"];
  capability=<|
    "ManifoldQ"->TrueQ@ToExpression["xAct`xTensor`ManifoldQ[MALG01]"],
    "CovDQ"->TrueQ@ToExpression["xAct`xTensor`CovDQ[DALG01]"],
    "RiemannxTensorQ"->TrueQ@ToExpression["xAct`xTensor`xTensorQ[RiemannDALG01]"],
    "RiccixTensorQ"->TrueQ@ToExpression["xAct`xTensor`xTensorQ[RicciDALG01]"],
    "TorsionxTensorQ"->TrueQ@ToExpression["xAct`xTensor`xTensorQ[TorsionDALG01]"]|>;
  If[!And@@Values[capability],Failure["XActCapabilityFailure",<|"Capability"->capability|>],
    <|"Status"->"PASS","SourceURL"->url,"ArchiveSHA256"->actual,
      "ExtractedEntryCount"->Length[extracted],"InstallParent"->root,
      "Packages"->{"xTensor","xCoba","xTras"},"Capability"->capability|>]
];
