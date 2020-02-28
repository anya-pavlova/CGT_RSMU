import sys
import glob
import os

path = sys.argv[1]  # path to run with samples
if sys.argv[1][-1:] == "/":
    path = sys.argv[1][:-1]
genes = sys.argv[2].split(",")

for filename in glob.glob(path+"/*"):
    if filename.split("/")[-1] in ["100a","101a","102a","103a","104a","105a","106a","107a"]:
        for gene in genes:
            os.system("grep \""+gene+"\" "+filename+"/"+filename.split("/")[-1]+"_InterVar.hg19_multianno.txt > /home/zlobert/raw_ann_for"+filename.split("/")[-1]+".txt")
            with open("/home/zlobert/raw_ann_for"+filename.split("/")[-1]+".txt", "r") as f2:
                with open("/home/zlobert/ann_for" + filename.split("/")[-1] + ".txt", "a") as f5:
                    f5.write(f2.read())
        os.system("grep \"Pathogenic\" /home/zlobert/ann_for"+filename.split("/")[-1]+".txt > /home/zlobert/pat_ann_for" + filename.split("/")[-1] + ".txt")
        os.system("grep \"Likely_pathogenic\" /home/zlobert/ann_for" + filename.split("/")[-1] + ".txt > /home/zlobert/like_ann_for" + filename.split("/")[-1] + ".txt")
        os.system("grep \"Uncertain_significance\" /home/zlobert/ann_for" + filename.split("/")[-1] + ".txt > /home/zlobert/us_ann_for" + filename.split("/")[-1] + ".txt")

        with open("/home/zlobert/pat_ann_for" + filename.split("/")[-1] + ".txt", "r") as f2:
            with open("/home/zlobert/big_ann_for_" + filename.split("/")[-1] + ".txt", "a") as f5:
                f5.write(f2.read())
        with open("/home/zlobert/like_ann_for" + filename.split("/")[-1] + ".txt", "r") as f3:
            with open("/home/zlobert/big_ann_for_" + filename.split("/")[-1] + ".txt", "a") as f5:
                f5.write(f3.read())
        with open("/home/zlobert/us_ann_for" + filename.split("/")[-1] + ".txt", "r") as f4:
            with open("/home/zlobert/big_ann_for_" + filename.split("/")[-1] + ".txt", "a") as f5:
                f5.write(f4.read())
        for gene in genes:
            try:
                os.remove("/home/zlobert/raw_ann_for"+filename.split("/")[-1]+".txt")
                os.remove("/home/zlobert/ann_for" + filename.split("/")[-1] + ".txt")
                os.remove("/home/zlobert/pat_ann_for" + filename.split("/")[-1] + ".txt")
                os.remove("/home/zlobert/like_ann_for" + filename.split("/")[-1] + ".txt")
                os.remove("/home/zlobert/us_ann_for" + filename.split("/")[-1] + ".txt")
                os.remove("/home/zlobert/"+gene+"_ann_for"+filename.split("/")[-1]+".txt")
            except FileNotFoundError:
                pass

