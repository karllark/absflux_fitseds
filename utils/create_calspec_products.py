import argparse
import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
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
    fontsize = 12
    font = {"size": fontsize}
    plt.rc("font", **font)
    plt.rc("lines", linewidth=1)
    plt.rc("axes", linewidth=2)
    plt.rc("xtick.major", width=2)
    plt.rc("xtick.minor", width=2)
    plt.rc("ytick.major", width=2)
    plt.rc("ytick.minor", width=2)

    fig, ax = plt.subplots(figsize=(12, 8))

    alltab = []
    for cspec in obs.data.keys():
        print(cspec)
        if "WFC3" not in cspec:
            tab = QTable()
            tab["WAVELENGTH"] = obs.data[cspec].waves
            tab["FLUX"] = obs.data[cspec].fluxes
            tab["ERROR"] = obs.data[cspec].uncs
            tab["NPTS"] = obs.data[cspec].npts
            alltab.append(tab)

            lam4 = (tab["WAVELENGTH"] ** 4).to(u.micron ** 4)
            gvals = obs.data[cspec].npts > 0
            ax.plot(obs.data[cspec].waves[gvals], lam4[gvals] * obs.data[cspec].fluxes[gvals], label=cspec)

    mspec = merge_gen_obsspec(alltab, [0.1150, 3.1] * u.micron, output_resolution=1000)
    mspec["FLUX"][mspec["NPTS"] == 0] = np.nan
    mspec["WAVELENGTH"] = mspec["WAVELENGTH"].to(u.micron)
    ax.plot(mspec["WAVELENGTH"], (mspec["WAVELENGTH"] ** 4) * mspec["FLUX"], label="merged", color="black", alpha=0.5)
    ax.plot(mspec["WAVELENGTH"], (mspec["WAVELENGTH"] ** 4) * mspec["FLUX"] * 1.2, color="black")

    ax.set_xlabel("Wavelength")
    ax.set_ylabel("Flux")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(sname)
    ax.legend()

    # plot or save to a file
    if args.png:
        fig.savefig(f"{args.starname}_merge.png")
    else:
        plt.show()