# B3h observable-specific Lyalpha memory bound

UNIT=BASS_B3H_LYA_DUAL_WITNESS_20261028
BASE_F=5c3623cb06280561853b00b33d74ae638ab24c82
ORIGINAL_DAG_RECORD=28/88; DELTA=0; AUTO_NEXT_NODE=false.

Selected next theory/implementation unit: replace the scalar norm memory estimate by a signed output-specific constant positive dual witness. For the saved two-state same-law difference xdot=-M(t)x, the output is integral N*Ralpha(t)*x_2 dt. Preserve the shared Ralpha in both M22 and the count row. No native ODE, QSS solve, old quadrature, B3i or historical campaign replay is authorized by this unit.

The earlier candidate of deriving moving-QSS lag was dropped after source inspection: the saved native endpoint transaction already has a second-order particular solution and knot layers. Reuse that completed result rather than rerunning it. REC143's313background jets and BF2 are separately scoped; neither supplies missing physical error radii here.

For endpoint non-Lyalpha matrices [[a,-beta],[-chi,d]], define k=max_endpoint chi/a and s=min_endpoint(d-beta*k)>0. With N>=0 and 0<=R<=Rmax, w2=N*Rmax/(s+Rmax),w1=k*w2 obey M(theta,R)^T*w>=N*R*e2. The first row follows from a*k>=chi; the second residual is bounded below by N*s*(Rmax-R)/(s+Rmax). Positivity then gives -w^T*x_minus <= Delta_count <= w^T*x_plus for every finite horizon. Every feasible constant nonnegative witness is componentwise >=w; this is optimality within that witness family, not sharpness of an actual nonautonomous finite trajectory.

Input is a selected exact-rational projection of saved source512-bit QSS intervals and coefficient endpoints, SHA2563ac1c66eb95937bc2456f3c99c57f96128c57a619a72d02ac6d869beb8e87c44. It does not re-solve QSS. Parent ZIP5008994bytes/SHA256300182efc14eb633620f0dc6f183f700bec110a069fc05a692bacdf6684a5d54 was restored locally and hash matched. Physical/source uncertainty and E_QSS_old remainnull, L4false.

S0 covers actual R1-R5/C1-C4 contract, theory and design outputs9/20. Initial source capsule BASS_B3H_LYA_DUAL_S0_20261028.zip:9018bytes, SHA256c1bf1cfdaefce28ee9dc6a66e189261b4290c7b4a179a376aa41d575d447c757. Git is the concise projection; the capsule contains full contract/theory/plan/input/survey/ledger. Actual provider ACKs follow separately.

Fresh scientific/test allocation30CPU/120wall seconds, one thread, targeted red/green plus one primary and one independent-algorithm check. Preparation/network/model/delivery costs are unmeasured,not0. Old budgets remainclosed/nontransferable. Actual execution is serial parent fallback; native_subagent and distinct-author R6/C9 are NOT_RUN. Independent algorithms and CAS do not close those reviews. No central/foreign/main writes, merge or automatic second unit.
