import os
import filecmp
import shutil

if __name__ == "__main__":

    obspath = f"data/whitedwarfs/"
    obstypes = ["stis"]
    ralphpath = ["/user/bohlin/stiscal/dat/"]
    for otype, rpath in zip(obstypes, ralphpath):

        path = f"{obspath}{otype}/"
        all_entries = os.listdir(path)
        files = [
            entry for entry in all_entries if os.path.isfile(os.path.join(path, entry))
        ]
        for cfile in sorted(files):
            file1 = f"{path}{cfile}"
            file2 = f"{rpath}{cfile}"
            if os.path.exists(file2):
                if filecmp.cmp(file1, file2, shallow=False):
                    print(f"{cfile} is up-to-date")
                else:
                    shutil.copyfile(file2, file1)
                    print(f"{cfile} updated from origin dir")
            else:
                print(f"{cfile} not present in origin dir")