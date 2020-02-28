import glob
import os
import subprocess
import sys

path = sys.argv[1]
ngs_rich_ready = []
ngs_rich_not = []

for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] not in ["nohup.out", "tabl.csv", "RDKB_N113a_reb", "2019108", "nmicgap_2019118",
                                       "2019109", "2019105", "2019115", "2019111", "nmicgap_2019120", "nmicgap_2019117",
                                       "2019122", "RDKB_N112a_reb"]:
        try:
            with open(filename + "/NGSrich/marked_" + filename.split("/")[-1] + "_enrichment.html", "r") as f:
                print("in")
                print(filename)
                ngs_rich_ready.append(filename)
        except FileNotFoundError:
            print("not in")
            print(filename)
            ngs_rich_not.append(filename)
            os.chdir(filename)
            os.system("cleaner "+filename.split("/")[-1]+"_1.fq.gz,"+filename.split("/")[-1]+"_2.fq.gz")
    elif filename.split("/")[-1] in ["RDKB_N113a_reb", "2019108", "nmicgap_2019118",
                                     "2019109", "2019105", "2019115", "2019111", "nmicgap_2019120",
                                     "nmicgap_2019117", "2019122", "RDKB_N112a_reb"]:
        print("not in")
        print(filename)
        ngs_rich_not.append(filename)
        os.chdir(filename)
        os.system("cleaner " + filename.split("/")[-1] + "_1.fq.gz," + filename.split("/")[-1] + "_2.fq.gz")
for filename in ngs_rich_not:
    process = subprocess.Popen(["sudo", "nohup", "python3.5", "/home/bioinf/pipeline/pipe_v6.py",
                                filename, "coverage"])

"""for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] in ["nmicgap_2019116"]:
        os.chdir("/home/bioinf/programs/ngsrich/NGSrich_0.7.8/bin")
        process = subprocess.Popen(["nohup", "java", "NGSrich", "evaluate",
                                    "-r", filename + "/marked_" + filename.split("/")[-1] + ".bam",
                                    "-u", "hg19",
                                    "-t", "/home/bioinf/data/target/S31285117_Covered.bed",
                                    "-o", filename + "/NGSrich"])"""