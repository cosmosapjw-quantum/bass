# Independent S6 physics/math validation (read-and-run only)

Reviewer: separate subagent (physmath scientific-validator), 2026-10-19. 18 tests OK; independent scripts incl.
60/80-digit checks and owner fetch at 0e25846. No FAIL; all items low severity.

| Claim | Verdict | Note |
|---|---|---|
| S6.1 identity | PASS | k_0=0, odd l vanish; series-direct <=1.1e-28 |
| S6.2 rho(d)=sqrt(coth(3|d|/2)) | PASS | both signs of d |
| S6.3 coefficient bound | PASS / wording CONCERN | proof steps verified; |k_n|/bound<=0.06 vs 60-digit; rigorous modulo non-interval quadrature + 1e-25 floor (d=0.02, l>=52 30-digit noise covered by floor) |
| S6.4 refinement rate | prior PASS (independent 80-digit GL, ratios ->1; b=0.3,d=0.6 confirms min rule, 1.03 vs ~0.16) / P2,P24 CONCERN | holdout has one asymptotic pair per config; P24 ratios 0.78-0.84 at x=10-13; KL tilt adds essential singularity, rate relies on unstated lambda_n->0; ln rho* ~ e^{-3 max(|b|,|b+d|)} |
| S6.5 constraint-only guarantee | PASS / wording CONCERN | sufficient, not sharp (|M_l|=1 incompatible with M_2=0) |
| S6.6 rank-one certificate | PASS | 15p-5s+3=0 derivation, root location, binding, KL group ratios; extra cases {0,3/5}, {1/9,11/15}, c2+1 rejected |
| S6.7 spectral residual | PASS | owner Simpson-32/GL8/deposition normalisation match replica; <=2.2e-16 on 26 rows |
| S6.8 source age | identity and du^2 PASS / direction CONCERN | at out-of-sample x=1.5 leading P4 formula overestimates (0.82, 0.67); main cause l>=6 moments (30-55%) |
| S6.9 coupled feedback | derivation PASS, NOT_TESTED numerically | d(a^3 s)/dt=(8piG/3c^2)a^3 DeltaP; negative feedback |

Disposition: all four wording concerns applied to S6_THEORY_KO.md and S6_RESULTS_KO.md. No code change required.
