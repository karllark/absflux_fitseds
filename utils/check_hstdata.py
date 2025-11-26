import os
import filecmp
import shutil

if __name__ == "__main__":

    obspath = f"data/whitedwarfs/"
    obstypes = ["stis", "wfc3"]
    ralphpath = ["/user/bohlin/stiscal/dat/", "/user/bohlin/wfc3/spec/"]
    for otype, rpath in zip(obstypes, ralphpath):

        print(f"checking {otype} files")

        path = f"{obspath}{otype}/"
        all_entries = os.listdir(path)
        files = [
            entry for entry in all_entries if os.path.isfile(os.path.join(path, entry))
        ]
        for cfile in sorted(files):
            file1 = f"{path}{cfile}"
            tpath = rpath
            if (otype == "stis") & ("wdfs" in cfile):
                tpath = tpath.replace("dat", "narayan")
            file2 = f"{tpath}{cfile}"
            if os.path.exists(file2):
                if not filecmp.cmp(file1, file2, shallow=False):
                    shutil.copyfile(file2, file1)
                    print(f"{cfile} updated from origin dir")
            else:
                print(f"{cfile} not present in origin dir")
