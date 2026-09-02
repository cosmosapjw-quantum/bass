% XCAS-01 independent REDUCE oracle.
off nat;
off rounded;

procedure assertzero(expr,label);
  begin scalar r;
    r := factor expr;
    if r neq 0 then rederr list("FAIL",label,"residual",r);
    write "PASS ",label;
  end;

ab := (mu+be)/(1+be*mu);
abi := (xx-be)/(1-be*xx);
assertzero(sub(xx=ab,abi)-mu,"aberration_inverse");
assertzero(df(ab,mu)-(1-be^2)/(1+be*mu)^2,"solid_angle_jacobian");

ff := 1+xx+xx^2;
xsrc := xx-eps*(1-xx^2);
full := (1+eps*xx)*(1+xsrc+xsrc^2);
gfull := coeff(full,eps,1);
expected := xx*ff-(1-xx^2)*df(ff,xx);
assertzero(gfull-expected,"weighted_pullback_generator_d1");
assertzero((gfull-xx*ff)+(1-xx^2)*df(ff,xx),"aberration_advection_gap");

write "PASS_REDUCE_XCAS01";
quit;
