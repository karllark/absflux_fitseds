import numpy as np
import matplotlib.pyplot as plt


def get_fit_params(params):
    """
    Removes the parameters that are fixed so the fitter does not fit them
    """
    fit_params = np.zeros(len(params) - 2)
    fit_params[0:2] = params[0:2]
    fit_params[2:] = params[3:-1]

    return fit_params


def get_full_params(params):
    """
    Expands the fit parameters to the full list
    """
    full_params = np.zeros(len(params) + 2)
    full_params[0:2] = params[0:2]
    full_params[3:-1] = params[2:]
    full_params[-1] = 17.0
    
    return full_params


def plot_data_model(reddened_star, weights, modinfo, params_in, paramnames, starname, velocity, 
                    params_unc=None, prange=None):

    params = get_full_params(params_in)
    
    # intrinsic sed
    modsed = modinfo.stellar_sed(params[0:3], velocity=velocity)

    # dust_extinguished sed
    ext_modsed = modinfo.dust_extinguished_sed(params[3:10], modsed)

    # hi_abs sed
    hi_ext_modsed = modinfo.hi_abs_sed(
        params[10:12], [velocity, 0.0], ext_modsed
    )

    # create a StarData object for the best fit SED
    #modsed_stardata = modinfo.SED_to_StarData(modsed)

    norm_model = np.average(hi_ext_modsed["BAND"])
    norm_data = np.average(reddened_star.data["BAND"].fluxes).value

    # plotting setup for easier to read plots
    fontsize = 18
    font = {"size": fontsize}
    plt.rc("font", **font)
    plt.rc("lines", linewidth=1)
    plt.rc("axes", linewidth=2)
    plt.rc("xtick.major", width=2)
    plt.rc("xtick.minor", width=2)
    plt.rc("ytick.major", width=2)
    plt.rc("ytick.minor", width=2)

    # setup the plot
    fig, axes = plt.subplots(nrows=2, figsize=(13, 10), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

    # plot the bands and all spectra for this star
    ax = axes[0]
    for cspec in modinfo.fluxes.keys():
        if cspec == "BAND":
            ptype = "o"
        else:
            ptype = "-"

        # ax.plot(reddened_star.data[cspec].waves,
        #        weights[cspec], 'k-')

        gvals = reddened_star.data[cspec].fluxes > 0.0
        ax.plot(
            reddened_star.data[cspec].waves[gvals],
            reddened_star.data[cspec].fluxes[gvals] * np.power(reddened_star.data[cspec].waves[gvals], 4.0),
            "k" + ptype,
            label="data",
            alpha=0.7,
        )

        # print(reddened_star.data[cspec].waves)
        # print(modinfo.waves[cspec])

        ax.plot(
            modinfo.waves[cspec][gvals], 
            modsed[cspec][gvals] * (norm_data / norm_model) * np.power(modinfo.waves[cspec][gvals], 4.0), 
            "b" + ptype, 
            label=cspec,
            alpha=0.5,
        )
        ax.plot(
            modinfo.waves[cspec][gvals],
            ext_modsed[cspec][gvals] * (norm_data / norm_model) * np.power(modinfo.waves[cspec][gvals], 4.0),
            "r" + ptype,
            label=cspec,
            alpha=0.5,
        )
        modspec = hi_ext_modsed[cspec] * norm_data / norm_model
        ax.plot(
            modinfo.waves[cspec][gvals],
            modspec[gvals] * np.power(modinfo.waves[cspec][gvals], 4.0),
            "g" + ptype,
            label=cspec,
            alpha=0.5,
        )
        
        diff = 100.0 * (reddened_star.data[cspec].fluxes.value - modspec) / modspec
        axes[1].plot(reddened_star.data[cspec].waves, diff, "k" + ptype)

        
    # finish configuring the plot
    if prange is None:
        ax.set_ylim(4e5 * norm_data / norm_model, 1e7 * norm_data / norm_model)
    else:
        ax.set_ylim(prange)
    ax.set_yscale("log")
    ax.set_xscale("log")
    axes[1].set_xlabel(r"$\lambda$ [$\mu m$]", fontsize=1.3 * fontsize)
    ax.set_ylabel(r"$\lambda^4 F(\lambda)$ [RJ units]", fontsize=1.3 * fontsize)
    axes[1].set_ylabel("residuals [%]", fontsize=1.0 * fontsize)
    ax.tick_params("both", length=10, width=2, which="major")
    ax.tick_params("both", length=5, width=1, which="minor")
    axes[1].set_ylim(-10., 10.)
    axes[1].plot([0.1, 2.5], [0.0, 0.0], "k:")

    for k, (pname, pval) in enumerate(zip(paramnames, params_in)):
        if params_unc is not None:
            ptxt = fr"{pname} = ${pval:.2f} \pm {params_unc[k]:.2f}$"
        else:
            ptxt = f"{pname} = {pval:.2f}"
        ax.text(0.7, 0.5 - k*0.04, ptxt,
             horizontalalignment='left',
             verticalalignment='center',
             transform = ax.transAxes,
             fontsize=fontsize)
        
    ax.text(0.1, 0.9, starname, transform = ax.transAxes, fontsize=fontsize)
    
    # ax.legend()

    # use the whitespace better
    fig.tight_layout()