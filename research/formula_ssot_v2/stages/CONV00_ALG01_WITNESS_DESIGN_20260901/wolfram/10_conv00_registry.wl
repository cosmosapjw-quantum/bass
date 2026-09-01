(* ::Package:: *)
ClearAll[BASSZeroQ,CONV00Registry,TimeRateToRayRate,RayRateToTimeRate,ValidateCONV00];
BASSZeroQ[x_]:=If[AtomQ[x],TrueQ[x===0],Flatten[x]===ConstantArray[0,Length@Flatten[x]]];
CONV00Registry[]:=<|
 "MetricSignature"->"(-,+,+,+)","SpatialOrientation"->"epsilon_123=+1",
 "PhotonPropagationDirection"->"e^a","ObservedSkyDirection"->"n_hat^a=-e^a",
 "ExplicitConstants"->{"c","hbar","k_B","G"},
 "RateTypes"-><|"TimeRate"->"s^-1","RayLengthRate"->"m^-1"|>,
 "Frames"->{"normal","matter_or_hydrogen","electron_rest","local_observer"},
 "Nonidentifications"->{"aB is not physical acceleration","OmegaTriad is not vorticity","global/electron tilt is not local boost"}|>;
TimeRateToRayRate[q_,c_]:=q/c; RayRateToTimeRate[q_,c_]:=c q;
ValidateCONV00[]:=Module[{c=Unique["c$"],qt=Unique["qt$"],ql=Unique["ql$"],r},
 r=<|"TimeToLengthToTime"->FullSimplify[RayRateToTimeRate[TimeRateToRayRate[qt,c],c]-qt,Assumptions->c>0],
      "LengthToTimeToLength"->FullSimplify[TimeRateToRayRate[RayRateToTimeRate[ql,c],c]-ql,Assumptions->c>0]|>;
 <|"Status"->If[And@@Values[Map[BASSZeroQ,r]],"PASS","FAIL"],"Registry"->CONV00Registry[],"Residuals"->r,"ResidualZeroQ"->Map[BASSZeroQ,r]|>];
