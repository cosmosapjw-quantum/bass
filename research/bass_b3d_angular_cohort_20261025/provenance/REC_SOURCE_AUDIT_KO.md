# REC source intake for BASS — actual source and next admissible edge

Observation date: 2026-10-25 Asia/Seoul. Read-only source audit; no science execution,
NPZ download, archive download, native run, or remote mutation.

## Current source identity

| PR | Current observed HEAD | Scope in current body |
|---|---|---|
| 132 | ae189694c15e09c6f96c44ef6b74b48afc2632ac | Retarded Bianchi-I characteristic/native-Wien adapter |
| 133 | c5394eccf6ff45f134e396c549844af91988aeb7 | Stored-history refinement envelopes, final delivery |
| 134 | ccf2bd088972e952fbe8e7e6eb21ccc8a7275447 | Frozen incoming 314×313 response and conditional error allocation |
| 135 | 0e3f6ead3bc42122a91edeaabe64ab498db399aa | Six-primitive thermodynamic Jacobian: S0 contract only, scientific execution NOT_RUN |

The current PR135 tree contains6554 entries and is not truncated. There is no
root AGENTS.md or applicable nested AGENTS.md for these lanes. Historical copied
AGENTS.md under survey source subtrees are not active owner instructions.
The parent independently reads the current central AGENTS. This intake queried
repo metadata, the30 latest updated PR records, eight retained PR metadata
records, PR132/135 recursive trees, and selected text. It is not an all-branch or
all-conversation survey.

`SELECTED_9_SOURCE_DELTA.json` confirms all3 original NPZ and6 owner modules
retain exactly the same Git blobs from scientific PR132 through current PR135.
No NPZ content was downloaded. All fetched text has exact Git blob validation,
SHA256 and byte counts in `source_manifest.json`.

## The actual LINE01 incident datum

Source: `research/rec_line_source_20261023/fixtures/STORED_NATIVE_LYA_STATE.json`,
blob54f06a59eeb3745ca72ec7a7dede5892c658bff1; original CSV
blob6399b59ca3c97d6c5b1162f83f50a6677fad06ff,
SHA2563a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7.

Source decimal fields, unchanged:

- z=1099.9986525171403; x1s=0.85507000330964777;
  nH=250.18675437302318 cm^-3; H=4.9696512229238343e-14 s^-1.
- TR=0.25882399309326415 eV; xr2p=1.9711283950160407e-14.
- Dfplus_Lya=7.6643364422337378e-15.
- E21=10.198714553953742 eV; g=3;
  Aeff=(626490000+2×626480000)/3 s^-1; lambda=hc/E21.
- Saved reconstruction reports x2p=1.9731060921627546e-14,
  fPlanck=7.709689027638636e-18 and
  f_plus=7.672046131261377e-15. These are reused owner outputs, not recomputed here.

The native scalar datum is a real blue-side occupation at one saved FLRW epoch.
Its frame is local non-tilted matter-rest orthonormal frame; rates use proper
seconds and physical volume. No angular field is saved. LINE01's separately
supplied S fixtures are not observed angular structure.

LINE01 uses total occupation
f_plus=1/expm1(E21/TR)+Dfplus_Lya and physical
x2p=xr2p+3*x1s*exp(-E21/TR). Native-HISTORY uses signed departures from a Wien
reference exp(-E21/TR). Conversion must retain the reference shift; numeric
rounding of Planck/Wien to the same saved double does not identify their models.
`line_source.py` blob5ac2a3107b80710504e63705ff16562131b5d1cf and
`history_boundary.py` blob1aa7f134c332bc4596372df18c7c47306260ecfc are unchanged.

## What can be consumed, and what remains to bind

LINE01 provides the coefficient card, local physical populations, scalar
blue trace at one epoch, fixed-frame local source equation, and paired
atomic-internal/radiation ledger. This is sufficient for its instantaneous
source and held-background local population map.

It does not supply the finite receiver's incoming characteristic support:
receiver identity/cell/face, time interval, energy-face correspondence,
angular measure, source→receiver frame transform, characteristic map,
and finite incident photon donor/depletion rule are absent. A scalar
cell average f_ij in B3b2 cannot fill these fields. A single trace value also
does not declare a finite temporal support or boundary reservoir.

