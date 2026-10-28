# BASS PR238 bounded sibling review: exact stored-energy cap

Reviewer: `/root/angular_certificate_review`, 2026-10-29 Asia/Seoul.

Reviewed sibling: PR238, branch `research/bass-ce1f-tabulated-meanray-implementation-20261029`, head `0286dd0a97f512a2dc6f431e462e64bd65267047`.

Actual sibling source read: `/workspace/scratch/c7d714747210/sibling_comparison/einstein_tabulated_source.py`; SHA256 `8191ad0035b8683570200f6258351f444e105e3e26cd5d8c4829d26ebc23c53f`.

Our previously reviewed source remains SHA256 `1bfce9103c02c06f7f3477a16b2f9ccc1d3e34a0de71acd5fa6b9c5ef7115345`. No source file or remote branch was modified in this review.

## Finding

The sibling geometry function's selected `Emax` does **not** universally bound the exact-real initial energy of the stored discrete source. The failure occurs on the simplest ordinary positive one-cell table. Therefore the sufficient energy-cap premise used to justify its common geometry hull and Dini comparison is not closed for all admitted inputs.

This is a localized certificate-assurance finding. It is not a counterexample to Einstein–Vlasov evolution, the centered angular-cell construction, or the final conservative geometry-error number. No violation of the final returned geometry bound was established by this review. The direct pressure certificate is a separate result; it passes the strict initial-pressure comparison in the example below.

## Source location and mechanism

Sibling `certified_tabulated_geometry`, lines251–254, evaluates an energy certificate but then chooses

```python
Econt = _iv_fraction(source.exact_energy)
Eb = Interval(float(source.energy0))
Emax = Interval(max(Econt.upper, Eb.upper))
```

`source.energy0` is a binary64 evaluation of the ray-energy sum. The exact-real stored-source ODE instead uses

`E_Q(0)=sum_j mass_j * sqrt(sum_i n_ji²)`,

with each recorded mass and ray component interpreted as an exact binary rational. Neither the exact continuum energy nor the rounded binary64 evaluation must exceed this exact-real value.

Sibling `certified_tabulated_energy` already calculates an exact-real stored energy internally and reports its continuum discrepancy and evaluator discrepancy. Geometry does not use either of those differences to upper-bound E_Q. The selected cap is then used at lines263–267 in both the log-scale hull and `propagate_interval`.

For the standard proof, positivity and expansion give `E_Q(u)≤E_Q(0)`. To conclude `E_Q(u)≤Emax`, one must first establish `E_Q(0)≤Emax`. The explicit example disproves that premise at u=0. The weaker inequalities actually needed for a particular trajectory might still hold through other slack; the existing energy-cap argument has not established them universally.

## Ordinary positive-table witness

Actual invocation:

```python
TabulatedRadiation(
    ['0','1'], ['0','1'], [['0.9']],
    refinement=1, backend='python_oracle')
```

The physical input is a uniform isotropic continuum angular table with exact continuum energy9/10. Its stored ray and mass are

```text
n = (0.5773502691896258, 0.5773502691896258, 0.5773502691896258)
n_i.hex() = 0x1.279a74590331dp-1
mass.hex() = 0x1.ccccccccccccdp-1
```

The exact stored squared norm is

```text
81129638414606703496731723412443 /
81129638414606681695789005144064
```

and is greater than1. The sibling's float evaluation returns `source.energy0=0.9`, so its chosen cap is the exact binary64 number

```text
Emax = 0.90000000000000002220446049250313080847263336181640625
```

Independent Decimal110 evaluation of the exact stored mass/ray formula gives

```text
E_Q(0) = 0.9000000000000001431272750758168544229966047394690051401865...
E_Q(0)-Emax = 1.2092281458331372361452397137765259889018651...e-16
```

A separate MPFR192 RNDD/RNDU computation, forming the rational stored norm before the square root and subtracting the exact binary cap *before* conversion to binary64 endpoints, encloses the signed gap by

```text
[1.2092281458331372e-16, 1.2092281458331375e-16]
```

Both endpoints are strictly positive. The difference is greater than the MPFR enclosure uncertainty, and its sign is independently confirmed by the Decimal calculation. Thus the witness does not depend on a comparison between two nearly equal rounded output energies.

The same failure is reproduced if the sibling is supplied the exact decimal expansion of binary64 .9,

```text
0.90000000000000002220446049250313080847263336181640625
```

as its table entry. This second input has exactly the energy semantics of our binary64 input API, so the issue is not explained by decimal-versus-binary physical input differences.

All exact input data, hex values, signed MPFR intervals, Decimal values, the existing returned geometry result and source checksum are preserved in `SIBLING_238_EVIDENCE.json`.

## Direct-pressure result in this witness

At ell=0, continuum pressure is E_cont/3. The exact-real stored pressure is E_Q/3. The Decimal110 maximum discrepancy for the exact9/10 input is

```text
4.77090916919389514743322015798230017133955037...e-17
```

The sibling pressure certificate returns componentwise bounds

```text
(2.5704917553678075e-16,
 2.5704917553678075e-16,
 2.4039583016740340e-16)
```

which contain that difference strictly. The energy-cap finding therefore does not invalidate this observed direct-pressure certificate. The underlying centered Taylor construction agrees with the independent CE1-F mathematical derivation, while implementation-specific proof obligations remain local to each source.

## Minimal correction

Return an outward interval for the exact-real stored energy from `certified_tabulated_energy` and choose

```python
Emax = Interval(max(E_cont.upper, E_Q_exact_real.upper))
```

as in our reviewed implementation. For the witness, the outward binary64 upper endpoint of E_Q is `0.9000000000000002`, sufficient for the comparison coefficient. An alternative safe cap is an outward upper of `E_cont + exact_real_discrete_difference_upper`, using the already returned absolute discrepancy. Recompute the small geometry hull/source/Dini result after changing the cap, preserve the original result, and add a test asserting exact-real stored initial energy is bounded. No alteration of physical data, normalization or target tolerance is needed.

## Other inspected difference: maxcomp

Sibling line224 converts an exact rational stored square with `float(nsq[i])` before taking the maximum with the cell-coordinate upper endpoint. A nearest float conversion is not by itself an outward upper. However, for ordinary nondegenerate cells the cell-coordinate upper endpoint often dominates the stored square, and in the witness above it certainly does. This review did not demonstrate an underbounded `maxcomp` or a final pressure-bound violation caused by this line. It is therefore recorded as an unclosed conversion/proof detail, not as a second established numerical failure. Replacing it with `_iv_fraction(nsq[i]).upper` is a minimal unambiguous outward formulation if that path is retained.

## Scope decision

Preserve both branch identities and their source/evidence. The sibling's universal geometry-certificate admission requires the energy-cap correction or an alternative completed argument. Its direct pressure/source construction and numerical results should be evaluated independently at their actual scope. Our prior C9 result continues to apply to our unchanged recorded source bytes, which already include the exact-real discrete energy cap.

No repository-wide no-go, general impossibility claim, or main/parent merge recommendation is made.

