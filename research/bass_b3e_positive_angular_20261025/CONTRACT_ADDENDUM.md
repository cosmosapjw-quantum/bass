# B3e R6 implementation clarifications

This addendum records the independent R6 findings before numerical execution.
The frozen equations, fixtures, tolerances and admitted scope are unchanged.

1. The mixture Loewner matrix is the positive sum
   M_bound_mix=sum(c_a*beta_a*M_a). The pressure error must be compared with
   +/-M_bound_mix, using the stated2e-12*F_reference eigenvalue allowance.
   There is no averaged R or common fictitious beta.
2. Frame invariance comparisons for dimensional F_lower, B_F, B_T and M
   use the same positive cohort reference-energy scale. Integer selectedK
   equality remains exact; dimensionless relative bounds use their stated
   absolute roundoff gate512eps. A dimensional bound is not divided by its
   own possibly zero value in the isotropic case.
3. The output scope wording is19 main endpoints (14 inherited+5new), plus
   two canonical orientation checks and one mixture. Only14 are inherited.

Independent R6 is PASS_SCOPED and authorizes the next bounded implementation,
preexecution code review and S0 preparation checkpoint. Scientific execution
begins after root GO and actual S0 backup ACK.
