import os
import argparse

from measure_extinction.utils.helpers import read_bohlin
from measure_extinction.merge_obsspec import (
    obsspecinfo,
    merge_gen_obsspec,
    merge_stis_obsspec,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--medwds", help="process WD stars (mediumwds)", action="store_true")
    parser.add_argument("--miscwds", help="process misc WD stars (miscwds)", action="store_true")
    args = parser.parse_args()


    # fmt: off
    if args.medwds:
        names = ["wd0148_467", "wd0227_050", "wd0809_177", "wd1105_048", "wd1105_340", "wd1327_083",
                 "wd1713_695", "wd1911_536", "wd1919_145", "wd2039_682", "wd2117_539", "wd2126_734",
                 "wd2149_021",
                 "hz4", "wd1202_232", "wd1544_377", "wd2341_322"]   # hz4 = WD0352_096
        path = "data/mediumwds/"
    elif args.miscwds:
        names = ["grw_70d5824", "sdss132811", "wd1057_719", "wd1657_343",
                 "wdj040027", "wdj041345", "wdj174911", "wdj175318", "wdj181144"]
        path = "data/miscwds/"
    else:
        names = ["wdfs0122_30", "wdfs0248_33", "wdfs0458_56", "wdfs0639_57", "wdfs0956_38", "wdfs1055_36",
                "wdfs1110_17", "wdfs1206_27", "wdfs1214_45", "wdfs1302_10", "wdfs1434_28", "wdfs1514_00",
                "wdfs1535_77", "wdfs1557_55", "wdfs1814_78", "wdfs1837_70", "wdfs1930_52", "wdfs2317_29",
                "wdfs2351_37"]
        path = "data/faintwds/"
    # fmt: on

    for cname in names:
        print(f"working on {cname}")

        for cspec in ["wfc3_g102", "wfc3_g141"]:
            grating = cspec.split("_")[1]
            cfile = f"{path}wfc3/{cname}.{grating}"
            if os.path.exists(cfile):
                tab = read_bohlin(cfile)

                cres = obsspecinfo[cspec][0]

                rb_info = merge_gen_obsspec(
                    [tab], obsspecinfo[cspec][1], output_resolution=cres
                )

                ofile = f"{path}{cname}_{cspec}.fits"
                rb_info.write(ofile, overwrite=True)

        for cspec in ["stis_g430l", "stis_g750l"]:
            grating = cspec.split("_")[1]
            cfile = f"{path}stis/{cname}.{grating}"
            if os.path.exists(cfile):
                tab = read_bohlin(cfile)

                rb_info = merge_stis_obsspec([tab], waveregion="Opt")

                ofile = f"{path}{cname}_{cspec}.fits"
                rb_info.write(ofile, overwrite=True)

        for cspec in ["stis_g140l", "stis_g230l"]:
            grating = cspec.split("_")[1]
            cfile = f"{path}stis/{cname}.{grating}"
            if os.path.exists(cfile):
                tab = read_bohlin(cfile)

                rb_info = merge_stis_obsspec([tab], waveregion="UV")

                ofile = f"{path}{cname}_{cspec}.fits"
                rb_info.write(ofile, overwrite=True)