For the actual native scalar HISTORY line face,
G_native=3×10^6×LYA_FACT m^-3 and
R=G_native*H*(d_out-d_in), with LYA_FACT=4.662899067555897e15 cm^-3.
This is a phase-space face flux normalization, whereas B3b2 G_i is a finite-cell
measure. A finite count requires the actual face flux integrated over proper
receiver time and declared angular support. Multiplying a trace by arbitrary
G_i would silently choose a bandwidth. The native phase measure also differs
slightly from reconstruction from modern SI constants; keep its source owner.

REC-HISTORY-RESP01 NEXT_INPUT_CONTRACT still explicitly lists the Bianchi
transport/incident trace/frame/energy/angular measure/clock connection as an
open owner obligation. It supplies a conditional error-response operator;
physical history uncertainty epsilon_j remains null. New PR135 supplies no
new admitted incident angular trace or receiver support.

## Gross channels and atomic exclusivity

For LINE01:
Delta=g*n_l-n_u>0,
D=n_u*(1+f_plus)-g*n_l*f_plus,
R=A*B*D;
gross_down=A*B*n_u*(1+f_plus),
gross_up=A*B*g*n_l*f_plus.
The positive gross channels must remain separate even near cancellation.
Atomic number changes(-R,+R), photon number+R,
internal energy-E*R, photon energy+E*R, kinetic heat0 in this recoil-free model.
The angular PSTF term E*A*D*Q is an injection rate, not stored Source.pi.

LINE01 authorizes only standalone_detached/native_line_owner_active=false.
LINE02 separately isolates the native direct pair
Trr[1,1] += r0, sr[1] += r0*b0,
r0=LYA_FACT*H/(nH_cm3*x1s), b0=3*x1s*Dfplus_Lya.
Replacement is
Mstar=M+(r-r0)e e^T,
sstar=s+(r*b-r0*b0)e.
Other Beta, 2s↔2p, Raman/two-photon, diffusion, virtual blocks and history remain
owned by native source. LINE02 r*xr_p and r*b0 are signed departure terms,
not positive gross emission/absorption. Production source is unchanged.
`native_line_owner.py` blobcb36a10b19b9b60c046383389f9706bd9970222f is unchanged.

An outgoing boundary assignment and separate positive radiation Source for the
same event would double-charge radiation. The HISTORY adapter explicitly accepts
one radiation owner (boundary or event). A BASS transaction must make this
exclusivity concrete and carry the same atomic energy debit.

## Conditional f_plus=0 emission plus collisionless transport

The already accepted BASS B3b commit_emission API performs exactly the detached
f_plus=0 finite transaction. Reuse its actual source/card, population/energy
identity, duplicate-transfer guard, proper dt, thick-path gate, and14-node
positive emission cubature. This source is separable from noninteracting
collisionless transport provided the new contract fixes the following:

1. Initial radiation and atomic stocks, their frame/epoch/fixed scales, and
   a single owner for the line excitation energy.
2. The zero-blue-trace support over the full proposed time interval. Genuine
   vacuum is sufficient. For existing radiation, prove its transported support
   cannot reach the blue line face, or declare that radiation a distinct
   noninteracting control component. The latter is a new bounded model scope,
   not an absorption-capable physical continuation of the original background.
3. A frozen positive redshift rate H+sigma_nn>0 along admitted rays ensures
   photons emitted at the line move to its red side; this alone does not exclude
   pre-existing blue-side photons entering the line.
4. Atomic population dilution and internal-energy dilution during transport,
   and proper-time conversion dt=(L/c)dτ. The source step holds its background
   and populations except for the declared transition; streaming changes must
   be carried back into the next source's N,H,S input.
5. Separate local splitting truncation from the thick/finite-opacity envelope,
   angular packet representation and background integration errors. A second-order
   splitting claim needs the chosen transport/source smoothness and composition.

Therefore the actual finite-absorption edge remains INPUT_DEPENDENT with the
specific receiver support/normalization/clock and finite donor obligations.
A source-qualified emission+collisionless bounded test is independently
preparable under the explicit zero-trace/support contract. This is a constructive
next step, not a no-go theorem or a completion of B3c/B4/B5.

Evidence status: source identities and text content are implementation-level
readback; all REC scientific numerical results above are owner-reported and
reused. Different-model scientific review NOT_RUN. No claim of scientific
reexecution, complete remote archive restore, or global physical completion.
