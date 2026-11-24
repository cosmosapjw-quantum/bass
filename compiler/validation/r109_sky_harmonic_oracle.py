"""Regenerate the finite HEALPix-pixel quadrature reference for the Rust spin transform."""
from pathlib import Path

import healpy as hp
import numpy as np


def main():
    nside, lmax = 2, 4
    ell, m = hp.Alm.getlm(lmax)
    alm = np.empty((3, len(ell)), dtype=complex)
    for field in range(3):
        phase = (ell+1)*(m+2)*(field+1)
        alm[field] = (np.sin(phase) + 1j*np.cos(phase)*(m > 0))/(ell+1)
    alm[1:, ell < 2] = 0
    sky = hp.alm2map(alm, nside, lmax=lmax)
    # iter=0 computes the actual uniform-pixel weighted inner products.
    # The low-resolution pixel window and quadrature residual are common to both sides.
    recovered = hp.map2alm(sky, lmax=lmax, iter=0, pol=True, use_weights=False)
    modes = np.sort(np.unique(ell))
    pixels = np.arange(hp.nside2npix(nside))
    directions = np.array(hp.pix2vec(nside, pixels))
    rows = [f"# HEALPix/healpy {hp.__version__} NSIDE={nside} lmax={lmax} COSMO",
            "# p x y z dOmega T Q U | a ell m ReT ImT ReE ImE ReB ImB"]
    values = np.vstack((directions, np.full(len(pixels),4*np.pi/len(pixels)),sky)).T
    for row in values:
        rows.append("p " + " ".join(f"{x:.17g}" for x in row))
    for l in modes:
        for order in range(int(l)+1):
            coeff = recovered[:, hp.Alm.getidx(lmax,l,order)]
            vals = np.stack((coeff.real, coeff.imag), axis=1).ravel()
            rows.append(f"a {l} {order} " + " ".join(f"{x:.17g}" for x in vals))
    path = Path(__file__).resolve().parents[2]/"_rustcore/tests/fixtures/r109_healpix_sky.txt"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("\n".join(rows)+"\n")


if __name__ == "__main__":
    main()
