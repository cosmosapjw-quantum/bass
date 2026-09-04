% Numerical BG-02 off-shell identities for GNU Octave.
% This is an auxiliary audit; the authoritative symbolic implementation is WL/xAct.
format long e;
max_residual = 0.0;
for i = 1:32
  v = zeros(1,9);
  for j = 1:9
    v(j) = (i + j - 1)/(7 + 2*(j - 1));
  endfor
  R3=v(1); H=v(2); sigma2=v(3); divA=v(4); A2=v(5);
  Lambda=v(6); kappaG=v(7); rho=v(8); p=v(9);
  Hres=(R3+6*H^2-sigma2-2*Lambda-2*kappaG*rho)/2;
  Ftrace=-R3/12-3*H^2/2-sigma2/4+(divA+A2)/3+Lambda/2-kappaG*p/2;
  FADM=-R3/3-3*H^2+(divA+A2)/3+kappaG*(rho-p)/2+Lambda;
  FRay=-H^2-sigma2/3+(divA+A2)/3-kappaG*(rho+3*p)/6+Lambda/3;
  r=[FADM-Ftrace+Hres/2, Ftrace-FRay+Hres/6, FADM-FRay+2*Hres/3];
  max_residual=max(max_residual,max(abs(r)));
endfor
fprintf('BG02_OCTAVE_MAX_RESIDUAL=%.17e\n',max_residual);
if max_residual > 1e-12
  error('BG02 off-shell identity residual exceeded tolerance');
endif
