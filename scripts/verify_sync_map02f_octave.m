% Independent GNU Octave numerical oracle for SYNC-MAP-02F.
% This does not parse repository Python/Wolfram code and has authority effect NONE.

more off;
format long e;
rand("seed", 20260902);
randn("seed", 20260902);

tol = 5.0e-12;
max_norm = 0.0;
max_inverse = 0.0;
max_jacobian = 0.0;
max_planck = 0.0;
max_tangent = 0.0;

betas = [0.0, 1.0e-8, 1.0e-3, 0.1, 0.5, 0.8];
mus = [-0.97, -0.5, 0.0, 0.33, 0.91];

for beta = betas
  gamma = 1.0 / sqrt(1.0 - beta * beta);
  for mu = mus
    D = gamma * (1.0 + beta * mu);
    mu_tilde = (mu + beta) / (1.0 + beta * mu);
    mu_back = (mu_tilde - beta) / (1.0 - beta * mu_tilde);
    jacobian = (1.0 - beta * beta) / ((1.0 + beta * mu)^2);
    max_inverse = max(max_inverse, abs(mu_back - mu));
    max_jacobian = max(max_jacobian, abs(jacobian - D^(-2)));
    max_norm = max(max_norm, abs(mu_tilde^2 + (1.0 - mu_tilde^2) - 1.0));

    nu = 100.0e9;
    T = 2.72548;
    hP = 6.62607015e-34;
    kB = 1.380649e-23;
    x = hP * nu / (kB * T);
    x_tilde = hP * (D * nu) / (kB * (D * T));
    max_planck = max(max_planck, abs(x_tilde - x));
  endfor
endfor

for sample = 1:256
  e = randn(3, 1);
  e = e / norm(e);
  raw = randn(3, 3);
  sigma = 0.5 * (raw + raw');
  sigma = sigma - trace(sigma) * eye(3) / 3.0;
  rawN = randn(3, 3);
  nB = 0.5 * (rawN + rawN');
  aB = randn(3, 1);
  Omega = randn(3, 1);
  scalar = e' * sigma * e + aB' * e;
  V = scalar * e - sigma * e - aB + cross(Omega, e) - cross(e, nB * e);
  max_tangent = max(max_tangent, abs(e' * V));
endfor

clean_max = max([max_norm, max_inverse, max_jacobian, max_planck, max_tangent]);

% Hostile controls must be separated from roundoff.
beta = 0.2;
mu = 0.4;
gamma = 1.0 / sqrt(1.0 - beta * beta);
D = gamma * (1.0 + beta * mu);
correct_jac = D^(-2);
wrong_jac = D^(-1);
wrong_sign_D = gamma * (1.0 - beta * mu);
hostile_jacobian_signal = abs(wrong_jac - correct_jac);
hostile_sign_signal = abs(wrong_sign_D - D);

if clean_max > tol
  error("SYNC_MAP_02F_OCTAVE_FAIL: clean residual exceeds tolerance");
endif
if hostile_jacobian_signal < 1.0e-4
  error("SYNC_MAP_02F_OCTAVE_FAIL: wrong Jacobian power escaped");
endif
if hostile_sign_signal < 1.0e-4
  error("SYNC_MAP_02F_OCTAVE_FAIL: wrong Doppler sign escaped");
endif

printf('{"status":"PASS","samples":256,"tolerance":%.17g,"max_clean_residual":%.17g,"hostile_jacobian_signal":%.17g,"hostile_sign_signal":%.17g,"authority_effect":"NONE"}\n', tol, clean_max, hostile_jacobian_signal, hostile_sign_signal);
