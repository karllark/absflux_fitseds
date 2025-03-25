import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import astropy.units as u

from measure_extinction.stardata import StarData


def plot_set(
    ax,
    starnames,
    off_val=0.5,
    extra_off_val=0.0,
    norm_wave_range=[0.5, 0.8] * u.micron,
    col_vals=["b", "g", "r", "m", "c", "y"],
    ann_wave_range=[0.5, 0.8] * u.micron,
    ann_rot=25.0,
    ann_offset=0.2,
    ann_key="BAND",
    fontsize=12,
    path="data/faintwds/",
    subpath="",
):
    """
    Plot a set of spectra
    """
    # only_bands = ["J", "H", "K"]
    only_bands = None

    n_col = len(col_vals)
    for i in range(len(starnames)):
        stardata = StarData(subpath + starnames[i] + ".dat", path=path, only_bands=only_bands)

        stardata.plot(
            ax,
            norm_wave_range=norm_wave_range,
            yoffset=extra_off_val + off_val * i,
            yoffset_type="multiply",
            pcolor=col_vals[i % n_col],
            annotate_key=ann_key,
            annotate_wave_range=ann_wave_range,
            annotate_text=starnames[i] + " " + stardata.sptype,
            fontsize=fontsize*0.8,
            annotate_rotation=ann_rot,
            annotate_yoffset=ann_offset,
        )


if __name__ == "__main__":

    # commandline parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--uv", help="plot UV only", action="store_true")
    parser.add_argument("--png", help="save figure as a png file", action="store_true")
    parser.add_argument("--pdf", help="save figure as a pdf file", action="store_true")
    args = parser.parse_args()

    fontsize = 12

    font = {"size": fontsize}

    plt.rc("font", **font)

    plt.rc("lines", linewidth=1)
    plt.rc("axes", linewidth=2)
    plt.rc("xtick.major", width=2)
    plt.rc("xtick.minor", width=2)
    plt.rc("ytick.major", width=2)
    plt.rc("ytick.minor", width=2)

    # fig, ax = pyplot.subplots(nrows=1, ncols=1, figsize=(10, 13))
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))

    all = "wdfs0122_30 wdfs0248_33 wdfs0458_56 wdfs0639_57 wdfs0956_38 wdfs1055_36 wdfs1110_17 wdfs1206_27 wdfs1214_45 wdfs1302_10 wdfs1434_28 wdfs1514_00 wdfs1535_77 wdfs1557_55 wdfs1814_78 wdfs1837_70 wdfs1930_52 wdfs2317_29 wdfs2351_37"
 
    starnames = np.array(all.split())

    # avs = [4.76, 5.53, 4.49, 5.29, 4.99, 4.45, 5.50, 4.97, 6.24, 6.79, 6.18, 6.17]
    # sindxs = np.argsort(avs)
    # starnames = starnames[sindxs]

    # read in the data and determine the optical spectral slope
    # then sort by that
    path = "data/faintwds/"
    sslope = []
    for cstar in starnames:
        stardata = StarData(f"{cstar}.dat", path=path)
        gvals = (
            np.absolute(stardata.data["STIS"].waves - 0.15 * u.micron)
            < 0.01 * u.micron
        )
        bval = np.nanmedian(stardata.data["STIS"].fluxes[gvals])
        ctype = "STIS"
        gvals = (
            np.absolute(stardata.data[ctype].waves - 0.28 * u.micron)
            < 0.01 * u.micron
        )
        rval = np.nanmedian(stardata.data[ctype].fluxes[gvals])
        sslope.append(bval / rval)

    sindxs = np.argsort(sslope)
    starnames = starnames[sindxs]

    if args.uv:
        ann_key = "STIS"
        nrange = [0.25, 0.29] * u.micron
        arange = [0.13, 0.14] * u.micron
        normwave = "0.27"
        ann_offset = -0.07
        ann_rot = -16
        off_val = 0.2
        xticks = [0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.35]
        yrange = [1e-1, 1e5]
    else:
        ann_key = "BAND"
        nrange = [0.5, 0.8] * u.micron
        arange = [0.5, 0.8] * u.micron
        normwave = "0.65"
        ann_offset = -0.15
        ann_rot = -20.0
        off_val = 0.5
        xticks = [0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2]
        yrange = [1e-2, 1e12]

    col_vals = ["b", "g"]
    plot_set(
        ax,
        starnames,
        off_val=off_val,
        ann_key=ann_key,
        ann_rot=ann_rot,
        ann_offset=ann_offset,
        col_vals=col_vals,
        norm_wave_range=nrange,
        ann_wave_range=arange,
    )

    ax.set_yscale("log")
    ax.set_ylim(yrange)
    ax.set_xscale("log")
    # ax.set_xlim(kxrange)
    ax.set_xlabel(r"$\lambda$ [$\mu m$]", fontsize=1.3 * fontsize)
    ax.set_ylabel(rf"$F(\lambda)/F({normwave} \mu m)$ + offset", fontsize=1.3 * fontsize)

    ax.tick_params("both", length=10, width=2, which="major")
    ax.tick_params("both", length=5, width=1, which="minor")

    # ax.spines["right"].set_visible(False)
    # ax.spines["top"].set_visible(False)

    ax.xaxis.set_minor_formatter(ScalarFormatter())
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks(xticks, minor=True)

    if args.uv:
        ax.set_xlim(0.11, 0.35)

    fig.tight_layout()

    save_file = "figs/wd_spec"
    if args.uv:
        save_file = f"{save_file}_uv"
    if args.png:
        fig.savefig(save_file + ".png")
    elif args.pdf:
        fig.savefig(save_file + ".pdf")
    else:
        plt.show()
