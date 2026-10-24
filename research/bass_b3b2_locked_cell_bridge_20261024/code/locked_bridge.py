"""REC locked-cell INITIAL-DATA inventory ↔ BASS massless state packets.

No IVP, event rate, collision operator, boundary reconstruction or source object.
Physical energy is exclusively c * the saved network momentum_scale.
"""
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import numpy as np
from vendor import kinetic

C = 299792458.0
EPS = np.finfo(float).eps
SUM_TOL = 512 * EPS
ROUNDTRIP_TOL = 128 * EPS
ROOT = Path(__file__).resolve().parents[1]


def real(value, name):
    if np.iscomplexobj(value):
        raise ValueError(name + ': real input required')
    try:
        out = np.asarray(value, dtype=float)
    except (TypeError, OverflowError) as exc:
        raise ValueError(name + ': real numeric input required') from exc
    if not np.all(np.isfinite(out)):
        raise ValueError(name + ': finite input required')
    return out


def positive(value, name):
    out = real(value, name)
    if np.any(out <= 0):
        raise ValueError(name + ': strictly positive input required')
    return out


def multiply_positive(a, b, name):
    """Allow true zeros, but reject loss of any positive product."""
    with np.errstate(over='ignore', invalid='ignore', under='ignore'):
        out = np.asarray(a) * np.asarray(b)
    if not np.all(np.isfinite(out)) or np.any((np.asarray(a) > 0) & (np.asarray(b) > 0) & (out <= 0)):
        raise ValueError(name + ': nonfinite arithmetic or positive underflow')
    return out


@dataclass(frozen=True)
class Units:
    kappa: float
    L: float
    Pstar: float

    def __post_init__(self):
        for name in ('kappa', 'L', 'Pstar'):
            x = positive(getattr(self, name), name)
            if x.shape != ():
                raise ValueError(name + ': scalar required')
            object.__setattr__(self, name, float(x))
        self.alpha
        self.weight_factor

    @property
    def alpha(self):
        return float(multiply_positive(multiply_positive(self.kappa, self.L, 'kappa L'), self.L, 'alphaL'))

    @property
    def weight_factor(self):
        return float(multiply_positive(multiply_positive(self.alpha, C, 'alphaL c'), self.Pstar, 'weight scale'))


@dataclass(frozen=True)
class LockedGrid:
    G: np.ndarray
    p: np.ndarray
    directions: np.ndarray
    A: np.ndarray
    cell_labels: tuple
    intervals: np.ndarray
    input_identity: dict = field(default_factory=dict)

    def __post_init__(self):
        for name in ('G', 'p', 'A'):
            object.__setattr__(self, name, positive(getattr(self, name), name).copy())
        for name in ('directions', 'intervals'):
            object.__setattr__(self, name, real(getattr(self, name), name).copy())
        if self.G.ndim != 1 or self.A.ndim != 1:
            raise ValueError('one-dimensional G and A required')
        n, m = len(self.G), len(self.A)
        if n == 0 or m == 0 or self.G.shape != (n,) or self.p.shape != (n,) or self.directions.shape != (m, 3) or self.intervals.shape != (n, 2):
            raise ValueError('incompatible grid shapes')
        if len(self.cell_labels) != n or len(set(self.cell_labels)) != n or np.any(self.intervals[:, 1] <= self.intervals[:, 0]):
            raise ValueError('unique cell labels and increasing intervals required')
        if abs(float(np.sum(self.A))-1) > ROUNDTRIP_TOL:
            raise ValueError('general bridge requires already normalized angular weights')
        if np.max(np.abs(np.sum(self.directions**2, axis=1)-1)) > ROUNDTRIP_TOL:
            raise ValueError('unit directions required')
        multiply_positive(C, self.p, 'physical energy')

    @property
    def shape(self):
        return (len(self.G), len(self.A))

    @property
    def identity(self):
        h = hashlib.sha256()
        for name in ('G', 'p', 'directions', 'A', 'intervals'):
            h.update(getattr(self, name).tobytes())
        h.update(json.dumps([list(self.cell_labels), self.input_identity], sort_keys=True).encode())
        return h.hexdigest()


@dataclass(frozen=True)
class PacketState:
    k: np.ndarray
    w: np.ndarray
    mass: np.ndarray
    units: Units
    grid_identity: str
    cell_labels: tuple
    angular_labels: tuple
    frame: np.ndarray = field(default_factory=lambda: np.eye(4))


