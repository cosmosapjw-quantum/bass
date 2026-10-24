"""Source-bound scalar history and local finite Lyalpha boundary.

Scope/units/acceptance: ../FROZEN_CONTRACT.md and ../PREEXEC_ADDENDUM.md.
This is an isolated scientific adapter; production modules are unchanged.
Native source: rec_bianchi@a7c46fd, hydrogen.c 421ad4678a9a2f00...b2a051b.
"""
from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

import numpy as np

NVIRT, NSUBLYA, NSUBLYB = 311, 140, 271
E21, E31, E41 = 10.198714553953742, 12.087365397278509, 12.748393192442178
E32, E42 = 1.8886508433247664, 2.5496786384884356  # literal native differences
LYA_FACT = 4.662899067555897e15  # cm^-3: literal native convention
EV_J = 1.602176634e-19
G_NATIVE = 3.0e6 * LYA_FACT  # m^-3


def _finite(*values):
    if not all(math.isfinite(float(x)) for x in values):
        raise ValueError("NONFINITE_INPUT")


def _depth(tau, q=1.0):
    _finite(tau, q)
    if tau < 0 or q <= 0:
        raise ValueError("DEPTH_DOMAIN")
    u = tau / q
    if not math.isfinite(u):
        raise ValueError("TRANSFORMED_DEPTH_OVERFLOW")
    return u


def boundary(d_in, xr_p, x1s, tau, q=1.0, reference_occupation=0.0):
    """Native-Wien departures; signed values admitted by absolute occupations."""
    _finite(d_in, xr_p, x1s, reference_occupation)
    if x1s <= 0 or reference_occupation < 0:
        raise ValueError("BOUNDARY_DOMAIN")
    u = _depth(tau, q)
    source = xr_p / 3.0 / x1s
    _finite(source)
    if reference_occupation + d_in < 0 or reference_occupation + source < 0:
        raise ValueError("NEGATIVE_ABSOLUTE_OCCUPATION")
    transmitted = math.exp(-u)
    absorbed = -math.expm1(-u)
    delta = (source - d_in) * absorbed
    outgoing = d_in + delta
    _finite(delta, outgoing)
    return dict(outgoing=outgoing, delta=delta, transmission=transmitted,
                absorbed_fraction=absorbed, log_transmission=-u, source=source)


def boundary_jvp(d_in, xr_p, x1s, tau, q, dd_in, dxr_p, dx1s, dtau, dq,
                 reference_occupation=0.0):
    """Derivative at an admitted state; thermodynamic reference is held fixed."""
    b = boundary(d_in, xr_p, x1s, tau, q, reference_occupation)
    _finite(dd_in, dxr_p, dx1s, dtau, dq)
    ds = dxr_p / 3.0 / x1s - b["source"] * (dx1s/x1s)
    du = dtau/q - (tau/q)*(dq/q)
    _finite(ds, du)
    answer = (b["transmission"]*dd_in + b["absorbed_fraction"]*ds
              + (b["source"]-d_in)*b["transmission"]*du)
    _finite(answer)
    return answer


def interpolation(eta0, h, values, iz, eta):
    """Native strict-past interpolation, with an explicit fixed-cell witness."""
    _finite(eta0, h, eta)
    if h <= 0 or isinstance(iz, (bool, np.bool_)) or not isinstance(iz, (int, np.integer)) or iz < 0:
        raise ValueError("HISTORY_CLOCK_OR_INDEX")
    y = np.asarray(values)
    if y.ndim != 1 or len(y) < iz:
        raise ValueError("HISTORY_PREFIX_SHAPE")
    if iz < 2 or eta < eta0:
        return dict(value=0.0, k=None, alpha=0.0, thermal=True, query_slope=0.0,
                    at_knot=False, query=float(eta), prefix=int(iz))
    endpoint = eta0 + h*(iz-1)
    _finite(endpoint)
    if eta >= endpoint:
        raise ValueError("HISTORY_FUTURE_READ")
    position = (eta-eta0)/h
    _finite(position)
    k = math.floor(position)
    alpha = position-k
    if k < 0 or k+1 >= iz:
        raise ValueError("HISTORY_INDEX_ROUNDOFF")
    y0, y1 = y[k], y[k+1]
    if not (np.isfinite(y0) and np.isfinite(y1)):
        raise ValueError("HISTORY_SAMPLE_NONFINITE")
    value = (1.0-alpha)*y0 + alpha*y1
    slope = (y1-y0)/h
    if not (np.isfinite(value) and np.isfinite(slope)):
        raise ValueError("HISTORY_RESULT_NONFINITE")
    # Exact representable knot, or native subtraction resolving alpha==0.
    knot = alpha == 0.0 or eta == eta0+h*k
    return dict(value=value, k=k, alpha=alpha, thermal=False, query_slope=slope,
                at_knot=bool(knot), query=float(eta), prefix=int(iz))


