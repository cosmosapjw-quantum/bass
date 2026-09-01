# GEO-02R2 PHYS-MATH-CODE audit

## Equation-to-code map

| Equation/contract | Public function | Executable evidence |
|---|---|---|
| `C(a,n)` | `BianchiStructureConstants` | inherited ALG-01/R1/R2 tests |
| Levi-Civita/Koszul generator | `LeviCivitaConnection` | exact II/V/IX witness tests |
| torsion residual | `ConnectionTorsionResidual` | zero for five witnesses |
| metric-compatibility residual | `ConnectionMetricCompatibilityResidual` | zero for five witnesses |
| connection one-form inventory | `ConnectionOneFormTerms` | counts `0,6,4,6,10` |
| constant `O(3)` covariance | `ConnectionCovarianceQ` | proper/improper tests and hostile mutation |
| array-order adapter | `ConnectionToLockedGammaOrder`, `ConnectionFromLockedGammaOrder` | direct, inverse and componentwise tests |
| parent/claim receipt | `ConnectionCompositionReceipt` | semantic hash and exceptional carriers |

## TDD and repair sequence

1. The composition test was committed before the connection APIs.
2. A first raw-GitHub download probe returned HTTP 404 and was rejected as an
   invalid infrastructure probe.
3. Exact Dropbox-restored `ALG-01R2` source produced a valid RED:
   `2 passed / 16 failed / 0 not evaluated`.
4. The initial candidate produced `17/18`; the sole failure exposed a reversed
   direct `Transpose` contract.
5. The corrected test was replayed against the unchanged parent and again
   produced valid RED `2/16`.
6. The implementation was corrected and produced focused GREEN `18/18`.
7. Imported donor plus composition tests produced `33/33`.
8. Fresh full regression produced `114/114`.

## Full regression

```text
W0Environment.wlt                         PASS
W1Conventions.wlt                         PASS
ALG01BianchiAlgebra.wlt                   PASS
ALG01R1ExceptionalAndCovariance.wlt       PASS
ALG01R2ExactIdentityAndCarriers.wlt       PASS
GEO02CartanConnection.wlt                 PASS
GEO02R2ConnectionComposition.wlt          PASS

total succeeded      114
total failed           0
not evaluated          0
```

## Identity and runtime

```text
parent commit
b0a2c8da9e74ce960394ae9c67c9744fb8e497ad

parent semantic registry SHA-256
e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762

connection module SHA-256
1f28c921734194c5a3b79e8d31ae045f7bfce336e2641e6e01a9232a0cdbc13d

corrected composition test SHA-256
941b1686c9a21a09f3150e0c645d8cf447209eacc87c234c8507b0d9ae2fb30a

full test-stack SHA-256
02288d40138d362b6a57b72387b2608b342c42ffe2cccecebd04fbde631433e1

xAct archive SHA-256
7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be
```

## Code-path reality

The new module is loaded by `wolfram/BASS/Kernel/init.wl`, and
`wolfram/scripts/run_stage.wls --stage GEO_02R2` selects the inherited five
stages plus both connection tests. The stage runner withholds curvature,
background and numerical claims.

The production Rust/Python solver path is not modified. This is symbolic
formula infrastructure only.

## Failure handling

- malformed `a` or `n` returns `Failure`, not a padded or projected state;
- invalid frame transforms return `False` or `Failure`;
- parent semantic hash mismatch blocks the composition receipt;
- missing exceptional carriers block the composition receipt;
- `curvature_generated` is structurally fixed to `False` in this stage.

## Regression and misspecification risks

### P0 fixed — array permutation

Round-trip tests alone were insufficient because mutually reversed adapters
can still round-trip. A direct componentwise identity is now mandatory.

### P1 open — sibling W2 not composed

The W2 abstract index/sign registry lives on a sibling branch. No code-level
proof yet shows that its abstract spacetime `Gamma`, extrinsic curvature and
Gauss-Codazzi adapters consume this exact concrete spatial array convention.

### P1 open — curvature dual oracle absent

No Riemann/Ricci code has been admitted. `GEO-03` must compare an independent
Cartan/exterior-form construction against an indexed component construction,
including contraction and xAct sign adapters.

### P2 open — source replay packaging

The stage has exact text mirrors and Wolfram replays, but no binary archive
identity is claimed. Dropbox remains a recovery mirror, not formula authority.

### P2 open — no numerical backend parity

No Rust/Python lowering, JVP/Jacobian, solver tolerance or output comparison
has been executed.

## Test sufficiency verdict

Sufficient for:

```text
spatial connection formula generation
five sentinel branch witnesses
proper/improper constant-frame covariance
index-order adapter
parent semantic inheritance
```

Insufficient for:

```text
spatial curvature
spacetime background equations
constraint propagation
all eleven branch evolution
matter or kinetic coupling
numerical solver correctness
```

## Verdict

`PASS_GEO02R2_SYMBOLIC_CONNECTION_CODE_PATH`

The code path is real, loaded, replayed and adversarially tested, but its
scientific claim ceiling remains a spatial connection compiler stage.
