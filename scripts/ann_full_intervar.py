import sys
import glob
import os

path = sys.argv[1]  # path to run with samples
if sys.argv[1][-1:] == "/":
    path = sys.argv[1][:-1]

for filename in glob.glob(path+"/*"):
    if filename.split("/")[-1] in ["100a", "101a", "102a", "103a", "104a", "105a", "106a", "107a"]:
        os.system("grep \"Pathogenic\" "+filename+"/"+filename.split("/")[-1]+"_InterVar.hg19_multianno.txt > /home/robert/pat_ann_for" + filename.split("/")[-1] + ".txt")
        os.system("grep \"Likely_pathogenic\" "+filename+"/"+filename.split("/")[-1]+"_InterVar.hg19_multianno.txt > /home/robert/like_ann_for" + filename.split("/")[-1] + ".txt")
        os.system("grep \"Uncertain_significance\" "+filename+"/"+filename.split("/")[-1]+"_InterVar.hg19_multianno.txt > /home/robert/uncertain_ann_for" + filename.split("/")[-1] + ".txt")
        try:
            with open("/home/robert/pat_ann_for" + filename.split("/")[-1] + ".txt", "r") as f2:
                with open("/home/robert/ann_no_genes" + filename.split("/")[-1] + ".txt", "a") as f5:
                    f5.write(f2.read())
        except FileNotFoundError:
            pass
        try:
            with open("/home/robert/like_ann_for" + filename.split("/")[-1] + ".txt", "r") as f3:
                with open("/home/robert/ann_no_genes" + filename.split("/")[-1] + ".txt", "a") as f5:
                    f5.write(f3.read())
        except FileNotFoundError:
            pass
        try:
            with open("/home/robert/uncertain_ann_for" + filename.split("/")[-1] + ".txt", "r") as f4:
                with open("/home/robert/ann_no_genes" + filename.split("/")[-1] + ".txt", "a") as f5:
                    f5.write(f4.read())
        except FileNotFoundError:
            pass
        try:
            os.remove("/home/robert/pat_ann_for" + filename.split("/")[-1] + ".txt")
            os.remove("/home/robert/like_ann_for" + filename.split("/")[-1] + ".txt")
            os.remove("/home/robert/uncertain_ann_for" + filename.split("/")[-1] + ".txt")
        except FileNotFoundError:
            pass

