import argparse
import pickle
import emcee
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np

from measure_extinction.model import MEModel
from measure_extinction.stardata import StarData
from measure_extinction.extdata import ExtData


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("starname", help="Name of star")
    parser.add_argument("--burnfrac", help="burn fraction", default=0.5, type=float)
    parser.add_argument(
        "--obspath",
        help="path to observed data",
        default="/home/kgordon/Python/extstar_data/MW/",
    )
    parser.add_argument(
        "--picmodname", help="name of pickled model", default="tlusty_z100_modinfo.p"
    )
    parser.add_argument(
        "--bands", help="only use these observed bands", nargs="+", default=None
    )
    parser.add_argument("--png", help="save figure as a png file", action="store_true")
    parser.add_argument("--pdf", help="save figure as a pdf file", action="store_true")
    args = parser.parse_args()

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

    # base filename
    outname = f"figs/{args.starname}_mefit"

    # get the observed data
    fstarname = f"{args.starname}.dat"
    reddened_star = StarData(fstarname, path=f"{args.obspath}", only_bands=args.bands)

    # get the modeling info
    modinfo = pickle.load(open(args.picmodname, "rb"))
    modinfo_cont = pickle.load(
        open(args.picmodname.replace("modinfo", "cont_modinfo"), "rb")
    )

    # setup the ME model
    memod = MEModel(obsdata=reddened_star, modinfo=modinfo)
    memod_cont = MEModel(obsdata=reddened_star, modinfo=modinfo_cont)

    # get the extinction curve
    tstr = outname.replace("figs", "exts")
    extfile = f"{tstr}_ext.fits"
    ext = ExtData(filename=extfile)
    ptab = ext.fit_params["MCMC"]
    for k, cname in enumerate(ptab["name"]):
        param = getattr(memod, cname)
        param.value = ptab["value"][k]
        if ptab["fixed"][k] > 0.1:
            param.fixed = True
        else:
            param.fixed = False
        if ptab["prior"][k] > 0.1:
            param.prior = (ptab["prior_val"][k], ptab["prior_unc"][k])
        else:
            param.prior = None

    # weights
    memod.fit_weights(reddened_star)
    memod_cont.fit_weights(reddened_star)

    # get the MCMC chains
    sampfile = f"{tstr}_.h5"
    reader = emcee.backends.HDFBackend(sampfile)
    samples = reader.get_chain()
    nsteps = samples.shape[0]

    # analyze chains for convergence
    tau = reader.get_autocorr_time(quiet=True)
    print("taus = ", tau)
    # burnin = int(2 * np.max(tau))
    # thin = int(0.5 * np.min(tau))
    # samples = reader.get_chain(discard=burnin, flat=True, thin=thin)
    # log_prob_samples = reader.get_log_prob(discard=burnin, flat=True, thin=thin)
    # log_prior_samples = reader.get_blobs(discard=burnin, flat=True, thin=thin)

    # print("burn-in: {0}".format(burnin))
    # print("thin: {0}".format(thin))
    # print("flat chain shape: {0}".format(samples.shape))
    # print("flat log prob shape: {0}".format(log_prob_samples.shape))
    # print("flat log prior shape: {0}".format(log_prior_samples.shape))

    flat_samples = reader.get_chain(discard=int(args.burnfrac * nsteps), flat=True)

    # get the 50 percentile and +/- uncertainties
    params_per = map(
        lambda v: (v[1], v[2] - v[1], v[1] - v[0]),
        zip(*np.percentile(flat_samples, [16, 50, 84], axis=0)),
    )

    # now package the fit parameters into two vectors, averaging the +/- uncs
    n_params = samples.shape[2]
    params_p50 = np.zeros(n_params)
    params_unc = np.zeros(n_params)
    for k, val in enumerate(params_per):
        params_p50[k] = val[0]
        params_unc[k] = 0.5 * (val[1] + val[2])

    # set the best fit parameters in the output model
    memod.fit_to_parameters(params_p50, uncs=params_unc)
    memod_cont.fit_to_parameters(params_p50, uncs=params_unc)
    print(f"p50 parameters, burnfrac={args.burnfrac}")
    memod.pprint_parameters()

    # plot
    fig, axes = plt.subplots(
        nrows=3, figsize=(8, 8), gridspec_kw={"height_ratios": [2, 2, 1]}
    )

    # normalized the data by the continuum model
    modsed = memod.stellar_sed(modinfo)
    ext_modsed = memod.dust_extinguished_sed(modinfo, modsed)
    hi_ext_modsed = memod.hi_abs_sed(modinfo, ext_modsed)

    modsed_cont = memod_cont.stellar_sed(modinfo_cont)
    ext_modsed_cont = memod_cont.dust_extinguished_sed(modinfo_cont, modsed_cont)
    hi_ext_modsed_cont = memod_cont.hi_abs_sed(modinfo_cont, ext_modsed_cont)

    for cspec in list(reddened_star.data.keys()) + ["MODEL_FULL_LOWRES"]:

        if cspec == "BAND":
            cwaves = reddened_star.data[cspec].waves
            ptype = "o"
            rcolor = "g"
            calpha = 0.75
            linewidth = 10.0
            fcolor = "none"
            markersize = 10.0
        else:
            cwaves = modinfo.waves[cspec]
            ptype = "-"
            rcolor = "k"
            calpha = 0.5
            linewidth = 2.0
            fcolor = None
            markersize = None

        nvals = np.full(len(cwaves), 1.0)
        # plot the residuals
        if cspec != "MODEL_FULL_LOWRES":
            mcolor = "r"
            gvals = hi_ext_modsed[cspec] > 0.0
            modspec = hi_ext_modsed[cspec][gvals] * memod.norm.value
            diff = (
                100.0
                * (reddened_star.data[cspec].fluxes.value[gvals] - modspec)
                / modspec
            )
            if cspec != "BAND":
                uncs = None
            else:
                uncs = 100.0 * reddened_star.data[cspec].uncs.value[gvals] / modspec

            nvals = np.full(len(diff), 1.0)
            nvals[(memod.weights[cspec])[gvals] == 0.0] = np.nan

            axes[2].errorbar(
                cwaves[gvals],
                diff,
                yerr=uncs,
                fmt=rcolor + ptype,
                alpha=0.2,
                markersize=markersize,
                mfc=fcolor,
            )
            axes[2].errorbar(
                cwaves[gvals] * nvals,
                diff * nvals,
                yerr=uncs,
                fmt=rcolor + ptype,
                alpha=calpha,
                markersize=markersize,
                mfc=fcolor,
            )

            # compute the ratio to the extinguished model continuum
            reddened_star.data[cspec].fluxes /= (
                memod_cont.norm.value * hi_ext_modsed_cont[cspec]
            )
            reddened_star.data[cspec].uncs /= (
                memod_cont.norm.value * hi_ext_modsed_cont[cspec]
            )

            gvals = reddened_star.data[cspec].fluxes > 0.0
            # nan models where no data or excluded
            nvals = np.full(len(cwaves), 1.0)
            nvals[memod_cont.weights[cspec] == 0.0] = np.nan
        else:
            mcolor = "c"

        hi_ext_modsed[cspec] /= hi_ext_modsed_cont[cspec]

        for cax in axes[0:2]:
            cax.plot(
                cwaves,
                hi_ext_modsed[cspec] * nvals,
                mcolor + ptype,
                linewidth=linewidth,
                markersize=markersize,
                mfc=fcolor,
                label=f"Model: {cspec}",
            )
            cax.plot(
                cwaves,
                hi_ext_modsed[cspec],
                mcolor + ptype,
                alpha=0.2,
                linewidth=linewidth,
                markersize=markersize,
                mfc=fcolor,
            )

            # data
            if cspec != "MODEL_FULL_LOWRES":
                cax.errorbar(
                    reddened_star.data[cspec].waves[gvals],
                    reddened_star.data[cspec].fluxes[gvals],
                    #yerr=reddened_star.data[cspec].uncs[gvals],
                    fmt=rcolor + ptype,
                    alpha=calpha,
                    mfc=fcolor,
                    markersize=markersize,
                    label=f"Data: {cspec}"
                )

    axes[0].set_xlim(0.11, 0.38)
    axes[1].set_xlim(0.35, 2.0)
    axes[1].set_xscale("log")
    axes[2].set_xlim(0.11, 2.0)
    axes[2].set_xscale("log")

    for cax in axes[0:2]:
        cax.axhline(1.0, ls="--", color="k", alpha=0.5)
        cax.set_ylabel(r"$F/F_{\mathrm{modcont}}$")
        cax.set_ylim(0.5, 1.2)

    axes[2].set_ylim(-10.0, 10.0)
    axes[2].axhline(0.0, ls="--", color="k", alpha=0.5)
    axes[2].set_ylabel("residuals [%]")

    axes[2].set_xlabel(r"$\lambda$ [$\mu$m]")

    for cax in axes[1:3]:
        cax.xaxis.set_major_formatter(ScalarFormatter())
        cax.xaxis.set_minor_formatter(ScalarFormatter())
        cax.tick_params(axis="x", which="minor", labelsize=fontsize)
        cax.tick_params(axis="x", which="minor", labelsize=fontsize)
    axes[1].set_xticks([0.4, 0.6, 0.8, 1.0, 2.0], minor=True)
    axes[2].set_xticks([0.11, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 2.0], minor=True)

    axes[0].set_title((reddened_star.file).replace(".dat", ""), fontsize=fontsize)

    axes[1].legend(fontsize=0.7*fontsize, ncol=2)

    save_str = "_mefit_mcmc_norm"

    fig.tight_layout()

    # plot or save to a file
    if args.png:
        fig.savefig(f"{args.starname}{save_str}.png")
    elif args.pdf:
        fig.savefig(f"{args.starname}{save_str}.pdf")
    else:
        plt.show()


if __name__ == "__main__":
    main()
