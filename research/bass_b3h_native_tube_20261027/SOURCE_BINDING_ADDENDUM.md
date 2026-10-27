# S0 source binding and normalization decision

The input packet is `inputs/FINITE_TUBE_INPUT_SLICE.json`, 5722 bytes, SHA256
`0eb250e965ad3496d00b53d5a165bafc93de8506baa9dad8e04de2bbd3614cdd`.
Parent REC source is PR139 `d6dbe39a4923439547c01695d9020ba39367ea90`,
`data/pr05b2_source_history_v060.npz`, Git blob
`de43b1a2642fa0aa049abbfd1b0a7d775d684b1b`, 35239470 bytes,
SHA256 `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`.
The parent NPZ is immutable input. Four exact row140 knots and the original
clock/constants suffice for this selected cell; no original native solve is replayed.

The data-preparation packet suggests a right-endpoint reference. The frozen
consumer contract chooses the left endpoint. This changes only the common
volume and energy representation: eta_ref=eta0+5126*h and eta_end=eta0+5127*h.
Both use the exact-real affine native interpolation clock formed from the
original binary64 eta0 and h. The stored eta array differs by its final binary64
rounding and is retained as a diagnostic. This is a represented native history,
with physical interpolation/history error still null.

Use local u=eta-eta_ref and shifted knots u_j=(j-5126)h+ln(E140/E21).
The interval is selected by the source-native cell containing z=1100.
The actual single snapshot is z=1099.9986525171403, not exactly 1100.
Keep its own epoch for snapshot checks. Strict-past admissibility must hold on
each arrival segment, not only at the final accepted-count prefix.

Source H(eta), TR(eta), and nH(eta) are present in the exact original HyRec
October-2012 archive. Thus compute proper duration by integral d_eta/H(eta);
nH_ref is the total effective-H normalization, not the excited-state inventory.
The source's direct-line recoil/kinetic heat and electron/ion yield are zero in
its existing collapsed recoil-free convention. Missing input is the
interval-dependent absolute x1s, xr_p, source opacity, and matched
non-Lyalpha/QSS replenishment ledger.

For energy reporting keep the positive propagation loss directly:
W_loss=G E21 integral exp(3u) expm1(u) f_in du=U_ref-E21*N_in.
This is work associated with transport from the initial slice to line arrival,
not thermal heat. Also store the signed radiation change -W_loss.
A second small subtraction of rounded large numbers is a diagnostic only.

No actual A(eta) or f_s(eta) is supplied for the entire interval. Therefore
D_up,D_down,atomic kick and new B3i consumption remain null/not_run. Their absence
does not prevent completion of the actual incoming photon inventory and its
free transport using the existing B3g library.