def interpolation_jvp(result, dvalues, deta=0.0):
    _finite(deta)
    if result["thermal"]:
        return 0.0
    if result["at_knot"] and deta != 0.0:
        raise ValueError("NONSMOOTH_QUERY")
    dy = np.asarray(dvalues)
    k, a = result["k"], result["alpha"]
    if dy.ndim != 1 or len(dy) <= k+1 or not np.all(np.isfinite(dy[k:k+2])):
        raise ValueError("HISTORY_TANGENT_SHAPE_OR_NONFINITE")
    answer = (1.0-a)*dy[k]+a*dy[k+1]+result["query_slope"]*deta
    if not np.isfinite(answer):
        raise ValueError("HISTORY_TANGENT_NONFINITE")
    return answer


def interpolation_envelope(h, alpha, curvature_bound, left_error=0.0, right_error=0.0):
    _finite(h, alpha, curvature_bound, left_error, right_error)
    if h <= 0 or not 0 <= alpha <= 1 or min(curvature_bound,left_error,right_error) < 0:
        raise ValueError("INTERPOLATION_ERROR_DOMAIN")
    answer = 0.5*curvature_bound*h*h*alpha*(1-alpha)+(1-alpha)*left_error+alpha*right_error
    _finite(answer)
    return answer


def native_links(energies_eV):
    """Exact routing in hydrogen.c:fplus_from_fminus; each target has one owner."""
    e = np.asarray(energies_eV,dtype=float)
    if e.shape != (NVIRT,) or not np.all(np.isfinite(e)) or np.any(e <= 0) or np.any(np.diff(e) <= 0):
        raise ValueError("NATIVE_ENERGY_GRID")
    if not (e[NSUBLYA-1] < E21 < e[NSUBLYA] and e[NSUBLYB-1] < E31 < e[NSUBLYB] and e[-1] < E41):
        raise ValueError("NATIVE_LINE_GRID")
    source = np.arange(1,NVIRT+3,dtype=int)
    source[NSUBLYA-1],source[NSUBLYB-1],source[NVIRT-1] = NVIRT,NVIRT+1,NVIRT+2
    source[NVIRT],source[NVIRT+1] = NSUBLYA,NSUBLYB
    targets = np.r_[e,E21,E31]
    all_outgoing_energies = np.r_[e,E21,E31,E41]
    sources = all_outgoing_energies[source]
    if np.any(sources <= targets):
        raise ValueError("NATIVE_REDSHIFT_ORIENTATION")
    return source,targets,sources


def incoming_history(eta0,h,outgoing_history,iz,eta_face,energies_eV,*,z_face=None):
    """Scalar FLRW history; optional z_face preserves native floating arithmetic."""
    _finite(eta_face)
    history = np.asarray(outgoing_history)
    if history.ndim != 2 or history.shape[0] != NVIRT+3:
        raise ValueError("OUTGOING_HISTORY_SHAPE")
    source,targets,sources = native_links(energies_eV)
    if z_face is None:
        try:
            zp1 = math.exp(-eta_face)
        except OverflowError as exc:
            raise ValueError("HISTORY_CLOCK_OVERFLOW") from exc
    else:
        _finite(z_face)
        if z_face <= -1:
            raise ValueError("FACE_REDSHIFT_DOMAIN")
        zp1 = 1.0+z_face
        exact_eta = -math.log(zp1)
        if abs(exact_eta-eta_face) > 16*np.finfo(float).eps*max(1.0,abs(eta_face)):
            raise ValueError("FACE_CLOCK_MISMATCH")
    if not math.isfinite(zp1) or zp1 <= 0:
        raise ValueError("HISTORY_CLOCK_DOMAIN")
    result=[]
    for row,et,es in zip(source,targets,sources):
        ainv = zp1*float(es)/float(et)
        if not math.isfinite(ainv) or ainv <= 0:
            raise ValueError("HISTORY_QUERY_DOMAIN")
        stencil=interpolation(eta0,h,history[row],iz,-math.log(ainv))
        stencil["source_index"]=int(row)
        result.append(stencil)
    return dict(incoming=np.array([r["value"] for r in result]),stencils=result,
                representation="native_scalar_FLRW",zp1=zp1)


