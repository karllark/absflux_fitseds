import argparse
import datetime
import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.io import fits
from astropy.table import QTable

from measure_extinction.stardata import StarData
from measure_extinction.merge_obsspec import merge_gen_obsspec

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("starname", help="Name of star")
    parser.add_argument("--png", help="save figure as a png file", action="store_true")
    args = parser.parse_args()

    sname = args.starname
    path = "data/whitedwarfs/"
    fname = f"{sname}.dat"

    obs = StarData(fname, path=path)

    # plotting setup for easier to read plots
    fontsize = 16
    font = {"size": fontsize}
    plt.rc("font", **font)
    plt.rc("lines", linewidth=1)
    plt.rc("axes", linewidth=2)
    plt.rc("xtick.major", width=2)
    plt.rc("xtick.minor", width=2)
    plt.rc("ytick.major", width=2)
    plt.rc("ytick.minor", width=2)

    fig, ax = plt.subplots(figsize=(12, 8), layout="constrained")

    allspec = []
    alltab = []
    waverange = []
    for cspec in obs.data.keys():
        if "WFC3" not in cspec:
            tab = QTable()
            tab["WAVELENGTH"] = obs.data[cspec].waves
            tab["FLUX"] = obs.data[cspec].fluxes
            tab["ERROR"] = obs.data[cspec].uncs
            tab["NPTS"] = obs.data[cspec].npts
            alltab.append(tab)
            allspec.append(cspec)

            # plot the individual grating spectra
            lam4 = (tab["WAVELENGTH"] ** 4).to(u.micron**4)
            gvals = obs.data[cspec].npts > 0
            ax.plot(
                obs.data[cspec].waves[gvals],
                lam4[gvals] * obs.data[cspec].fluxes[gvals],
                label=cspec,
            )
            waverange.append([np.min(obs.data[cspec].waves[gvals]),
                              np.max(obs.data[cspec].waves[gvals])])

    mspec = merge_gen_obsspec(alltab, [0.1150, 3.1] * u.micron, output_resolution=1000)
    mspec["FLUX"][mspec["NPTS"] == 0] = np.nan
    mspec["WAVELENGTH"] = mspec["WAVELENGTH"].to(u.micron)

    # save the merged spectrum to a file
    #   include the individual grating spectra in FITS extensions
    ofile = f"calspec_products/{sname}_2026_10_ucA_obs.fits"
    phdu = fits.PrimaryHDU()
    current_time = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    phdu.header["CDATE"] = (current_time, "Creation date and time in UTC")
    phdu.header["USECASE"] = ("A", "Use case for CALSPEC product")
    phdu.header["USETYPE"] = ("OBS", "Type of CALSPEC product")
    phdu.header["STAR"] = (sname, "Name of the star")
    phdu.header["NGRAT"] = (len(allspec), "Number of individual grating spectra")
    phdu.header["RES"] = (1000, "Output resolution of merged spectrum")
    phdu.header["WAVEMIN"] = (
        mspec["WAVELENGTH"][0],
        "Minimum wavelength of merged spectrum in microns",
    )
    phdu.header["WAVEMAX"] = (
        mspec["WAVELENGTH"][-1],
        "Maximum wavelength of merged spectrum in microns",
    )
    phdu.header["COMMENT"] = "Spectra included with wavelength ranges"
    for cspec, crange in zip(allspec, waverange):
        phdu.header["COMMENT"] = f"{cspec}: {crange[0]:.4f} - {crange[1]:.4f}"

    phdu.header["COMMENT"] = (
        "Individual spectra are included in FITS extensions for reference"
    )
    mhdu = fits.BinTableHDU(mspec, name="OBS")
    hdulist = [phdu, mhdu]
    for ctab, cspec in zip(alltab, allspec):
        hdulist.append(fits.BinTableHDU(ctab, name=cspec))
    hduout = fits.HDUList(hdulist)
    hduout.writeto(ofile, overwrite=True)

    # plot the merge spectrum
    ax.plot(
        mspec["WAVELENGTH"],
        (mspec["WAVELENGTH"] ** 4) * mspec["FLUX"],
        label="merged",
        color="black",
        alpha=0.5,
    )
    ax.plot(
        mspec["WAVELENGTH"],
        (mspec["WAVELENGTH"] ** 4) * mspec["FLUX"] * 1.2,
        color="black",
    )

    ax.set_xlabel(r"$\lambda$ [$\mu$m]")
    ax.set_ylabel(r"$\lambda^4 F(\lambda)$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(sname)
    ax.legend()

    # plot or save to a file
    if args.png:
        fig.savefig(f"{args.starname}_merge.png")
    else:
        plt.show()
