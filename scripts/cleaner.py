import sys
import os
import glob

list_will = sys.argv[1].split(",") # should be list
path_to_dir = os.getcwd()

for filename in glob.glob(path_to_dir + "/*"):
    if filename.split("/")[-1] not in list_will:
        print(filename)
        try:
            os.remove(filename)
        except IsADirectoryError:
            os.system("rm -r "+filename)
