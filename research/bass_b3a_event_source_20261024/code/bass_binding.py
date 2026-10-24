"""Pure BASS transfer attachment; no pressure-rate addition or stock update."""
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys
import numpy as np
from event_measure import C,G,GrossEventBundle,Identity,real_array,positive
from rec_adapter import OWNER,INVARIANT_CLOCK

path = Path(__file__).resolve().parents[1]/'vendor/bass/core.py'
spec = importlib.util.spec_from_file_location('b3a_unchanged_bass_core',path)
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)


@dataclass(frozen=True)
class BassRatePair:
    U: np.ndarray
    J: np.ndarray
    PiRate_hat_radiation: np.ndarray
    identity: Identity
    atomic_energy_ledger: str = 'internal_excitation_energy'
    thermal_energy_rate: float = 0.
    ionization_yield: float = 0.
    free_electron_yield: float = 0.


def bass_rate_pair(bundle, *, length_m):
    if not isinstance(bundle,GrossEventBundle) or bundle.down.identity.owner != OWNER or bundle.down.identity.clock != INVARIANT_CLOCK:
        raise ValueError('compatible detached gross event owner and invariant proper clock required')
    L = positive(length_m,'L')
    net = bundle.net_moments()
    factor = 8*np.pi*G/C**4*L**3/C
    transfer = factor*net.cQ_J_m3_s
    return BassRatePair(np.array([transfer[0],-transfer[0]]),np.array([transfer[1:],-transfer[1:]]),
                        factor*net.PiRate_J_m3_s,net.identity)


@dataclass(frozen=True)
class Attachment:
    source: object
    rates: BassRatePair
    applied_transfer_keys: frozenset


def attach_source(bundle, *, length_m, pressure, pi, expected_identity,
                  transfer_id, applied_transfer_keys=frozenset(), positive_domain=None):
    if not isinstance(expected_identity,Identity) or bundle.down.identity != expected_identity:
        raise ValueError('stale or incompatible owner/epoch/frame/clock identity')
    if not isinstance(transfer_id,str) or not transfer_id:
        raise ValueError('explicit transfer id required')
    # A physical source charge survives observer/frame representation changes.
    key = (expected_identity.owner,expected_identity.epoch,transfer_id)
    if key in applied_transfer_keys:
        raise ValueError('duplicate transfer refused')
    rates = bass_rate_pair(bundle,length_m=length_m)
    if np.any(rates.U) or np.any(rates.J):
        if not callable(positive_domain) or positive_domain(rates) is not True:
            raise ValueError('explicit successful positive-domain callback required for nonzero binding')
    p = real_array(pressure,'current state pressure',(2,))
    stress = real_array(pi,'current state pi',(2,3,3))
    source = core.Source(p.copy(),stress.copy(),rates.U.copy(),rates.J.copy())
    source.arrays(2,balanced=True)
    return Attachment(source,rates,frozenset(applied_transfer_keys)|{key})
