(* ::Package:: *)

(* BG-02 pure-Wolfram design oracle.
   This is an independent algebraic oracle, not a native xAct projection replay. *)

ClearAll["Global`*"];

eps3[i_, j_, k_] := Signature[{i, j, k}];

pstf[m_] := FullSimplify[
  (m + Transpose[m])/2
  - IdentityMatrix[3] Tr[(m + Transpose[m])/2]/3
];

(* Off-shell scalar rate identities. *)
ham = (r3 + 6 h^2 - s2)/2 - lam - kg rho;
fTrace = -r3/12 - 3 h^2/2 - s2/4 + acc/3 + lam/2 - kg p/2;
fADM = -r3/3 - 3 h^2 + acc/3 + kg (rho - p)/2 + lam;
fRay = -h^2 - s2/3 + acc/3 - kg (rho + 3 p)/6 + lam/3;

rateResiduals = FullSimplify[{
  fADM - fTrace + ham/2,
  fTrace - fRay + ham/6,
  fADM - fRay + 2 ham/3
}];

deSitter = FullSimplify[
  {ham, fTrace, fADM, fRay}
  /. {r3 -> 0, s2 -> 0, rho -> 0, p -> 0,
      acc -> 0, lam -> 3 h^2}
];

kasner = FullSimplify[
  {ham, fTrace, fADM, fRay}
  /. {r3 -> 0, h -> 1/(3 tau), s2 -> 2/(3 tau^2),
      rho -> 0, p -> 0, acc -> 0, lam -> 0}
];

flatFLRW = FullSimplify[
  {fADM, fRay}
  /. {r3 -> 0, s2 -> 0, acc -> 0,
      h^2 -> (kg rho + lam)/3}
];

(* PSTF K/sigma algebra. *)
sigma = {
  {s11, s12, s13},
  {s12, s22, s23},
  {s13, s23, -s11 - s22}
};
K = h IdentityMatrix[3] + sigma;

kQuadraticResidual = FullSimplify[
  pstf[3 h K - 2 K.K] - (-h sigma - 2 pstf[sigma.sigma])
];

projectedVsLieResidual = FullSimplify[
  pstf[2 sigma.K] - (2 h sigma + 2 pstf[sigma.sigma])
];

(* BASS canonical connection storage: generated[[gamma,alpha,beta]]. *)
av = {a1, a2, a3};
nm = {
  {n11, n12, n13},
  {n12, n22, n23},
  {n13, n23, n33}
};

cgen[ga_, al_, be_] :=
  Sum[eps3[al, be, de] nm[[de, ga]], {de, 3}]
  + av[[al]] KroneckerDelta[ga, be]
  - av[[be]] KroneckerDelta[ga, al];

ggen[ga_, al_, be_] :=
  (cgen[ga, al, be] - cgen[al, be, ga] + cgen[be, ga, al])/2;

(* Curvature lock: locked[[alpha,beta,gamma]] = generated[[gamma,alpha,beta]]. *)
glock[al_, be_, ga_] := ggen[ga, al, be];

riemannFrom[gamma_] := Array[
  Function[{al, be, ga, de},
    Expand@Sum[
      gamma[be, ga, mu] gamma[al, mu, de]
      - gamma[al, ga, mu] gamma[be, mu, de]
      - cgen[mu, al, be] gamma[mu, ga, de],
      {mu, 3}
    ]
  ],
  {3, 3, 3, 3}
];

ricciFrom[r_] := Array[
  Function[{ga, be},
    Expand@Sum[r[[al, be, ga, al]], {al, 3}]
  ],
  {3, 3}
];

rGood = riemannFrom[glock];
ricGood = ricciFrom[rGood];
r3Good = FullSimplify[Tr[ricGood]];

(* Deliberate negative control: canonical storage is falsely read as locked. *)
gbad[al_, be_, ga_] := ggen[al, be, ga];
rBad = riemannFrom[gbad];
r3Bad = FullSimplify[Tr[ricciFrom[rBad]]];

r3Compact = -6 av.av - Tr[nm.nm] + Tr[nm]^2/2;
constraints = Expand /@ (nm.av);
vars = {a1, a2, a3, n11, n12, n13, n22, n23, n33};
r3Remainder = FullSimplify[
  Last@PolynomialReduce[Expand[r3Good - r3Compact], constraints, vars]
];

