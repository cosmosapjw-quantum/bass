{kernelWall, kernelValue}=AbsoluteTiming[
 {kernelCPU, residuals}=Timing[
  sig={sx,sy,-sx-sy}; pr={px,py,pz}; rg=Total[pr]; ss=Total[sig^2];
  ch=3 hh^2-ss/2-rd-rg;
  dh=-hh^2-ss/3-(rd+2 rg)/6;
  ds=-3 hh sig+pr-rg/3;
  directional=FullSimplify[dh+ds+3 hh (hh+sig)-rd/2-pr-2 ch/3];
  ellCoeff=8 Pi/(3 n0 lam^3);
  exposure=ellCoeff(Exp[3 aa[t]]-1);
  sourceDen=gg-(gg+1)xx;
  down=ff0(1+ff)xx/sourceDen;
  up=ff0 gg(1-xx)ff/sourceDen;
  feq=xx/sourceDen;
  implicit=gg vv-(gg+1)x0(1-Exp[-vv]);
  photonEnergy=eLine Sqrt[Sum[nn[i]^2 Exp[-2(aa[t]-ab+bb[i][t]-bbb[i])],{i,1,3}]];
  photonK=Table[nn[i]Exp[-(aa[t]-ab)-(bb[i][t]-bbb[i])],{i,1,3}];
  energyDerivative=FullSimplify[D[photonEnergy,t]/photonEnergy+
   aa'[t]+Sum[bb[i]'[t]photonK[[i]]^2,{i,1,3}]/Total[photonK^2],
   Assumptions->eLine>0 && Element[{aa[t],ab,bb[1][t],bb[2][t],bb[3][t],bbb[1],bbb[2],bbb[3],nn[1],nn[2],nn[3]},Reals] && Total[photonK^2]>0];
  <|"DirectionalExpansionOffConstraint"->directional,
    "ExposureDerivative"->FullSimplify[D[exposure,t]-8 Pi aa'[t]Exp[3 aa[t]]/(n0 lam^3)],
    "LogExposureDerivative"->FullSimplify[D[implicit,vv]-(gg-(gg+1)x0 Exp[-vv])],
    "ComovingAtoms"->FullSimplify[Exp[3 al] n0 Exp[-3 al]-n0],
    "ComovingExcitationPhotonCount"->FullSimplify[Exp[3 al](n0 Exp[-3 al]x0 Exp[-vv]+n0 Exp[-3 al]x0(1-Exp[-vv]))-n0 x0],
    "FiniteExchangeEnergy"->Expand[-eLine dn+eLine dn],
    "GrossToNetFace"->FullSimplify[down-up-ff0(feq-ff)],
    "GrossUpMinusIncidentFlux"->FullSimplify[up-ff0 ff-ff0 ff feq],
    "SourceTimeUnits"->FullSimplify[(kap len^3 edot/cc)(cc dt/len)-kap len^2 edot dt],
    "CohortEnergyDerivative"->energyDerivative,
    "PhotonPressureTrace"->FullSimplify[Sum[den photonK[[i]]^2/Sqrt[Total[photonK^2]],{i,1,3}]-den Sqrt[Total[photonK^2]]]
  |>
 ];
 <|"Residuals"->residuals,"KernelCPUSeconds"->kernelCPU|>
];
<|"Version"->$Version,"Result"->kernelValue,"KernelWallSeconds"->kernelWall,
 "SupportLowerBound"->N[(3/5)/(1+1/50)^3,20]|>
