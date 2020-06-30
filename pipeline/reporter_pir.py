from bs4 import BeautifulSoup
import sys
import glob

path = sys.argv[1]
if sys.argv[1][-1:] == "/":
    path = sys.argv[1][:-1]

with open(path + "/tabl.csv", "w") as f:
    f.write("sample\tReads\tOn Target +- 100 bp\tCoverage percent\tDup\tInsert size\tELS\tTarget " +
            "Size\tTarget Regions\tCoverage " +
            "Mean\tCoverage Std Dev\tCovered 1x\tCovered 5x\tCovered 10x\tCovered 20x\tCovered 30x\tTPKM\tCovered 13x\n")

for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] not in ["nohup.out", "tabl.csv"]:
        try:
            with open(filename + "/NGSrich/marked_" + filename.split("/")[-1] + "_enrichment.html", "r") as f:
                sample_str = [filename.split("/")[-1]]
                contents = f.read()
                soup = BeautifulSoup(contents, 'lxml')
                for el in soup.find('table', {'class': 'output'}):
                    if el != '\n':
                        # print(str(el).split("<td>")[1].split("</b>")[0][3:])
                        sample_str.append(str(el).split("<td>")[2].split("</td>")[0])
                print(sample_str)
            x13 = ((float(sample_str[9][:-1]) - float(sample_str[10][:-1])) * 0.7) + float(sample_str[10][:-1])
            try:
                with open(filename + "/lane_1/marked_dup_metrics.txt", "r") as f3:
                    for k, line in enumerate(f3):
                        if k == 7:
                            Dups = line.split("\t")[8]
                            ELS = line.split("\t")[9][:-1]
            except FileNotFoundError:
                try:
                    with open(filename + "/lane_2/marked_dup_metrics.txt", "r") as f3:
                        for k, line in enumerate(f3):
                            if k == 7:
                                Dups = line.split("\t")[8]
                                ELS = line.split("\t")[9][:-1]
                except FileNotFoundError:
                    try:
                        with open(filename + "/lane_3/marked_dup_metrics.txt", "r") as f3:
                            for k, line in enumerate(f3):
                                if k == 7:
                                    Dups = line.split("\t")[8]
                                    ELS = line.split("\t")[9][:-1]
                    except FileNotFoundError:
                        try:
                            with open(filename + "/lane_4/marked_dup_metrics.txt", "r") as f3:
                                for k, line in enumerate(f3):
                                    if k == 7:
                                        Dups = line.split("\t")[8]
                                        ELS = line.split("\t")[9][:-1]
                        except FileNotFoundError:
                            print("dup not ready: " + filename)
            with open(filename + "/insert_size_metrics.txt", "r") as f4:
                for k, line in enumerate(f4):
                    if k == 7:
                        insert_size = line.split("\t")[0]
            with open(path + "/tabl.csv", "a") as f2:
                f2.write("\t".join(
                    sample_str[:3] + [str(round(round(int(sample_str[2]) / int(sample_str[1]), 3) * 100, 2)) + "%"] +
                    [str(round(round(float(Dups), 3) * 100, 2)) + "%"] + [insert_size] + [str(ELS)] + sample_str[3:] +
                    [str(x13)]) + "\n")
        except FileNotFoundError:
            print("not ready: "+filename)
