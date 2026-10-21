#!/usr/bin/env python3
"""SOURCE07 C11 source-locked, strict-domain Grackle Case-A rate adapter.

The underlying cgs coefficients are emitted directly from the unchanged
rei_microphysics::igm_rates::igm_rates Rust implementation. Only a smooth
10,000--24,000 Kelvin segment is admitted to prevent crossing either the
5500 K Grackle branch or 0.8*11605 K dielectronic switch.
No clamping, unconditional Case-B substitution, or arbitrary gas extrapolation.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

HERE=Path(__file__).resolve().parent
TABLE=HERE/"owner_grackle_rates_129.csv"
COLUMNS=("rr_HII_cm3_s","rr_HeII_cm3_s","rr_HeIII_cm3_s",
         "dr_HeII_cm3_s","rr_cool_HII_erg_cm3_s",
         "rr_cool_HeII_erg_cm3_s","rr_cool_HeIII_erg_cm3_s",
         "dr_cool_HeII_erg_cm3_s")
EV_ERG=1.602176634e-12


class RateDomainError(ValueError):
    pass


class CaseARates:
    def __init__(self,table:Path=TABLE):
        self.path=Path(table)
        data=np.genfromtxt(self.path,delimiter=",",names=True)
        if tuple(data.dtype.names)!=("T_K",)+COLUMNS:
            raise ValueError("wrong rate-table header or science owner")
        self.temperatures=np.array(data["T_K"],dtype=float)
        self.values=np.column_stack([data[k] for k in COLUMNS])
        if not np.all(np.isfinite(self.values)) or np.any(self.values<=0):
            raise ValueError("nonpositive Grackle rate table")
        if not np.all(np.diff(self.temperatures)>0):
            raise ValueError("nonmonotone Grackle table")
        if not (self.temperatures[0]<=10000.001 and
                self.temperatures[-1]>=23999.999):
            raise ValueError("incomplete Grackle rate domain")
        self.minT=float(self.temperatures[0])
        self.maxT=float(self.temperatures[-1])
        self.interp=PchipInterpolator(np.log(self.temperatures),
                                     np.log(self.values),axis=0,extrapolate=False)
        self.sha256=hashlib.sha256(self.path.read_bytes()).hexdigest()

    def __call__(self,temperature:float)->np.ndarray:
        t=float(temperature)
        if not np.isfinite(t) or not (self.minT<=t<=self.maxT):
            raise RateDomainError(f"GRACKLE_C11_T_OUTSIDE_10000_24000:{t}")
        vals=np.exp(self.interp(np.log(t)))
        if vals.shape!=(8,) or not np.isfinite(vals).all() or np.any(vals<0):
            raise RateDomainError("BAD_GRACKLE_COEFFICIENT")
        return vals

    def exact_grid_parity(self)->float:
        rel=0.
        for T,row in zip(self.temperatures,self.values):
            approx=self(float(T))
            rel=max(rel,float(np.max(np.abs(approx-row)/row)))
        return rel


class ConstantRates:
    """Manufactured testing provider; never relabel as physical Grackle."""
    def __init__(self,rr=(0.,0.,0.),dr=0.,cooling=(0.,0.,0.),dr_cool=0.):
        self.v=np.array([*rr,dr,*cooling,dr_cool],dtype=float)
        if not np.isfinite(self.v).all() or np.any(self.v<0):
            raise ValueError("invalid manufactured rates")
        self.minT=1.
        self.maxT=1e6
        self.sha256="MANUFACTURED_NOT_A_GRACKLE_COEFFICIENT"
    def __call__(self,temperature):
        if not (np.isfinite(temperature) and self.minT<=temperature<=self.maxT):
            raise RateDomainError("MANUFACTURED_T_OUTSIDE_DOMAIN")
        return self.v.copy()
