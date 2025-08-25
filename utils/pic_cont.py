import glob
import pickle
import time

from measure_extinction.modeldata import ModelData


if __name__ == "__main__":
    # model data
    start_time = time.time()
    print("reading model files")
    modstr = "wd_hubeny_"
    modpath = "/home/kgordon/Python/extstar_data/Models/"

    tlusty_models_fullpath = glob.glob(f"{modpath}/{modstr}*.dat")
    contfiles = []
    regfiles = []
    for cfile in tlusty_models_fullpath:
        if "cont" in cfile:
            contfiles.append(cfile)
        else:
            regfiles.append(cfile)

    for mtype in ["", "cont"]:

        if mtype == "cont":
            tlusty_models_fullpath = contfiles
        else:
            tlusty_models_fullpath = regfiles
        #tlusty_models_fullpath = glob.glob(f"{modpath}/{modstr}*{mtype}.dat")
        tlusty_models = [
            tfile[tfile.rfind("/") + 1 : len(tfile)] for tfile in tlusty_models_fullpath
        ]
        if len(tlusty_models) > 1:
            print(f"{len(tlusty_models)} model files found.")
        else:
            raise ValueError("no model files found.")

        # get the models with just the reddened star band data and spectra
        modinfo = ModelData(
            tlusty_models,
            path=f"{modpath}/",
            band_names=None,
            spectra_names=["BAND", "STIS", "STIS_Opt"],
        )
        pickle.dump(modinfo, open(f"{modstr}{mtype}_modinfo.p", "wb"))
        print("finished reading model files")
        print("--- %s seconds ---" % (time.time() - start_time))