# Exact reuse for the split matter/radiation warm LRS pilot
Date: 2026-10-21 (Asia/Seoul). Scope: R2–R5 contribution; no new pilot integration or performance benchmark.

## Result and source boundary

The source supports an exact, bounded, **per-model cache of the massive three-moment evaluator** as a small next optimization. The evaluator depends on the current geometric coordinates \((x,b)\) and fixed kinetic inputs, not the contemporaneous photon hierarchy, gas state or predictor-corrector proxy. A cache can therefore avoid repeated quadrature evaluations without changing the retained quadrature, time integrator, closure or reduction expression.

This conclusion comes from the actual source in
`vendor/rei_c15/research/rei_c15_sigma_pi_feedback_20261015/coupled.py`,
`EinsteinBoltzmann.massive_source_3moments` and its `_physical` caller, under owner
`80825585f9fe31d2ee0d5af545ada3fa1f52be72`.
The current adapter is `split_sweep.PreparedContext.model`; the original owner bytes should remain pinned.

The prior 729-case calculation, its 243 PASS groups, plots and receipts are inputs to reuse. No assertion of a measured cache speedup or memory saving is made. The separate PR198 collisionless long-interval reduction must retain its own physical lineage.

## 1. Definition and fixed-quadrature map

Use signature \((-+++)\), \(a_\perp=a e^{-b}\), \(a_\parallel=a e^{2b}\), \(x=\ln(a/a_0)\), and \(r=e^{-x}\). Covariant spatial momenta are conserved for the collisionless Bianchi I species. This reduces the Vlasov equation to a fixed initial distribution in those momenta; energy and pressure still depend on the evolving metric. Heinzle–Uggla Eq. (2d),(2f),(3) give precisely this representation in \(G=c=1\) units. Their invariant momentum/distribution construction is used here; their asymptotic theorem is not imported into the driven warm photon/chemistry problem. [Original paper](https://arxiv.org/pdf/gr-qc/0512031), [rendered original, Section 2](https://ar5iv.labs.arxiv.org/html/gr-qc/0512031).

For physical comoving momentum \(q_i\), the energy is
\[
 E(\mathbf q,a,b)=\sqrt{m^2c^4+c^2a^{-2}
 \left[e^{2b}(q_1^2+q_2^2)+e^{-4b}q_3^2\right]}.
\]
If \(\mathcal N f_0\,d^3q\) denotes the comoving number measure, then
\[
 \rho=a^{-3}\int E\,\mathcal N f_0\,d^3q,\qquad
 D=P_\parallel-P_\perp
 =a^{-3}\int\frac{c^2}{E}
 \left[p_\parallel^2-\frac{p_\perp^2}{2}\right]\mathcal N f_0\,d^3q,
\]
where \(p_\parallel=a^{-1}e^{-2b}q_3\) and
\(p_\perp^2=a^{-2}e^{2b}(q_1^2+q_2^2)\). Both \(\rho,D\) have energy-density/pressure units.
Here \(\rho\) is energy density, not mass density. This map is a direct derivation from the mass-shell integral; the normalization \(\mathcal N\) is source-owned.

The C15 kernel uses dimensionless \(m/(k_BT_{\rm ref}/c^2)\) and \(q c/(k_BT_{\rm ref})\); its arrays therefore contain dimensionless energies. In its actual variable names:
\[
 R_j^2=e^{2b}(1-\mu_j^2)+e^{-4b}\mu_j^2,\quad
 p_{ij}^2=r^2q_i^2R_j^2,\quad
 E_{ij}=\sqrt{M^2+p_{ij}^2},\quad
 v_{ij}^2=p_{ij}^2/E_{ij}^2,
\]
\[
 \bar\mu_j^2=e^{-4b}\mu_j^2/R_j^2,\qquad
 W_{ij}(\alpha_m)=\frac{w_{r,i}}{\mathcal Z}w_{\mu,j}
 \left[1+\alpha_m P_2(\mu_j)\right],\quad
 P_2(\mu)=(3\mu^2-1)/2 .
\]
The implemented three moments are
\[
 J_{00}=r^3\sum_{ij}W_{ij}E_{ij},\quad
 J_{01}=r^3\sum_{ij}W_{ij}E_{ij}v_{ij}^2,\quad
 J_{20}=r^3\sum_{ij}W_{ij}E_{ij}v_{ij}^2P_2(\bar\mu_j).
\]
C15 then uses \(E_m=\rho_{m,\rm ref}J_{00}\) and
\(D_m=\rho_{m,\rm ref}J_{20}\). The current evaluator also returns \(J_{01}\), which remains useful for pressure/initial-seed calibration.

**Computational identity:** retain C15's actual evaluation order
`weighted=(rr**3)*massive_weight*energy`,
then `np.sum(weighted)`, `np.sum(weighted*v2)`,
`np.sum(weighted*v2*.5*(3*mu2-1)[None,:])`.
The algebraically equivalent replacement \(E v^2=p^2/E\) has a different floating-point operation sequence and is not part of an exact-byte cache optimization.

### Dependency and cache table

| Quantity | Depends on | Reuse boundary |
|---|---|---|
| \(q_i,w_{r,i},\mu_j,w_{\mu,j},P_2(\mu_j)\) | quadrature order, radial family, \(M\) in normalization | immutable prepared context |
| \(W_{ij}\) | those data and \(\alpha_m\) | one fixed component seed/model |
| \(R_j^2,p_{ij}^2,E_{ij},v_{ij}^2\) | \(x,b,M\), nodes | only identical current geometry and kernel inputs |
| \(J_{00},J_{01},J_{20}\) | geometry and \(W_{ij}\) | exact \((x,b)\) within the fixed model |
| \(D_r\) | current gamma, neutrino and UV states | recompute from actual state |
| \(H\) and total Einstein source | current components, shear, gas, UV | cannot use the massive-only key |

The code's current prepared context marks quadrature/source/rate arrays readonly, but the fresh `massive_weight` is writeable. The frozen Parameters dataclass prevents field edits, while `model.params` itself can still be rebound. An implementation must make the kernel binding stable for the cache lifetime, detect a changed binding, or clear/rebuild the cache. A process-global cache keyed only by epoch would omit relevant state.

## 2. Exact cache equivalence lemma

Let \(K\) contain the source identity and fixed kinetic data. Within one model lifetime, suppose \(K\) and the floating-point environment remain unchanged. Let \(F_K(x,b)\) be the deterministic source function, including its existing domain checks. Cache the immutable tuple of its three returned binary64 values using an injective encoding of the two finite binary64 inputs, for example `struct.pack(">dd", x, b)`.

For every valid call sequence the cached evaluator returns exactly the same tuple as \(F_K\). On a miss it executes \(F_K\); on a hit the stored value came from the same input bytes and the same \(K\). Induction over the call sequence proves the claim. Eviction only causes a future miss and does not change the value. This is an elementary conditional program-equivalence result, not a new physical theorem.

Requirements for a concrete wrapper:

1. Bound the cache size; preserve `fast_massive` mode and the original owner callable.
2. Use one cache per component seed/model, or include the complete immutable kernel binding in a shared key.
3. Validate the same finite/domain conditions; failed evaluations must not produce cache entries.
4. Preserve signed-zero key identity and reject nonfinite values through the owner contract.
5. Store only immutable tuples, and create fresh counters/proxy/gas/photons for each case.
6. Include the new adapter in source identity for *new* runs; previously completed results retain their old execution source.
7. Check exact cached-versus-uncached return bytes, invalid inputs, eviction, repeated geometry with changed unrelated state, and separation of opposite \(\alpha_m\) cases. A small integration comparison can test the wiring; the completed 729 cases need no replay.

Python's bounded `functools.lru_cache` is an existing standard-library implementation suitable for memoization. Its documentation distinguishes coherent cache updates from a guarantee of a single evaluation during concurrent misses. One numerical thread per worker avoids making such a guarantee. [Python 3.12 functools](https://docs.python.org/3.12/library/functools.html), [binary packing](https://docs.python.org/3.12/library/struct.html).

## 3. Why other tempting reductions need a separate contract

At fixed geometry the quadrature is mathematically affine in the P2 seed:
\[
 J_\ell^{(n)}(x,b;\alpha_m)
 =J_{\ell,0}^{(n)}(x,b)+\alpha_m J_{\ell,2}^{(n)}(x,b).
\]
This is a useful basis factorization for many seeds at the **same** geometry. Different fully coupled trajectories have different \(b(x)\) and photon/gas states, however. A precomputed \((x,b)\) grid with interpolation introduces a new approximation. Even at identical geometry, reducing two basis sums then adding them changes binary rounding relative to the source expression. Therefore the affine map is a derived candidate for later validation, while the exact memoization above preserves current arithmetic.

NumPy explicitly documents that partial pairwise summation and precision depend on the chosen axis and memory layout. A batched reshape, `einsum`, BLAS dot, SIMD reassociation, FMA or parallel reduction can be mathematically equivalent yet not preserve source rounding. In the current cancellation problem this distinction is visible. [NumPy 2.3 sum](https://numpy.org/doc/2.3/reference/generated/numpy.sum.html).

The massless limit permits radial factorization when the distribution separates in radial and angular variables, because \(E=cqR/a\). With finite mass the square root couples radial and angular variables. This explains why a reduced collisionless massless code is a separate reusable idea rather than an automatic replacement for the massive C15 kernel. Thomson collisions and newly emitted/absorbed UV require their existing evolving state and event ownership.

## 4. Cancellation as an acceptance observable

For the fixed LRS axis,
\[
 \pi_A{}^a{}_b=\mathrm{diag}(-D_A/3,-D_A/3,2D_A/3),\quad
 \sigma^a{}_b=\mathrm{diag}(-s,-s,2s),\quad
 \kappa_t=8\pi G/c^2.
\]
Thus
\[
 \widetilde\Pi_A=\frac{\kappa_tD_A}{\sqrt3H^2},\quad
 \Pi_{\rm tot}=|\widetilde\Pi_m+\widetilde\Pi_r|,\quad
 \sigma:\pi_A=2sD_A .
\]
Replacing the total by \(|\widetilde\Pi_m|+|\widetilde\Pi_r|\) creates an order-unity source error on the cancellation plane. For opposite \(D_m,D_r\), the error in the corresponding dimensional absolute source is \(2\min(|D_m|,|D_r|)\). This is an exact identity.

If computed component errors are \(\delta D_m,\delta D_r\), the absolute error of their sum is bounded by
\[
 |\delta D_{\rm tot}|\leq|\delta D_m|+|\delta D_r|
\]
before the final addition's rounding contribution. Relative error is ill-conditioned as \(D_{\rm tot}\to0\), so component-wise absolute comparisons and work-sum residuals are appropriate. A raw residual must not be clipped to improve apparent agreement.

The source equation
\[
 \widetilde\Sigma'=\widetilde\Pi_{\rm tot}
 -(3+\dot H/H^2)\widetilde\Sigma,\qquad {}'=d/d\ln a
\]
matches the trace-free Einstein equation after restoring \(\kappa_t\). Lee–Nungesser–Tod, Sec. 2.1, provides the corresponding general Bianchi I equation. [Original paper](https://arxiv.org/pdf/1911.04937).
At an initially vanishing signed total stress and shear, a nonzero derivative of the component sum creates total stress at first order and shear at second order in \(\Delta\ln a\). Caching only \(D_{\rm tot}(a_i)=0\) would erase this retained physical response.

## 5. External components: concrete decisions

| Existing component | Use now | Reason / condition |
|---|---|---|
| Python bounded memoization and binary packing | Adopted: OrderedDict bounded LRU and struct binary keys; locally validated | no new dependency or closure; bounded storage and byte-identical inputs |
| Existing SciPy PCHIP owner objects | Reuse prepared coefficients | same source/rate table and interpolation domain; keep warm range and extrapolation policy |
| NumPy existing vectorized quadrature | Retain source arithmetic for this change | exact cache leaves reduction unchanged |
| Python multiprocessing/shared-memory | Retain independent process execution; explicit shared memory is conditional | only fixed arrays may be shared; lifecycle and readonly semantics need handling |
| New global affine-\(\alpha_m\) basis table | Derived follow-up candidate | geometry/rounding contract needs validation; no speedup claim |
| New JIT/MPI/solver or forced dense batch evolution | Defer in this bounded change | additional precision/dependency/scheduling decisions; present goal already has finished pilot |

The SciPy documentation confirms a multi-column interpolation axis and a shape-preserving PCHIP implementation; this supports preparing and reusing the owner's already chosen interpolator rather than recreating it per case. [SciPy 1.17.0 PCHIP](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.interpolate.PchipInterpolator.html).

NumPy recommends readonly sharing or synchronization for arrays shared by threads. Python's `multiprocessing.shared_memory` provides named cross-process memory but requires explicit `close/unlink` ownership. Those APIs are reusable if shared array size makes transfer/storage material; no such measured need is asserted here. [NumPy thread safety](https://numpy.org/doc/2.3/reference/thread_safety.html), [Python 3.12 shared memory](https://docs.python.org/3.12/library/multiprocessing.shared_memory.html).

## Evidence status and retrieval scope

- Literature-supported: conserved Bianchi I covariant momenta and fixed distribution representation; trace-free Einstein equation.
- Derived from those equations and inspected code: pure kernel dependency map, affine seed identity, cancellation identities, conditional exact-cache equivalence.
- Implementation status: exact cache implemented in `cached_context.py` with an OrderedDict LRU, immutable data bytes and per-call dtype/shape/stride/C-contiguity binding checks. `work_plan.py` and `batch_worker.py` apply completed-case reuse and pending-only case batching. Scoped numerical and independent-review receipts are in `evidence/`.
- Existing numerical results: reused from pinned prior report; no rerun or new convergence assertion.
- SciSpace query returned 10 records with duplicates and incorrect index dates for some arXiv items. Bibliographic identity/years were checked against the original sources, not the search index's ingestion year.
- Exa search requested 5+5 results in two distinct workstreams. Follow-up fetches read selected original papers and official versioned documentation. Initial arxiv/html fetches returned metadata rather than full equations; ar5iv originals and actual arXiv PDFs resolved that gap.
- Raw retrieval JSONs under `research_notes/research_pass*.json` are temporary working evidence. They contain long source text and should not be republished as the final research deliverable. This note and `source_records.json` contain the reusable synthesis and exact source links.

