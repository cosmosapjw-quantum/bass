% XCAS-04 GNU Octave oracle.
% Numerical and matrix-structure evidence only; GNU Octave core is not
% promoted as an independent symbolic CAS.  The Octave symbolic package is
% deliberately not used because its algebra backend is SymPy.

format long g;

sample_count = 256;
tolerance = 5.0e-12;
max_clean_residual = 0.0;
hostile_jacobian_signal = 0.0;
hostile_sign_signal = 0.0;
hostile_missing_aberration_signal = 0.0;
max_direction_tangency = 0.0;
max_rei_delta_residual = 0.0;

for k = 1:sample_count
  mu = -0.95 + 1.90 * (k - 1) / (sample_count - 1);
  beta = 0.001 + 0.75 * mod(37 * k, sample_count) / sample_count;
  gamma = 1.0 / sqrt(1.0 - beta * beta);

  mu_tilde = (mu + beta) / (1.0 + beta * mu);
  mu_back = (mu_tilde - beta) / (1.0 - beta * mu_tilde);
  doppler_source = gamma * (1.0 + beta * mu);
  doppler_target = 1.0 / (gamma * (1.0 - beta * mu_tilde));
  jacobian = (1.0 - beta * beta) / ((1.0 + beta * mu)^2);
  jacobian_from_doppler = doppler_source^(-2);

  max_clean_residual = max(max_clean_residual, abs(mu_back - mu));
  max_clean_residual = max(max_clean_residual, abs(doppler_source - doppler_target));
  max_clean_residual = max(max_clean_residual, abs(jacobian - jacobian_from_doppler));

  hostile_jacobian_signal = max(hostile_jacobian_signal, abs(jacobian - doppler_source^(-1)));
  hostile_sign_signal = max(hostile_sign_signal, abs(doppler_source - gamma * (1.0 - beta * mu)));

  % Full d=1 blackbody pullback generator versus Doppler-only primitive.
  x = mu;
  h = 1.0e-7;
  source_temperature = @(z) 2.0 + 0.3 * z + 0.2 * z.^2 + 0.05 * z.^3;
  source_temperature_prime = @(z) 0.3 + 0.4 * z + 0.15 * z.^2;
  full_pullback = @(bb) (1.0 / ((1.0 / sqrt(1.0 - bb * bb)) * (1.0 - bb * x))) * ...
    source_temperature((x - bb) / (1.0 - bb * x));
  numeric_generator = (full_pullback(h) - full_pullback(-h)) / (2.0 * h);
  exact_generator = x * source_temperature(x) - (1.0 - x * x) * source_temperature_prime(x);
  doppler_only_generator = x * source_temperature(x);

  max_clean_residual = max(max_clean_residual, abs(numeric_generator - exact_generator));
  hostile_missing_aberration_signal = max(
    hostile_missing_aberration_signal,
    abs(exact_generator - doppler_only_generator)
  );

  % Photon direction-flow tangency on a deterministic unit-sphere sample.
  raw_e = [cos(0.31 * k); sin(0.47 * k); cos(0.73 * k)];
  e = raw_e / norm(raw_e);
  sigma = [0.20, 0.03, -0.04; 0.03, -0.11, 0.02; -0.04, 0.02, -0.09];
  aB = [0.07; -0.05; 0.02];
  omega = [0.04; 0.01; -0.03];
  nB = [0.12, 0.02, 0.00; 0.02, -0.04, 0.01; 0.00, 0.01, -0.08];
  sigma_ee = e' * sigma * e;
  V = (sigma_ee + aB' * e) * e - sigma * e - aB ...
      + cross(omega, e) - cross(e, nB * e);
  max_direction_tangency = max(max_direction_tangency, abs(e' * V));

  % Exact semantic target checked numerically: (-H)-(-H-sigmaEE)=sigmaEE.
  H = 0.8 + 0.001 * k;
  rei_delta = (-H) - (-H - sigma_ee);
  max_rei_delta_residual = max(max_rei_delta_residual, abs(rei_delta - sigma_ee));
endfor

% d=1 finite Galerkin generator blocks must be skew-symmetric.
max_d1_skew = 0.0;
min_d0_non_skew = Inf;
ell_max = 12;
for m = 0:4
  n = ell_max - m + 1;
  G1 = zeros(n, n);
  G0 = zeros(n, n);
  for ell = m:ell_max
    col = ell - m + 1;
    if ell + 1 <= ell_max
      C_up = sqrt(((ell + 1)^2 - m^2) / (4 * (ell + 1)^2 - 1));
      G1(col + 1, col) = (ell + 1) * C_up;
      G0(col + 1, col) = ell * C_up;
    endif
    if ell - 1 >= m
      C_down = sqrt((ell^2 - m^2) / (4 * ell^2 - 1));
      G1(col - 1, col) = -ell * C_down;
      G0(col - 1, col) = -(ell + 1) * C_down;
    endif
  endfor
  max_d1_skew = max(max_d1_skew, norm(G1 + G1', Inf));
  min_d0_non_skew = min(min_d0_non_skew, norm(G0 + G0', Inf));
endfor

status = (
  max_clean_residual < tolerance &&
  max_direction_tangency < tolerance &&
  max_rei_delta_residual < tolerance &&
  max_d1_skew < tolerance &&
  hostile_jacobian_signal > 1.0e-6 &&
  hostile_sign_signal > 1.0e-6 &&
  hostile_missing_aberration_signal > 1.0e-6 &&
  min_d0_non_skew > 1.0e-6
);

receipt = struct();
receipt.status = ternary(status, 'PASS', 'FAIL');
receipt.engine = 'GNU Octave';
receipt.engine_role = 'INDEPENDENT_NUMERICAL_AND_MATRIX_ORACLE_NOT_SYMBOLIC_CAS';
receipt.samples = sample_count;
receipt.tolerance = tolerance;
receipt.max_clean_residual = max_clean_residual;
receipt.max_direction_tangency = max_direction_tangency;
receipt.max_rei_delta_residual = max_rei_delta_residual;
receipt.max_d1_skew_residual = max_d1_skew;
receipt.min_d0_non_skew_signal = min_d0_non_skew;
receipt.hostile_jacobian_signal = hostile_jacobian_signal;
receipt.hostile_sign_signal = hostile_sign_signal;
receipt.hostile_missing_aberration_signal = hostile_missing_aberration_signal;
receipt.authority_effect = 'NONE_EXTERNAL_ORACLE';
receipt.symbolic_backend = 'NONE';
receipt.note = 'Octave symbolic package is excluded from independent-engine count because it delegates algebra to SymPy.';

disp(jsonencode(receipt));
if !status
  exit(1);
endif

function out = ternary(condition, yes_value, no_value)
  if condition
    out = yes_value;
  else
    out = no_value;
  endif
endfunction
