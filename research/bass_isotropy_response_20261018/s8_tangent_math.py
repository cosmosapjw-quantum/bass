"""Analytic moving-support KL and collisionless-kernel derivatives for S8.

Only NEW explicitly isotropic birth rules are projected. These derivatives are
of the smooth positive KL optimum on an interior support, evaluated at the
stored binary64 approximate optimum; they do not differentiate stopping logic.
Signed alpha_b values are derivatives, never physical quadrature weights.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math
import numpy as np
import coupled_cohorts as cc
from angular_p24 import project as project_p24

INTERNAL_ATOL = 1e-15
COV_MIN_EIGENVALUE = 1e-10
COV_MAX_CONDITION = 1e8
TANGENT_MOMENT_ATOL = 1e-11
NORMALIZATION_DERIVATIVE_ATOL = 1e-12


class TangentDomainError(ArithmeticError):
    def __init__(self, label, **witness):
        self.record = {'kind': 'tangent_domain_or_conditioning', 'error': label, **witness}
        super().__init__(label)


def kernel_partials(d, mu):
    """Return R,D,R_d,D_d,R_mu,D_mu; complex-compatible for local verification."""
    mu = np.asarray(mu)
    a, c = np.exp(2*d), np.exp(-4*d)
    W, V = a*(1-mu*mu), c*mu*mu
    R = np.sqrt(W+V)
    D = (V-W/2)/R
    R_d = -2*D
    D_d = -(W*W+14*W*V+4*V*V)/(2*R**3)
    R_mu = mu*(c-a)/R
    D_mu = mu*(a+2*c)/R-D*mu*(c-a)/R**2
    return R, D, R_d, D_d, R_mu, D_mu


def angular_features(mu):
    mu = np.asarray(mu, dtype=float)
    z = mu*mu
    return np.column_stack(((3*z-1)/2, (35*z*z-30*z+3)/8))


def source_frame_derivatives(mu, prior):
    mu, prior = np.asarray(mu, dtype=float), np.asarray(prior, dtype=float)
    mu_b = -3*mu*(1-mu*mu)
    p2 = (3*mu*mu-1)/2
    prior_mass = math.fsum(prior)
    log_prior_b = 6*(p2-math.fsum(prior*p2)/prior_mass)
    f_b = np.column_stack((3*mu*mu_b, (35*mu**3-15*mu)*mu_b/2))
    return mu_b, log_prior_b, f_b


def feature_statistics(mu, alpha):
    alpha = np.asarray(alpha, dtype=float)
    f = angular_features(mu)
    mass = math.fsum(alpha)
    mean = np.array([math.fsum(alpha*f[:, j])/mass for j in range(2)])
    centered = f-mean
    cross = math.fsum(alpha*centered[:, 0]*centered[:, 1])/mass
    covariance = np.array([[math.fsum(alpha*centered[:, 0]**2)/mass, cross],
                           [cross, math.fsum(alpha*centered[:, 1]**2)/mass]])
    return f, mean, covariance


def checked_covariance_solve(covariance, rhs):
    covariance, rhs = np.asarray(covariance, dtype=float), np.asarray(rhs, dtype=float)
    if covariance.shape != (2, 2) or rhs.shape != (2,) or not np.isfinite(covariance).all() or not np.isfinite(rhs).all():
        raise TangentDomainError('S8_KL_COVARIANCE_INPUT')
    values = np.linalg.eigvalsh(covariance)
    condition = float(values[-1]/values[0]) if values[0] > 0 else math.inf
    if values[0] < COV_MIN_EIGENVALUE or condition > COV_MAX_CONDITION:
        raise TangentDomainError('S8_KL_COVARIANCE_RANK_OR_CONDITION',
                                 eigenvalues=values.tolist(), condition=condition if math.isfinite(condition) else None,
                                 minimum_required=COV_MIN_EIGENVALUE,
                                 maximum_condition=COV_MAX_CONDITION)
    answer = np.linalg.solve(covariance, rhs)
    return answer, values, condition


def implicit_kl_derivative(mu, alpha, multipliers, log_prior_b, features_b):
    """Differentiate <f>=0 with both moving features and the normalized prior.

    C lambda_b = -<f_b> - Cov(f, log(q)_b + lambda.f_b).
    alpha_b = alpha[(a-<a>)+(f-<f>).lambda_b].
    Actual centered moments are used, including the small nonlinear residual.
    """
    mu, alpha = np.asarray(mu, dtype=float), np.asarray(alpha, dtype=float)
    f_b = np.asarray(features_b, dtype=float)
    multipliers = np.asarray(multipliers, dtype=float)
    mass = math.fsum(alpha)
    f, mean, covariance = feature_statistics(mu, alpha)
    centered = f-mean
    a = np.asarray(log_prior_b, dtype=float)+f_b @ multipliers
    mean_a = math.fsum(alpha*a)/mass
    mean_fb = np.array([math.fsum(alpha*f_b[:, j])/mass for j in range(2)])
    cov_fa = np.array([math.fsum(alpha*centered[:, j]*(a-mean_a))/mass for j in range(2)])
    lambda_b, eigenvalues, condition = checked_covariance_solve(covariance, -mean_fb-cov_fa)
    alpha_b = alpha*(a-mean_a+centered @ lambda_b)
    derivative_residual = np.array([math.fsum(alpha_b*f[:, j]+alpha*f_b[:, j]) for j in range(2)])
    normalization_derivative = math.fsum(alpha_b)
    if (not np.isfinite(alpha_b).all() or max(abs(derivative_residual)) > TANGENT_MOMENT_ATOL or
        abs(normalization_derivative) > NORMALIZATION_DERIVATIVE_ATOL):
        raise TangentDomainError('S8_KL_DERIVATIVE_RESIDUAL',
                                 moment_derivative_residual=derivative_residual.tolist(),
                                 normalization_derivative=normalization_derivative)
    return alpha_b, {'lambda_b': lambda_b.tolist(), 'covariance': covariance.tolist(),
                     'covariance_eigenvalues': eigenvalues.tolist(), 'covariance_condition': condition,
                     'nonlinear_feature_mean_f64': mean.tolist(),
                     'moment_derivative_residual': derivative_residual.tolist(),
                     'normalization_derivative': normalization_derivative,
                     'linear_solve_residual': (covariance @ lambda_b+mean_fb+cov_fa).tolist()}


@dataclass(frozen=True)
class BirthDifferential:
    mu: np.ndarray
    alpha: np.ndarray
    mu_b: np.ndarray
    alpha_b: np.ndarray
    diagnostics: dict


def birth_differential(b, n, mode):
    if mode == 'source_frame_GL':
        mu, alpha = cc.source_frame_gl(n)
        zero = np.zeros_like(mu); zero.setflags(write=False)
        return BirthDifferential(mu, alpha, zero, zero,
                                 {'mode': mode, 'derivative_convention': 'fixed source-frame rays and weights',
                                  'exact_moment_certificate': cc.exact_birth_moment_certificate(mu, alpha, mode)})
    if mode != 'P24':
        raise ValueError('S8_ONLY_P24_OR_SOURCE_FRAME_GL')
    mu, prior = cc.lrs_rule(float(b), n)
    result = project_p24(mu, prior, atol=INTERNAL_ATOL)
    certificate = cc.exact_birth_moment_certificate(mu, result.weights, mode)
    if not certificate['pass']:
        raise TangentDomainError('S8_EXACT_NEW_BIRTH_MOMENT_EXCESS',
                                 b_birth=float(b), n=n, exact_moment_certificate=certificate)
    mu_b, score, f_b = source_frame_derivatives(mu, prior)
    alpha_b, diagnostics = implicit_kl_derivative(mu, result.weights, result.multipliers, score, f_b)
    diagnostics.update({'mode': mode, 'internal_projector_atol': INTERNAL_ATOL,
                        'multipliers': result.multipliers.tolist(), 'feasibility': asdict(result.feasibility),
                        'log_prior_b': score.tolist(), 'exact_moment_certificate': certificate,
                        'derivative_convention': 'smooth ideal positive KL branch at stored approximate optimum'})
    for arr in (mu, result.weights, mu_b, alpha_b):
        arr.setflags(write=False)
    return BirthDifferential(mu, result.weights, mu_b, alpha_b, diagnostics)


def primal_birth_rule(b, n, mode):
    """Same strict S8 physical rule, without requiring any tangent calculation."""
    if mode == 'source_frame_GL':
        return cc.source_frame_gl(n)
    if mode != 'P24':
        raise ValueError('S8_ONLY_P24_OR_SOURCE_FRAME_GL')
    mu, prior = cc.lrs_rule(float(b), n)
    result = project_p24(mu, prior, atol=INTERNAL_ATOL)
    certificate = cc.exact_birth_moment_certificate(mu, result.weights, mode)
    if not certificate['pass']:
        raise TangentDomainError('S8_EXACT_NEW_BIRTH_MOMENT_EXCESS',
                                 b_birth=float(b), n=n, exact_moment_certificate=certificate)
    return mu, result.weights
