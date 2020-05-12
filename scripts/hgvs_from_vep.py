import sys
import os

name_in = sys.argv[1]
name_out = sys.argv[2]

with open(name_out, "a") as out:
    with open(name_in, "r") as input:
        for line in input:
            if line[0] != "#":
                # print(line.split(";"))
                if "HGVSc" in line:
                    if ";" in line.split("HGVSc")[1]:
                        os.system(
                            "sudo bash -c \"transvar canno --ccds -i \\\"" + line.split("HGVSc")[1].split(";")[0][1:] +
                            "\\\" --refversion hg19 --ensembl > transvar_output.txt\"")
                        with open("transvar_output.txt", "r") as result:
                            is_it_any_strings = 0
                            for k, stroka in enumerate(result):
                                is_it_any_strings += 1
                                if k == 1:
                                    all_formats = stroka.split("\t")[-3]
                        if is_it_any_strings == 2:
                            out.write(line[:-1] + ";" + all_formats + "\n")
                        else:
                            out.write(line)
                        os.remove("transvar_output.txt")
                    else:
                        os.system("sudo bash -c \"transvar canno --ccds -i \\\"" + line.split("HGVSc")[1][1:-1] +
                                  "\\\" --refversion hg19 --ensembl > transvar_output.txt\"")
                        with open("transvar_output.txt", "r") as result:
                            is_it_any_strings = 0
                            for k, stroka in enumerate(result):
                                is_it_any_strings += 1
                                if k == 1:
                                    all_formats = stroka.split("\t")[-3]
                        if is_it_any_strings == 2:
                            out.write(line[:-1] + ";" + all_formats + "\n")
                        else:
                            out.write(line)
                        os.remove("transvar_output.txt")
                else:
                    out.write(line)
            else:
                out.write(line)
