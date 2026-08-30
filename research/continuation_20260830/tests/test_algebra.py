from fractions import Fraction as Q
import numpy as np
import pytest
from algebra import CausalSystem,original_residual_bridge,linear_goal_error


def fixture(different=False):
    rng=np.random.default_rng(8042);s,n=4,3
    W=np.array([[2.,.5,0.],[0.,3.,-.2],[.1,0.,4.]])
    diag=np.tile(W,(s,1,1))
    if different:diag[2]*=2
    lower=np.zeros((s,s,n,n))
    for i in range(s):
        for j in range(i):lower[i,j]=rng.normal(size=(n,n))*.1
    return CausalSystem(diag,lower),rng.normal(size=(s,n))

@pytest.mark.parametrize('different',[False,True])
def test_forward_and_transpose_actual_matrix(different):
    s,b=fixture(different)
    for tr in [False,True]:
        got=s.solve(b,transpose=tr);A=s.dense().T if tr else s.dense()
        np.testing.assert_allclose(got.value.ravel(),np.linalg.solve(A,b.ravel()),rtol=2e-13,atol=1e-14)
        assert got.relative_backward_error<2e-14
    assert s.factorization_count==(2 if different else 1)


def test_adjoint_predicts_actual_linear_goal_error():
    s,b=fixture();x=s.solve(b).value.copy();x[2,1]+=1e-5;g=np.arange(12).reshape(4,3)
    predicted,adjoint=linear_goal_error(s,b,x,g)
    actual=np.vdot(g,s.solve(b).value-x)
    assert abs(predicted-actual)<1e-13
    assert adjoint.factorization_count==1


def test_same_diagonal_claim_rejects_upper_leakage():
    s,b=fixture();lower=s.lower.copy();lower[0,3,0,0]=1e-20
    with pytest.raises(ValueError):CausalSystem(s.diagonal,lower)


def test_small_projection_can_change_original_solution():
    A=np.eye(8)-100*np.eye(8,k=-1);B=A.copy();B[0,-1]=1e-14;b=np.eye(8)[0];z=100.**np.arange(8)
    r=original_residual_bridge(B,b,A,b,z)
    np.testing.assert_allclose(r['proposal_residual'],0,atol=0)
    assert abs(r['original_residual'][0]-1)<1e-14
    assert r['bridge_difference']<1e-14
    assert r['claim']=='NO_FORWARD_OR_NONLINEAR_CERTIFICATE'
    # Exact original solution is z/2 (independent rational arithmetic).
    q=[Q(100)**i for i in range(8)]
    assert Q(1,10**14)*q[-1]==1


def test_zero_rhs_is_not_nan():
    s,b=fixture();got=s.solve(np.zeros_like(b))
    assert got.relative_backward_error==0 and np.count_nonzero(got.value)==0


def test_singular_and_nonfinite_rejected():
    with pytest.raises(ValueError):CausalSystem(np.zeros((1,2,2)),np.zeros((1,1,2,2)))
    s,b=fixture();b[0,0]=np.nan
    with pytest.raises(ValueError):s.solve(b)


def test_inputs_copied_and_returned_arrays_readonly():
    d=np.tile(np.eye(2),(2,1,1));l=np.zeros((2,2,2,2));s=CausalSystem(d,l);d[:]=99
    assert s.solve(np.ones((2,2))).value[0,0]==1
    with pytest.raises(ValueError):s.diagonal[0,0,0]=3


def test_backward_error_scaling_overflow_does_not_false_pass():
    system=CausalSystem(np.array([[[1e308]]]),np.zeros((1,1,1,1)))
    with pytest.raises(ArithmeticError,match='scaling overflow'):
        with np.errstate(over='ignore'):system.solve([[1e308]])