def incoming_history_jvp(result,history_tangent,query_tangent=0.0):
    dy=np.asarray(history_tangent)
    if dy.ndim != 2 or dy.shape[0] != NVIRT+3:
        raise ValueError("HISTORY_TANGENT_SHAPE")
    dq=np.asarray(query_tangent)
    if dq.ndim==0:
        dq=np.full(NVIRT+2,float(dq))
    if dq.shape!=(NVIRT+2,) or not np.all(np.isfinite(dq)):
        raise ValueError("QUERY_TANGENT_SHAPE")
    return np.array([interpolation_jvp(r,dy[r["source_index"]],dq[i])
                     for i,r in enumerate(result["stencils"])])


def line_ledger(d_in,xr_p,x1s,tau,nH_cm3,H,q=1.0,owner="boundary",reference_occupation=0.0):
    if not isinstance(owner,str) or owner not in ("boundary","event"):
        raise ValueError("EXCLUSIVE_RADIATION_OWNER_REQUIRED")
    _finite(nH_cm3,H)
    if nH_cm3<=0 or H<=0:
        raise ValueError("EXPANDING_NATIVE_LEDGER_DOMAIN")
    b=boundary(d_in,xr_p,x1s,tau,q,reference_occupation)
    rate=G_NATIVE*H*q*b["delta"]
    energy=E21*EV_J*rate
    _finite(rate,energy)
    return dict(R=rate,atomic_internal_J_m3_s=-energy,radiation_J_m3_s=energy,
                stable_jump=b["delta"],normalization=G_NATIVE,owner=owner,
                occupation_is_boundary_encoding=True,extra_radiation_source=0.0)


def _blob(path,expected):
    content=Path(path).read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
    if sha!=expected:
        raise ValueError("FROZEN_INPUT_IDENTITY:"+str(path))


