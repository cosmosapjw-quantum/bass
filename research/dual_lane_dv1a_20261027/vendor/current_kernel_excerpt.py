"""Executable-body transcription from pinned live GitHub reads.
This is NOT a replacement repository file. Used only for AST identity comparison.
Sources: hierarchy.py:327-391 and characteristics.py:47-75 at cc602e2.
Docstrings/comments are excluded from the identity relation.
"""
def _contract_one(J, sigma):
    J = np.asarray(J, float)
    l = J.ndim
    letters = "ijklmn"[:l - 1]
    return np.einsum(f"a{letters},ba->{letters}b", J, sigma)

def _contract_two(J, sigma):
    J = np.asarray(J, float)
    l = J.ndim - 2
    letters = "ijklmn"[:l]
    return np.einsum(f"ab{letters},ab->{letters}", J, sigma)

def _outer_sigma(J, sigma):
    return pstf(np.multiply.outer(np.asarray(J, float), sigma))

def hierarchy_rhs(J, H, sigma, l, i, signs=None):
    if signs is None:
        signs = SIGMA_SIGNS
    sigma = np.asarray(sigma, float)
    n = l + 2 * i
    def get(ll, ii):
        v = J.get((ll, ii))
        if v is None:
            raise KeyError(f"J[({ll},{ii})] 없음 — hierarchy_rhs 는 이웃을 요구한다")
        return v
    out = -H * ((3.0 + n) * np.asarray(get(l, i), float)
                + (1.0 - n) * np.asarray(get(l, i + 1), float))
    if l >= 1:
        cA = l / (2.0 * l + 3.0)
        tA = ((2.0 * n + 3.0) * _contract_one(get(l, i), sigma)
              + (2.0 - 2.0 * n) * _contract_one(get(l, i + 1), sigma))
        out = out - signs["A"] * cA * (pstf(tA) if l >= 2 else tA)
    cB_prev = l - n
    tB = (n - 1.0) * _contract_two(get(l + 2, i), sigma)
    if cB_prev != 0.0:
        tB = tB + cB_prev * _contract_two(get(l + 2, i - 1), sigma)
    out = out - signs["B"] * tB
    if l >= 2:
        cC = l * (l - 1.0) / (4.0 * l * l - 1.0)
        tC = ((n - 1.0) * _outer_sigma(get(l - 2, i + 2), sigma)
              - (l + n + 1.0) * _outer_sigma(get(l - 2, i + 1), sigma))
        out = out - signs["C"] * cC * tC
    return pstf(out) if l >= 2 else out

def rhs_split_ref(ehat, lnp, mass, bg: Background):
    e = np.asarray(ehat, float)
    S, N, A = unpack_sym(bg.sigma), unpack_sym(bg.n), bg.a
    p = np.exp(lnp)
    pe = p / np.sqrt(mass * mass + p * p)
    se = S @ e
    ese = float(e @ se)
    de = (-(se - ese * e) + np.cross(bg.rot, e)
          + pe * (np.cross(N @ e, e) - (A - float(A @ e) * e)))
    return de, -(bg.h + ese)
