# Actual computed projections

Expressions below are from repair3 AP_FINAL. Only the common BASS`Research`AP1`Private` context prefix is removed for display; raw strings remain in execution/repair3/ap-final.json. No expected expression was substituted.

## Hamiltonian

```wolfram
-lambda - (KK[-ia, -ib]*KK[ia, ib])/2 + (KK[ia, -ia]*KK[ib, -ib])/2 - kappaG*rho[] + ZZ[ia, -ia]/2
```

## Momentum

```wolfram
DK[-ia, ib, -ib] - DK[ib, -ia, -ib] - kappaG*flux[-ia]
```

## SpatialTrace

```wolfram
lambda + (2*acc[-ia]*acc[ia])/3 + (2*DA[ia, -ia])/3 + (5*KK[-ia, -ib]*KK[ia, ib])/6 - (KK[ia, -ia]*KK[ib, -ib])/6 - (2*LL[ia, -ia])/3 - kappaG*press[] - ZZ[ia, -ia]/6
```

## SpatialPSTF

```wolfram
-(acc[-ia]*acc[-ib]) - DA[-ia, -ib] - 2*KK[-ia, ic]*KK[-ib, -ic] + KK[-ia, -ib]*KK[ic, -ic] + LL[-ia, -ib] + (acc[-ic]*acc[ic]*met[-ia, -ib])/3 + (DA[ic, -ic]*met[-ia, -ib])/3 + (2*KK[-ic, -id]*KK[ic, id]*met[-ia, -ib])/3 - (KK[ic, -ic]*KK[id, -id]*met[-ia, -ib])/3 - (LL[ic, -ic]*met[-ia, -ib])/3 + (acc[-ic]*acc[ic]*nu[-ia]*nu[-ib])/3 + (DA[ic, -ic]*nu[-ia]*nu[-ib])/3 + (2*KK[-ic, -id]*KK[ic, id]*nu[-ia]*nu[-ib])/3 - (KK[ic, -ic]*KK[id, -id]*nu[-ia]*nu[-ib])/3 - (LL[ic, -ic]*nu[-ia]*nu[-ib])/3 - kappaG*StressPi[-ia, -ib] + ZZ[-ia, -ib] - (met[-ia, -ib]*ZZ[ic, -ic])/3 - (nu[-ia]*nu[-ib]*ZZ[ic, -ic])/3
```

## Actually computed bad-minus-good trace mutation

```wolfram
4*HH[]^2 + (4*Sigma[-ia, -ib]*Sigma[ia, ib])/3
```

Actual fixed-reference witness: `4` (4/ell^2 dimensionfully).
