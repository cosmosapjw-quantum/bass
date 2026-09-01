# ALG-01R2 PHYS–MATH audit

**Stage:** `ALG_01R2`  
**Verdict:** `PASS_WITH_STRICT_ALGEBRA_AND_WITNESS_SCOPE`  
**Tested source commit/tree:** `1de5a4bf735c77d71f00b34ec3660ea21fea93a2` / `6245f5d8e8bd8cf2ebf58178428a9d4f5b4bb898`

## 1. Assumptions and conventions

- spacetime signature: `(-,+,+,+)`;
- spatial orientation: `epsilon_123=+1`;
- Bianchi structure input:

  ```text
  C^gamma_{alpha beta}
    = epsilon_{alpha beta delta} n^{delta gamma}
      + a_alpha delta^gamma_beta
      - a_beta delta^gamma_alpha;
  ```

- `n^{alpha beta}=n^{beta alpha}` and the Jacobi constraint is `n^{alpha beta} a_beta=0`;
- canonical witness values are dimensionless fingerprints, not physical ONF magnitudes;
- physical `a_alpha`, `n_alpha_beta` and `Sigma_alpha_beta` have dimension `L^-1`;
- the signed class-B parameter `h=A^2/Delta_N` is dimensionless;
- the exceptional `VI_-1/9` sector is not a twelfth public algebra type.

## 2. Exact branch-identity repair

The generic RawJSON serializer maps the exact rational `-1/9` and its machine-real approximation to the same JSON number. Therefore bare RawJSON is not admitted as the semantic authority for exact branch parameters.

The repaired authority path stores

```text
signed_h_ast = ExactScalarAST[-1/9]
```

and hashes a semantic projection in which the bare display scalar is replaced by this exact AST. Machine-real `signed_h` values are rejected by `BianchiTypeSpecQ`.

Fresh exact-source replay produced the canonical registry semantic SHA-256

```text
e0e5fbba464a839fcb5b11d41c7772c666224ec69f806910aab3bfab5a2f1762
```

with no machine-real value in the projected authority object.

## 3. Exceptional witness obligations

The physical branch predicates remain

```text
a != 0
det(n_perp) < 0
h = -1/9
exceptional momentum constraint
```

and do not impose nonzero `Sigma13` or `Sigma23` on every physical solution.

The canonical witness separately carries the representation obligations

```text
non_diagonal_shear_survival
sigma13_carrier_present
sigma23_carrier_present
```

so that a code representation which silently deletes either independent direction is rejected without excluding legitimate zero-valued physical submanifolds.

Adversarial results:

| Mutation | Result |
| --- | --- |
| canonical exceptional witness | PASS |
| delete only `Sigma13` carrier | REJECT |
| delete only `Sigma23` carrier | REJECT |
| delete both carriers | REJECT |

## 4. Dimensional and limit checks

- `[a_alpha]=[n_alpha_beta]=[Sigma_alpha_beta]=L^-1`;
- `[Delta_N]=L^-2`;
- `[h]=1`;
- the exact identity `Delta_N=-9 A^2` implies `h=-1/9` without a hidden unit conversion;
- the canonical witness remains a dimensionless sign/rank probe and is never substituted for dimensional runtime data;
- no connection, spatial curvature or Einstein equation is inferred from this stage.

## 5. Counterexamples and hostile mutations

The full hostile registry contains eight generated mutations. All are detected:

```text
JACOBI_BREAK
IX_INERTIA_BREAK
V_N_BREAK
EXCEPTIONAL_H_BREAK
EXCEPTIONAL_MOMENTUM_BREAK
EXCEPTIONAL_SIGMA13_DELETE
EXCEPTIONAL_SIGMA23_DELETE
EXCEPTIONAL_SHEAR_DELETE
```

The machine-real `h` mutation is rejected before semantic hashing.

## 6. Ranked findings

- **P0:** none.
- **P1:** none remaining inside the declared ALG-01R2 scope.
- **P2:** connection-index convention, Koszul/Cartan connection and curvature are deliberately not promoted here.
- **P2:** only the five bounded witness branches are admitted as generator witnesses; this is not all-family background support.
- **P3:** canonical witnesses demonstrate representation obligations, not generic physical amplitudes.

## 7. Claim boundary

Authorized:

```text
ALG_01_EXACT_SEMANTIC_IDENTITY_VERIFIED
ALG_01_INDEPENDENT_EXCEPTIONAL_CARRIERS_VERIFIED
```

Withheld:

```text
CARTAN_CONNECTION_OR_CURVATURE_DERIVATION
BACKGROUND_EINSTEIN_MATTER_EQUATIONS
ALL_FAMILY_SOLVER_SUPPORT
GENERIC_ELL_COMPILER_CORRECTNESS
NUMERICAL_PARITY
SCIENCE_VALIDITY
BASS_RF04_PROMOTION
```
