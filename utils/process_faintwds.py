from measure_extinction.utils.helpers import read_bohlin
from measure_extinction.merge_obsspec import (
    obsspecinfo,
    merge_gen_obsspec,
    merge_stis_obsspec,
)


if __name__ == "__main__":

    names = ["wdfs1302_10"]

    path = "data/faintwds/"
    for cname in names:

        for cspec in ["wfc3_g102", "wfc3_g141"]:
            grating = cspec.split("_")[1]
            tab = read_bohlin(f"{path}wfc3/{cname}.{grating}")

            cres = obsspecinfo[cspec][0]

            rb_info = merge_gen_obsspec(
                [tab], obsspecinfo[cspec][1], output_resolution=cres
            )

            ofile = f"{path}{cname}_{cspec}.fits"
            rb_info.write(ofile, overwrite=True)

        for cspec in ["stis_g140l", "stis_g230l"]:
            grating = cspec.split("_")[1]
            tab = read_bohlin(f"{path}stis/{cname}.{grating}")

            rb_info = merge_stis_obsspec([tab], waveregion="UV")

            ofile = f"{path}{cname}_{cspec}.fits"
            rb_info.write(ofile, overwrite=True)