class FrozenHistoryMap:
    """Finite algebraic map at one frozen state; accepts complex tangent oracles."""
    def __init__(self,meta,virtual,tvr,tvv,prepared):
        self.x1s=meta["x1s"]
        self.TR=meta["TR_eV_rescaled"]
        self.nH=meta["nH_cm3"]
        self.H=meta["H_sInv"]
        self.r0=LYA_FACT*self.H/(self.nH*self.x1s)
        self.energies=virtual[:,0].copy()
        self.u0=np.r_[virtual[:,1],meta["Dfplus_Lya"],meta["Dfplus_Lyb"]]
        self.X0=prepared["X0"].copy()
        self._M=prepared["M"].copy()
        self.source=prepared["source"].copy()
        self._tvr=tvr.copy()
        self._tvv=tvv.copy()
        self._tau=virtual[:,5].copy()
        self._one_minus_P=virtual[:,12].copy()  # literal native result retained in CSV
        self._A=np.array([1-math.exp(-t) if t>1e-6 else t-t*t/2 for t in self._tau])
        for v in vars(self).values():
            if isinstance(v,np.ndarray):
                if not np.all(np.isfinite(v)):
                    raise ValueError("FROZEN_DATA_NONFINITE")
                v.setflags(write=False)
        if self._M.shape!=(313,313) or self.X0.shape!=(313,) or self.x1s<=0:
            raise ValueError("FROZEN_DATA_SHAPE_OR_DOMAIN")

    @staticmethod
    def _a(tau):
        return 1.0 if tau is None else -math.expm1(-_depth(tau))

    def Mstar(self,tau=None):
        M=self._M.copy()
        M[1,1]+=self.r0*(self._a(tau)-1.0)
        return M

    def source_increment(self,du,tau=None):
        u=np.asarray(du)
        if u.shape!=(313,) or not np.all(np.isfinite(u)):
            raise ValueError("INCOMING_VECTOR_SHAPE_OR_NONFINITE")
        b=np.empty(313,dtype=np.result_type(u.dtype,float))
        b[0]=3*self.r0*self.x1s*1.664786871919931*u[312]
        b[1]=3*self.r0*self._a(tau)*self.x1s*u[311]
        b[2:]=self._tvv[0]*self.x1s*(1-self._one_minus_P)*u[:311]
        if not np.all(np.isfinite(b)):
            raise ValueError("SOURCE_INCREMENT_NONFINITE")
        return b

    def source_at(self,incoming,tau=None):
        """Absolute RHS under exclusive original Lyalpha-pair replacement."""
        result=self.source+self.source_increment(np.asarray(incoming)-self.u0,tau)
        result[1]+=3*self.r0*(self._a(tau)-1.0)*self.x1s*self.u0[311]
        return result

    def outgoing(self,X,incoming,tau=None):
        x,u=np.asarray(X),np.asarray(incoming)
        if x.shape!=(313,) or u.shape!=(313,) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(u)):
            raise ValueError("FROZEN_OUTGOING_SHAPE_OR_NONFINITE")
        out=np.empty(314,dtype=np.result_type(x.dtype,u.dtype,float))
        xr,xv=x[:2],x[2:]
        for b in range(NVIRT):
            if self._tau[b]<=1e-30:
                out[b]=u[b]
                continue
            eq=-xr[0]*self._tvr[0,b]-xr[1]*self._tvr[1,b]
            if b==0:
                eq-=xv[1]*self._tvv[2,0]
            elif b==NVIRT-1:
                eq-=xv[NVIRT-2]*self._tvv[1,NVIRT-1]
            else:
                eq-=xv[b+1]*self._tvv[2,b]+xv[b-1]*self._tvv[1,b]
            eq/=self.x1s*self._one_minus_P[b]*self._tvv[0,b]
            out[b]=u[b]+(eq-u[b])*self._A[b]
        a=self._a(tau)
        out[311]=xr[1]/3.0/self.x1s if tau is None else u[311]+(xr[1]/(3*self.x1s)-u[311])*a
        out[312]=xr[0]/self.x1s*math.exp(-E32/self.TR)
        out[313]=xr[0]/self.x1s*math.exp(-E42/self.TR)
        if not np.all(np.isfinite(out)):
            raise ValueError("FROZEN_OUTGOING_NONFINITE")
        return out

    def outgoing_jvp(self,dX,du,tau=None):
        # Exactly linear in X and u at fixed tau and thermodynamic coefficients.
        return self.outgoing(dX,du,tau)


def load_frozen(csv_path,prepared_npz):
    _blob(csv_path,"6399b59ca3c97d6c5b1162f83f50a6677fad06ff")
    _blob(prepared_npz,"e96d15dfc0432429f2fcb680159f4820c02ce591")
    meta={}
    virtual=np.full((311,13),np.nan)
    tvr=np.zeros((2,311));tvv=np.zeros((3,311))
    seen=set()
    with Path(csv_path).open(newline="") as handle:
        for row in csv.reader(handle):
            if row[0]=="META":
                meta[row[1]]=float(row[2])
            elif row[0]=="VIRTUAL":
                i=int(row[1])
                if i in seen or len(row)!=15 or not 0<=i<311:
                    raise ValueError("FROZEN_VIRTUAL_ROWS")
                seen.add(i);virtual[i]=list(map(float,row[2:]))
            elif row[0]=="TVR":
                tvr[int(row[1]),int(row[2])]=float(row[3])
            elif row[0]=="TVV":
                tvv[int(row[1]),int(row[2])]=float(row[3])
    if len(seen)!=311:
        raise ValueError("FROZEN_VIRTUAL_ROWS")
    with np.load(prepared_npz,allow_pickle=False) as prepared:
        return FrozenHistoryMap(meta,virtual,tvr,tvv,prepared)
