# B3f R6 clarifications before execution

The equations, fixtures, tolerance and scope in FROZEN_CONTRACT.md are unchanged.

1. Nominal density n0 is strictly positive for a relative certificate. The
   second endpoint may have n1=0; its absolute finite pair bound remains valid,
   while a relative claim needs a positive true-energy lower bound. Negative
   density is rejected. The nonpositive-density focused test applies to n0.
2. A containing physical ball must explicitly satisfy the supplied endpoint
   differences ||DeltaR||2<=eR, ||DeltaS||F<=eS and |Delta n|<=en. Then
   h_pair<=h_ball, |DeltaW|<=deltaW, W1<=Wmax and F_up1<=b+eR prove
   U_pair<=U_ball. Compare any dimensional dominance residual on the positive
   nominal/reference energy scale, never by dividing by a possibly zero bound.
3. The numerical reserve is an absolute eps_fp*W0*F_up0 term before division
   by L0-U. Its empirical status is separate from the ideal exact-arithmetic
   theorem and from the separately measured truth-reference error.

These are R6 implementation clarifications. The independent review and its
exact input identity are in reviews/R6_CONTRACT_REVIEW.md. Scientific Python
execution remains pending preexecution code review and actual S0 preservation.
