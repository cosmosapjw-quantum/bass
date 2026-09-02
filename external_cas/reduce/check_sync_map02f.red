off nat;
on rounded;

operator tpoly;

procedure checkzero(id, value);
  if value = 0 then << prin2 "CHECK|"; prin2 id; prin2t "|PASS" >>
  else << prin2 "CHECK|"; prin2 id; prin2 "|FAIL|"; prin2t value >>;

procedure checknonzero(id, value);
  if value neq 0 then << prin2 "MUTATION|"; prin2 id; prin2t "|PASS" >>
  else << prin2 "MUTATION|"; prin2 id; prin2t "|FAIL|0" >>;

checkzero("I01_REGULAR_ABERRATION_COEFFICIENT",
  g^2*(g^2-1)-(g-1)*g^2*(g+1));
checkzero("I02_AXIAL_ABERRATION_UNIT_NORM",
  (x+b)^2+(1-x^2)*(1-b^2)-(1+b*x)^2);
checkzero("I03_SOLID_ANGLE_JACOBIAN",
  (1+b*x)-b*(x+b)-(1-b^2));
checkzero("I08_REI_EXACT_SIGMA_RESIDUAL",
  ((-h)-(-h-sigmaee))-sigmaee);
checkzero("I09_DIRECTION_FLOW_TANGENCY",
  (e2-1)*(see+ae)-(e2-1)*(see+ae));
checkzero("I10_SCREEN_U1_COVARIANCE",
  (pdot-2*ii*chid*pplus)+2*ii*(omega+chid)*pplus-(pdot+2*ii*omega*pplus));

checknonzero("M02_WRONG_JACOBIAN_POWER", b*(1-x^2));
checknonzero("M04_REI_WRONG_SIGN", -2*sigmaee);
checknonzero("M05_REI_WRONG_FACTOR", sigmaee);
checknonzero("M06_REI_FOREIGN_CONSTANT", 1-sigmaee);
checknonzero("M07_DROP_DIRECTION_RADIAL_COMPENSATOR", -see-ae);
checknonzero("M08_SCREEN_CONNECTION_SIGN", -4*ii*chid*pplus);

prin2t "STATUS|PASS";
quit;