witnessRules = <|
  "I" -> {a1 -> 0, a2 -> 0, a3 -> 0,
    n11 -> 0, n12 -> 0, n13 -> 0, n22 -> 0, n23 -> 0, n33 -> 0},
  "V" -> {a1 -> 1, a2 -> 0, a3 -> 0,
    n11 -> 0, n12 -> 0, n13 -> 0, n22 -> 0, n23 -> 0, n33 -> 0},
  "II" -> {a1 -> 0, a2 -> 0, a3 -> 0,
    n11 -> 1, n12 -> 0, n13 -> 0, n22 -> 0, n23 -> 0, n33 -> 0},
  "IX" -> {a1 -> 0, a2 -> 0, a3 -> 0,
    n11 -> 1, n12 -> 0, n13 -> 0, n22 -> 1, n23 -> 0, n33 -> 1}
|>;

witnessGood = Map[FullSimplify[r3Good /. #] &, witnessRules];
witnessBad = Map[FullSimplify[r3Bad /. #] &, witnessRules];

(* Homogeneous sigma divergence and exceptional carrier. *)
sm = {
  {S11, S12, S13},
  {S12, S22, S23},
  {S13, S23, -S11 - S22}
};

divSigma = FullSimplify@Table[
  Sum[
    -glock[b, i, d] sm[[d, b]]
    -glock[b, b, d] sm[[i, d]],
    {b, 3}, {d, 3}
  ],
  {i, 3}
];

compactDivSigma = FullSimplify@Table[
  -3 Sum[av[[b]] sm[[i, b]], {b, 3}]
  - Sum[
      eps3[i, m, v] nm[[m, b]] sm[[b, v]],
      {m, 3}, {v, 3}, {b, 3}
    ],
  {i, 3}
];

exceptionalRules = {
  a1 -> A, a2 -> 0, a3 -> 0,
  n11 -> 0, n12 -> 0, n13 -> 0,
  n22 -> N22, n23 -> N23, n33 -> N33
};

exceptionalThird = FullSimplify[divSigma[[3]] /. exceptionalRules];
exceptionalExpected = N22 S12 + (N23 - 3 A) S13;

checks = <|
  "rate_identities" -> And @@ Thread[rateResiduals == {0, 0, 0}],
  "de_sitter" -> And @@ Thread[deSitter == {0, 0, 0, 0}],
  "kasner" -> And @@ Thread[
    kasner == {0, -1/(3 tau^2), -1/(3 tau^2), -1/(3 tau^2)}
  ],
  "flat_flrw" -> And @@ Thread[
    flatFLRW == {-kg (rho + p)/2, -kg (rho + p)/2}
  ],
  "pstf_K_algebra" -> kQuadraticResidual == ConstantArray[0, {3, 3}],
  "lie_projected_relation" ->
    projectedVsLieResidual == ConstantArray[0, {3, 3}],
  "R3_compact_modulo_n_dot_a" -> r3Remainder == 0,
  "R3_good_witnesses" -> witnessGood ==
    <|"I" -> 0, "V" -> -6, "II" -> -1/2, "IX" -> 3/2|>,
  "wrong_order_negative_control" -> witnessBad ==
    <|"I" -> 0, "V" -> 4, "II" -> 3/2, "IX" -> 3/2|>,
  "homogeneous_sigma_divergence" ->
    FullSimplify[divSigma - compactDivSigma] == {0, 0, 0},
  "exceptional_momentum_carrier" ->
    FullSimplify[exceptionalThird - exceptionalExpected] == 0
|>;

Print@ExportString[
  <|
    "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
    "checks" -> checks,
    "good_R3_witnesses" -> Map[ToString[InputForm[#]] &, witnessGood],
    "wrong_order_R3_witnesses" -> Map[ToString[InputForm[#]] &, witnessBad],
    "exceptional_momentum_component_3" ->
      ToString[InputForm[exceptionalThird]],
    "claim_boundary" ->
      "PURE_WOLFRAM_ALGEBRA_ONLY_NOT_NATIVE_XACT_BG02_REPLAY"
  |>,
  "RawJSON"
];