def load_actual_inputs(directory=ROOT / 'inputs'):
    directory = Path(directory)
    manifest = json.loads((directory / 'IDENTITY.json').read_text())
    identity = {}
    for item in manifest['source_inputs']:
        name = Path(item['path']).name
        raw = (directory / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != item['sha256'] or len(raw) != item['size']:
            raise ValueError('actual input byte identity mismatch: ' + name)
        identity[name] = digest
    with np.load(directory / 'z1100_direct_network_node.npz', allow_pickle=False) as node, \
         np.load(directory / 'pr01c_background_snapshots_v048.npz', allow_pickle=False) as angular, \
         np.load(directory / 'pr05c2c1b2b1e0_source_derived_parent_v073.npz', allow_pickle=False) as parent:
        raw_A = positive(angular['angular_weights'], 'REC raw angular weights')
        raw_sum = float(np.sum(raw_A))
        if not np.isfinite(raw_sum) or raw_sum <= 0:
            raise ValueError('invalid REC raw angular sum')
        A = raw_A / raw_sum  # Actual HarmonicGrid normalization, only at intake.
        grid = LockedGrid(node['mode_measure_m3'], node['momentum_scale'], angular['directions'], A,
                          tuple(node['state_labels'].tolist()), node['state_intervals'], identity)
        f = real(parent['occupation'], 'saved occupation').copy()
        diagnostics = dict(raw_angular_sum=raw_sum, raw_angular_normalization='A=raw/sum(raw)',
                           source_frame='hydrogen local tetrad', source_kind='scalar unpolarized isotropic bootstrap INITIAL-DATA',
                           source_model='Bianchi II source-derived bootstrap',
                           coupled_macro_endpoint=False, physical_energy_owner='c * saved network momentum_scale',
                           target_energy_J=parent['target_energies_eV_rescaled'].copy()*1.602176634e-19)
    occupation(grid, f)
    return grid, f, diagnostics


def occupation(grid, f):
    f = real(f, 'occupation')
    if f.shape != grid.shape or np.any(f < 0):
        raise ValueError('nonnegative occupation on original locked grid required')
    return f


def to_packets(grid, f, units):
    f = occupation(grid, f)
    n = multiply_positive(multiply_positive(grid.G[:, None], grid.A[None, :], 'G A'), f, 'cell number density')
    w = multiply_positive(units.weight_factor, n, 'packet weight').ravel()
    with np.errstate(over='ignore', under='ignore', invalid='ignore'):
        radial = grid.p / units.Pstar
    positive(radial, 'scaled momentum')
    k = (radial[:, None, None] * grid.directions[None, :, :]).reshape(-1, 3)
    state = PacketState(k, w, np.zeros(len(w)), units, grid.identity,
                        tuple(label for label in grid.cell_labels for _ in grid.A),
                        tuple(j for _ in grid.G for j in range(len(grid.A))))
    _validate_state(state)
    return state


def _validate_state(state):
    k, w, mass, e = kinetic.packet_arrays(state.k, state.w, state.mass)
    multiply_positive(w, e, 'packet energy contribution')
    # The unchanged vendor tensor uses w/e. Detect an erased or nonfinite
    # positive coefficient even when the algebraic product w*e would fit.
    with np.errstate(over='ignore', invalid='ignore', under='ignore'):
        coefficient = w / e
    if not np.all(np.isfinite(coefficient)) or np.any((w > 0) & (coefficient <= 0)):
        raise ValueError('vendor tensor coefficient nonfinite or positive underflow')
    if np.any(mass != 0) or len(state.cell_labels) != len(w) or len(state.angular_labels) != len(w):
        raise ValueError('labelled massless packets required')
    frame = real(state.frame, 'frame')
    if frame.shape != (4, 4):
        raise ValueError('4x4 frame required')
    return k, w, mass, e


def fixed_grid_inverse(state, grid):
    k, w, mass, e = _validate_state(state)
    expected_cells = tuple(label for label in grid.cell_labels for _ in grid.A)
    expected_angles = tuple(j for _ in grid.G for j in range(len(grid.A)))
    if state.grid_identity != grid.identity or state.cell_labels != expected_cells or state.angular_labels != expected_angles:
        raise ValueError('original input identity/grid/labels required')
    if np.max(np.abs(state.frame-np.eye(4))) > ROUNDTRIP_TOL:
        raise ValueError('original frame required; explicitly invert boost first')
    with np.errstate(over='ignore', under='ignore', invalid='ignore'):
        radial = grid.p / state.units.Pstar
    positive(radial, 'inverse scaled momentum')
    expected_k = (radial[:, None, None] * grid.directions[None, :, :]).reshape(-1, 3)
    scale = np.linalg.norm(expected_k, axis=1)
    if k.shape != expected_k.shape or np.any(np.max(np.abs(k-expected_k), axis=1) > ROUNDTRIP_TOL * scale):
        raise ValueError('packet momentum does not match original fixed grid')
    # Reverse the accepted forward arithmetic without constructing a fake
    # f=1 state or an unnecessarily large weight_factor*G*A denominator.
    denominator = multiply_positive(grid.G[:, None], grid.A[None, :], 'inverse G A')
    with np.errstate(over='ignore', invalid='ignore', under='ignore'):
        n = w.reshape(grid.shape) / state.units.weight_factor
        f = n / denominator
    if not np.all(np.isfinite(n)) or np.any((w.reshape(grid.shape) > 0) & (n <= 0)):
        raise ValueError('inverse number density nonfinite or positive underflow')
    if not np.all(np.isfinite(f)) or np.any((n > 0) & (f <= 0)):
        raise ValueError('inverse nonfinite arithmetic or positive underflow')
    return f


def state_boost(state, beta):
    _, w, _, e = _validate_state(state)
    B = kinetic.boost_matrix(beta)
    k_new, w_new = kinetic.boost(state.k, state.w, state.mass, beta)
    if not np.all(np.isfinite(w_new)) or np.any((w > 0) & (w_new <= 0)):
        raise ValueError('boost positive-weight underflow/nonfinite arithmetic')
    transformed = PacketState(k_new, w_new, state.mass.copy(), state.units, state.grid_identity,
                              state.cell_labels, state.angular_labels, B @ state.frame)
    _validate_state(transformed)
    return transformed


def physical_sums(grid, f):
    """Direct SI sums; no packet k,w,units or vendor formulas are used."""
    f = occupation(grid, f)
    N = np.zeros(4); T = np.zeros((4, 4)); Ns = np.zeros(4); Ts = np.zeros((4, 4))
    for i in range(len(grid.G)):
        for j in range(len(grid.A)):
            count = multiply_positive(multiply_positive(grid.G[i], grid.A[j], 'oracle G A'), f[i, j], 'oracle count')
            energy = multiply_positive(C, grid.p[i], 'oracle energy')
            ell = np.r_[1., grid.directions[j]]
            nc = multiply_positive(C, count, 'oracle current coefficient') * ell
            tc = multiply_positive(energy, count, 'oracle energy density') * np.outer(ell, ell)
            N += nc; T += tc; Ns += np.abs(nc); Ts += np.abs(tc)
    if not all(np.all(np.isfinite(x)) for x in (N,T,Ns,Ts)):
        raise ValueError('nonfinite physical sum')
    return N, T, Ns, Ts


def packet_observables(state):
    k, w, mass, e = _validate_state(state)
    ell = np.column_stack((np.ones(len(w)), k/e[:, None]))
    denominator = multiply_positive(state.units.alpha, state.units.Pstar, 'current recovery scale')
    with np.errstate(over='ignore', invalid='ignore', under='ignore'):
        coefficients = w / denominator
        N = np.einsum('q,qa->a', coefficients, ell)
        raw_tensor = kinetic.tensor(k, w, mass)
        T = raw_tensor / state.units.alpha
    if np.any((w > 0) & (coefficients <= 0)) or not np.all(np.isfinite(N)) or not np.all(np.isfinite(T)):
        raise ValueError('nonfinite recovery or positive underflow')
    if np.any((np.diag(raw_tensor) > 0) & (np.diag(T) <= 0)):
        raise ValueError('positive recovered stress-energy underflow')
    return N, T


def residual(actual, expected, absolute_contributions):
    """L∞ component error / global L1 absolute contribution scale.

    The global scale remains meaningful for symmetry-forced zero components.
    An all-zero oracle has residual zero iff actual is identically zero.
    """
    scale = float(np.sum(np.abs(absolute_contributions)))
    difference = float(np.max(np.abs(np.asarray(actual)-expected)))
    return difference/scale if scale else (0.0 if difference == 0 else float('inf'))
