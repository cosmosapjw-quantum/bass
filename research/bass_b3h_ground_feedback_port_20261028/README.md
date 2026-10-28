# B3h ground-denominator feedback port

UNIT=BASS_B3H_GROUND_FEEDBACK_PORT_20261028
PARENT_FEEDBACK=ff1dc0c0cccf3fd037343a258848eddf59f36341
BASE_FROZEN=5e7b9e30961304870360f05c7447f66b9887ffd0
ORIGINAL_DAG_RECORD=28/88;DELTA=0;AUTO_NEXT_NODE=false.

Selected R1/C1 question: bind a feedback coefficient to the actually represented inverse-ground rate, preserving its incoming-source cancellation and the sign of a componentwise-negative reset. Source e35673b.../variable_operator.py blobcd189e7fb24def61734a740c887a7c08e7092464 evaluates R=C/g and b_alpha=3R*g*f. Hold A,b_non,C,f,g externally prescribed and impose the additional controlled closure ghat=g+q, Rhat=C/(g+q), phat'=b-(A+Rhat E22)phat, q'=Rhat phat2-R p2,q0=0. This isolates one ground-denominator port; it is not full ground/continuum/thermal/radiation feedback or atomic conservation closure. All other responses remain unactivated.

Theory will use nonnegative b,p, cooperative-A and nonnegative A column sums. For w=p-phat>=0,r=-q>=0, w'=-M w+e2*s,r'=R*w2-s,s=R*r*phat2/(g-r). Then (1^T w+r)'=-1^TAw<=0. Z<gmin supplies a non-exit condition. A prefix adjoint can sharpen r<=GZ and gives q>=q_nominal. New exact Fraction scalar gain/count bounds and independently solved nonlinear scalar fixtures will be computed, not a native trajectory.

Frozen tests: negative/zero/missing/singular and sign controls; new scalar RK4 refinement128/256/512/1024, finest error<=2e-9 and ratios>=12 above1e-13, invariant tolerance2e-12; separate Decimal80 implicit solution. These are selected-model checks, not physical validation. Fresh child cap30CPU/120wall,perchild30wall,one thread,one diagnosed repair episode; other costsunknown. Old allocationsclosed/nontransferable.

S01 outputs2/20, original28/88. Capsule4729bytes/7members,SHA2561b43459c1434757589a2282b496c5c89883666e595d4e1dc2035ec742284be44. Native delegation absent; distinct-authorR6/C9NOT_RUN. Expected-parent non-force publication and paired stage capsules preserve distinct R/C evidence. Parent original feedback archive is unchanged and now actually dual-backed; see PR230. No central/main/foreign edits or merge; physicalradii/globalcompletion/E_QSS_old=null,L4=false. Stop after this single selected unit.
