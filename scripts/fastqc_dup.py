import subprocess
import os
import zipfile
from collections import defaultdict
import pandas as pd
import numpy as np
import sys

def list_folders(path):
    folders = []
    for dirname in os.listdir(path):
        full_dirname = os.path.join(path, dirname)
        if os.path.isdir(full_dirname):
            folders.append(dirname)
    return folders


input_folder = sys.argv[1]
folders_name = list_folders(input_folder)

folders_name = [line for line in folders_name if not line.startswith('.')]

deduplicated_percentages = defaultdict(dict)

keyword = 'fastqc.zip'
for folder in folders_name:
    full_dir = os.path.join(input_folder, folder)
    zip_file_found = False
    for fname in os.listdir(full_dir):
        if keyword in fname:
            print(fname, "has the keyword")
            zip_file_found = True
            with zipfile.ZipFile(os.path.join(full_dir, fname), 'r') as zip_ref:
                zip_ref.extractall(full_dir)

            file_list = os.listdir(os.path.join(full_dir, fname[:-4]))
            # fastqc_data.txt
            fname_without_extension = fname[:-4]
            filename = os.path.join(full_dir, fname_without_extension, 'fastqc_data.txt')
            with open(filename) as f:
                line_start = "#Total Deduplicated Percentage"
                for line in f:
                    if line.startswith(line_start):
                        stripped_line = line[len(line_start):]
                        stripped_line = stripped_line.strip()
                        value = float(stripped_line)
                        read = fname_without_extension.split("_")[-2]
                        deduplicated_percentages[folder][read] = value

    if not zip_file_found:
        print("Zip file not found in {}".format(full_dir))


table = []
for folder, reads in deduplicated_percentages.items():
    table.append((folder, reads.get("1", np.nan), reads.get("2", np.nan)))
table = pd.DataFrame(table, columns=["sample", "reads1", "reads_2"])
table.to_excel(os.path.join(input_folder, "data_dup.xlsx"), index=False)



