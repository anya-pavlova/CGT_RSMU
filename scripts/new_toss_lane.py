import sys
import os
import argparse
import subprocess
import logging
from shutil import move, copyfile, copy
from collections import defaultdict

parser = argparse.ArgumentParser()

parser.add_argument("path_to_run", help="Source path to run")
parser.add_argument("run_name", help="Name of the run")
parser.add_argument("lanes", help="Lane numbers splitted by ';'")
parser.add_argument("bar_codes", help="Bar codes splitted by ',' for one lane. "
                                      "Groups of bar codes for different lanes should be splitted by ';'")
parser.add_argument("new_path", help="Destination path")
parser.add_argument("sample_name", help="Name of the sample")

args = parser.parse_args()

root_output_folder = os.path.join(args.new_path, args.run_name, args.sample_name)

if not os.path.isdir(root_output_folder):
    os.makedirs(root_output_folder)

lanes = args.lanes.split("/")
lanes_bar_codes = [lane_bar_codes.split(",") for lane_bar_codes in args.bar_codes.split("/")]

if len(lanes) != len(lanes_bar_codes):
    logging.error("Number of lanes is not equal to number of bar codes groups")
    exit(1)


files_groups = defaultdict(list)

for lane, lane_bar_codes in zip(lanes, lanes_bar_codes):
    input_folder = os.path.join(args.path_to_run, args.run_name, "L0{}".format(lane))
    for bar_code in lane_bar_codes:
        for read in ["1", "2"]:
            filename = "{}_L0{}_{}_{}.fq.gz".format(args.run_name, lane, bar_code, read)
            filepath = os.path.join(input_folder, filename)
            files_groups[(lane, read)].append(filepath)


for (lane, read), filepaths in files_groups.items():
    output_folder = os.path.join(root_output_folder, "lane_{}".format(lane))
    os.makedirs(output_folder, exist_ok=True)

    output_filename = "{}_L0{}_{}.fq.gz".format(args.sample_name, lane, read)
    output_filepath = os.path.join(output_folder, output_filename)

    if len(filepaths) == 1:
        copyfile(filepaths[0], output_filepath)
    else:
        with open(output_filepath, "wb") as f:
            subprocess.check_call(["cat", *filepaths], stdout=f)

