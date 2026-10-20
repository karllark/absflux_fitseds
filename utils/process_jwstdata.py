import os
import numpy as np
from astropy import units as u
from astropy.table import QTable

from measure_extinction.merge_obsspec import (
    obsspecinfo,
    merge_gen_obsspec,
)


if __name__ == "__main__":

    # fmt: off
    wdnames = ["wd1657+343"]
    # fmt: on
    names = wdnames
    path = "data/whitedwarfs/"

    for cname in names:
        print(f"working on {cname}")

        for cspec in ["nirspec_g140m_f070lp", "nirspec_g140m_f100lp", "nirspec_g235m_f170lp", "nirspec_g395m_f290lp"]:
            grating = cspec.split("_")[1]
            filter = cspec.split("_")[2]
            cfile = f"{path}nirspec/{cname}_m_{grating.upper()}_{filter.upper()}_NRS1_pfpc_x1d.fits"
            print(cfile)
            if os.path.exists(cfile):
                tab = QTable.read(cfile)
                print(tab.colnames)
                tab.rename_column("FLUX_ERROR", "ERROR")
                tab["WAVELENGTH"] *= u.micron
                tab["NPTS"] = np.full((len(tab["FLUX"])), 1.0)
                tab["NPTS"][tab["FLUX"] == 0.0] = 0.0

                rb_info = merge_gen_obsspec(
                    [tab], obsspecinfo[cspec][1], output_resolution=obsspecinfo[cspec][0]
                )

                ofile = f"{path}{cname}_{cspec}.fits"
                rb_info.write(ofile, overwrite=True)

