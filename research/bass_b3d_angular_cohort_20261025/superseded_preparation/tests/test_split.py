"""New model contract checks; no parent campaign/test replay."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import copy
from dataclasses import replace
import numpy as np
import emission_split as es


def expect_rejected(call):
    try:call()
    except (ValueError,ArithmeticError):return
    raise AssertionError('expected rejection')


def main():
    m=es.SplitModel();row=m.history[0]
    assert row['packets']==0 and row['n_gamma']==0 and row['rho_gamma']==0
    assert row['constraint']<1e-14 and row['atom_count_error']==0
    original=copy.deepcopy(m.__dict__)
    for kw in [dict(f_plus=.01),dict(frame='tilted'),dict(owner_mode='native')]:
        expect_rejected(lambda kw=kw:m.react(.001,**kw))
        assert m.reactions==0 and m.x==es.X0 and len(m.k_birth)==0
    expect_rejected(lambda:es.SplitModel(initial_photons={'blue':True}))
    bad=es.SplitModel();bad.y[1]=-1.1
    expect_rejected(lambda:bad.components(bad.y))
    # Failed thick gate in the unchanged actual source owner.
    state,source,ph,N,nu,nl=m.components(m.y)
    line=es.fx.owner.LineState(es.CARD.id,es.CARD.population_scope,nl,nu,1e30,0.,np.diag(es.S0),'THICK_GATE_NEGATIVE')
    expect_rejected(lambda:es.fx.gross_counts(line,1e-35))
    assert len(m.k_birth)==0 and m.reactions==0
    m.react(.001);assert len(m.k_birth)==14
    tx=m.transactions[-1]
    assert tx['down']>0 and tx['up']==0 and tx['rest_energy_change']==0
    assert np.all(np.array(tx['outgoing_U'])==0) and np.all(np.array(tx['outgoing_J'])==0)
    before=m.photons(m.y);testy=m.y.copy();testy[3]+=.003;testy[4]+=.001;testy[5]-=.0004
    after=m.photons(testy)
    beta=es.diagonal(.001,-.0004)
    assert np.allclose(after.k,before.k*np.exp(-.003-beta),rtol=256*np.finfo(float).eps,atol=0)
    assert np.allclose(after.w,before.w*np.exp(-.009),rtol=256*np.finfo(float).eps,atol=0)
    assert np.max(np.linalg.norm(after.k,axis=1))<1
    state,source,ph,N,nu,nl=m.components(m.y)
    rho,flux,p,pi=es.fx.photon_moments(ph)
    assert np.array_equal(state.flux[2],flux) and np.array_equal(source.pi[2],pi)
    assert abs(np.trace(pi))<1e-30 and state.rho[0]>0 and state.rho[1]>0
    # Current epoch and stock rejection in actual transaction; retain input bytes.
    ident=m.identity();state,source,ph,N,nu,nl=m.components(m.y,ident)
    line=es.fx.owner.LineState(es.CARD.id,es.CARD.population_scope,nl,nu,state.h/es.SCALE.time_s,0.,state.sigma/state.h,'STALE_STOCK_NEGATIVE')
    pop=es.fx.PopulationStock(ident,nu*1.01,nl,m.applied)
    expect_rejected(lambda:es.fx.commit_emission(line=line,source_identity=ident,state_identity=ident,
        state=state,source=source,population=pop,photons=ph,scale=es.SCALE,Pstar=es.PSTAR,dt_s=1e-5,
        transfer_id='stale',atomic_sector=0,photon_sector=2))
    correctpop=es.fx.PopulationStock(ident,nu,nl,m.applied)
    wrongstate=copy.deepcopy(state);wrongstate.h*=1.01
    expect_rejected(lambda:es.fx.commit_emission(line=line,source_identity=ident,state_identity=ident,
        state=wrongstate,source=source,population=correctpop,photons=ph,scale=es.SCALE,Pstar=es.PSTAR,dt_s=1e-5,
        transfer_id='stale-geometry',atomic_sector=0,photon_sector=2))
    expect_rejected(lambda:es.fx.commit_emission(line=line,source_identity=ident,state_identity=replace(ident,epoch='old'),
        state=state,source=source,population=correctpop,photons=ph,scale=es.SCALE,Pstar=es.PSTAR,dt_s=1e-5,
        transfer_id='stale-epoch',atomic_sector=0,photon_sector=2))
    assert np.array_equal(m.y,original['y']) and m.reactions==1
    print('PASS_SCOPED: vacuum/initial constraints, three sectors, positive actual emission, finite donor, exact characteristics, zero-blue/owner/frame/directional/thick/stale-stock rejection and no mutation')

if __name__=='__main__':main()
