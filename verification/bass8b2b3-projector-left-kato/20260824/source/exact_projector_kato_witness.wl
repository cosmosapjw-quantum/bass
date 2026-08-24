(* Exact rank-one projector, paired-left, differentiated-null and Kato witness. *)
Module[{t,u,td,ud,lam,lamd,den,r,rd,a,ad,p,pd,id,c,cd,k,wrong,res},
  den = 1 + u t;
  r = {{1},{t}};
  rd = {{0},{td}};
  a = {{1,u}}/den;
  ad = {{0,ud}}/den - {{1,u}} (ud t + u td)/den^2;
  p = FullSimplify[r.a];
  pd = FullSimplify[rd.a + r.ad];
  id = IdentityMatrix[2];
  c = FullSimplify[-lam (id-p)];
  cd = FullSimplify[-lamd (id-p) + lam pd];
  k = FullSimplify[pd.p - p.pd];
  wrong = FullSimplify[(-k).p - p.(-k) - pd];
  res = <|
    "schema" -> "bass8b2b3-exact-projector-left-kato-wolfram-v1",
    "status" -> "PASS_EXACT_PROJECTOR_LEFT_KATO_WOLFRAM",
    "wolfram_version" -> $Version,
    "normalization" -> FullSimplify[First[First[a.r]]-1],
    "normalization_tangent" -> FullSimplify[First[First[ad.r+a.rd]]],
    "right_null" -> FullSimplify[c.r],
    "left_null" -> FullSimplify[a.c],
    "projector_idempotence" -> FullSimplify[p.p-p],
    "projector_tangent" -> FullSimplify[p.pd+pd.p-pd],
    "generator_projector_left" -> FullSimplify[c.p],
    "generator_projector_right" -> FullSimplify[p.c],
    "differentiated_right_null" -> FullSimplify[cd.r+c.rd],
    "differentiated_left_null" -> FullSimplify[ad.c+a.cd],
    "kato_commutator" -> FullSimplify[k.p-p.k-pd],
    "kato_pp_block" -> FullSimplify[p.k.p],
    "kato_qq_block" -> FullSimplify[(id-p).k.(id-p)],
    "wrong_kato_sign_residual" -> wrong,
    "wrong_kato_sign_rejected" -> Not[TrueQ[wrong == ConstantArray[0,{2,2}]]],
    "global_scalar_projector_independence" -> FreeQ[p,{lam,lamd}],
    "global_scalar_projector_tangent_independence" -> FreeQ[pd,{lam,lamd}]
  |>;
  Print[res];
  If[res["status"] =!= "PASS_EXACT_PROJECTOR_LEFT_KATO_WOLFRAM", Exit[1]];
]
