# WSC-0 — Wolfram 15 capability matrix

| Capability | Probe | Classification | BASS use |
|---|---:|---|---|
| NDSolve Pantelides index reduction | PASS | executable | independent DAE oracle |
| NDSolve StructuralMatrix index reduction | PASS | executable | independent DAE oracle |
| symbolic Jacobian via `D` | PASS | executable | authority/Jacobian verifier |
| `SparseArray` | PASS | executable | sparse structure oracle |
| `FunctionCompile` | PASS | executable | in-kernel acceleration/oracle |
| WolframIR export | PASS | executable | compiler introspection only |
| Python `ExternalEvaluate` | FAIL here | SUPPORTED_BUT_ENV_OPEN | optional bridge, not core contract |
| Wolfram Client/WXF | docs supported | SUPPORTED | preferred Python→Wolfram bridge |
| xAct/xTensor | not found here | ENV_OPEN | native local seal remains required |
| Wolfram C codegen | available | POLICY_DISABLED | separate approval-only verifier track |

## Interpretation

Wolfram 15 already supplies most mathematical/DAE/Jacobian primitives that
ModelingToolkit would otherwise contribute. The missing piece is not a CAS
feature; it is a BASS-owned structural compiler with public, reproducible pass
semantics and a neutral IR.

`NDSolve` internal/private transformation objects are explicitly excluded from
the compiler contract. They may be used as an independent oracle only.
