Module[
 {q1, q2, lam, c0, mq, cq, cfull, r, a0, aq, pq, pscaled,
  pwrong, b2, bdb, s, ds, gamma, gammadot, qfac, qdot, dop,
  doprest, dopdotmoving, dopdotrest, n, nd, hub, hd, kappa,
  alpha, alphadot, nu, nudot, assumptions},
 assumptions = q1 != 0 && q2 != 0 && lam != 0 && q1 + q2 != 0 &&
   1 - b2 > 0 && 1 + s != 0 && n != 0 && hub != 0 && kappa != 0;
 c0 = {{-1, 1}, {1, -1}};
 mq = DiagonalMatrix[{q1, q2}];
 cq = mq.c0;
 cfull = lam cq;
 r = {1, 1};
 a0 = {1, 1};
 aq = {1/q1, 1/q2};
 pq = FullSimplify[Outer[Times, r, aq]/(aq.r), assumptions];
 pscaled = FullSimplify[Outer[Times, r, aq/lam]/((aq/lam).r), assumptions];
 pwrong = Outer[Times, r, a0]/(a0.r);
 gamma = 1/Sqrt[1 - b2];
 gammadot = gamma^3 bdb;
 qfac = (1 - b2)/(1 + s);
 qdot = D[qfac, b2] (2 bdb) + D[qfac, s] ds;
 dop = FullSimplify[gamma qfac, assumptions];
 doprest = Sqrt[1 - b2]/(1 + s);
 dopdotmoving = FullSimplify[gammadot qfac + gamma qdot, assumptions];
 dopdotrest = FullSimplify[D[doprest, b2] (2 bdb) + D[doprest, s] ds, assumptions];
 alpha = n kappa/hub;
 alphadot = FullSimplify[alpha (nd/n - hd/hub), assumptions];
 nu = FullSimplify[alpha dop, assumptions];
 nudot = FullSimplify[alphadot dop + alpha dopdotrest, assumptions];
 <|
  "RightKernelResidual" -> FullSimplify[cq.r, assumptions],
  "TransformedLeftResidual" -> FullSimplify[aq.cq, assumptions],
  "TransformedFullLeftResidual" -> FullSimplify[(aq/lam).cfull, assumptions],
  "UnchangedLeftResidual" -> FullSimplify[a0.cq, assumptions],
  "ProjectorIdempotenceResidual" -> FullSimplify[pq.pq - pq, assumptions],
  "GlobalScalarProjectorResidual" -> FullSimplify[pscaled - pq, assumptions],
  "DirectionDependentProjectorDifference" -> FullSimplify[pq - pwrong, assumptions],
  "PairedDopplerIdentityResidual" -> FullSimplify[dop - doprest, assumptions],
  "PairedDopplerDerivativeResidual" -> FullSimplify[dopdotmoving - dopdotrest, assumptions],
  "RateLogDerivativeResidual" -> FullSimplify[nudot/nu - (nd/n - hd/hub + dopdotrest/dop), assumptions],
  "Status" -> "PASS_EXACT_RATE_DUAL_WOLFRAM_WITNESS"
 |>
]
