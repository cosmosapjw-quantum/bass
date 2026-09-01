Module[{coords, dim, metric, inverseMetric, christoffel, einsteinResidual,
  divergenceCoordinate, divergenceFrame, h1, h2, h3, h, sigma1,
  expectedTime, expectedLongitudinal, residualTime, residualLongitudinal},
 coords = {s, x, y, z};
 dim = 4;
 metric = DiagonalMatrix[{
   -1,
   a1[s]^2,
   a2[s]^2 Exp[2 A x],
   a3[s]^2 Exp[2 A x]}];
 inverseMetric = FullSimplify[Inverse[metric]];
 christoffel = Table[
   1/2 Sum[inverseMetric[[mu, lambda]] (
      D[metric[[lambda, nu]], coords[[rho]]] +
      D[metric[[lambda, rho]], coords[[nu]]] -
      D[metric[[nu, rho]], coords[[lambda]]]),
     {lambda, dim}],
   {mu, dim}, {nu, dim}, {rho, dim}];
 einsteinResidual = ConstantArray[0, {dim, dim}];
 einsteinResidual[[1, 1]] = F[s];
 einsteinResidual[[1, 2]] = C[s]/a1[s];
 einsteinResidual[[2, 1]] = C[s]/a1[s];
 divergenceCoordinate = Table[
   FullSimplify[Sum[
     D[einsteinResidual[[mu, nu]], coords[[mu]]] +
     Sum[christoffel[[mu, mu, lambda]] einsteinResidual[[lambda, nu]],
       {lambda, dim}] +
     Sum[christoffel[[nu, mu, lambda]] einsteinResidual[[mu, lambda]],
       {lambda, dim}],
     {mu, dim}]],
   {nu, dim}];
 divergenceFrame = {
   divergenceCoordinate[[1]],
   a1[s] divergenceCoordinate[[2]],
   a2[s] Exp[A x] divergenceCoordinate[[3]],
   a3[s] Exp[A x] divergenceCoordinate[[4]]};
 h1 = a1'[s]/a1[s];
 h2 = a2'[s]/a2[s];
 h3 = a3'[s]/a3[s];
 h = (h1 + h2 + h3)/3;
 sigma1 = h1 - h;
 expectedTime = F'[s] + 3 h F[s] + 2 A C[s]/a1[s];
 expectedLongitudinal = C'[s] + (4 h + sigma1) C[s];
 residualTime = FullSimplify[divergenceFrame[[1]] - expectedTime];
 residualLongitudinal = FullSimplify[
   divergenceFrame[[2]] - expectedLongitudinal];
 VerificationTest[residualTime, 0,
  TestID -> "BASS-BG02-METRIC-001-type-v-time-divergence"];
 VerificationTest[residualLongitudinal, 0,
  TestID -> "BASS-BG02-METRIC-002-type-v-longitudinal-divergence"];
 VerificationTest[FullSimplify[divergenceFrame[[{3, 4}]]], {0, 0},
  TestID -> "BASS-BG02-METRIC-003-type-v-transverse-divergence"];
 VerificationTest[
  FreeQ[FullSimplify[divergenceFrame], x],
  True,
  TestID -> "BASS-BG02-METRIC-004-homogeneity"];
]
