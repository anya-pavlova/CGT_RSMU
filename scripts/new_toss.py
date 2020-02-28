import sys
import os
import argparse
import subprocess
import logging
from shutil import move, copy
from glob import glob

parser = argparse.ArgumentParser()

parser.add_argument("path_to_run", help="Source path to run")
parser.add_argument("run_name", help="Name of the run")
parser.add_argument("lanes", help="Lane numbers splitted by ';'")
parser.add_argument("bar_codes", help="Bar codes splitted by ',' for one lane. "
                                      "Groups of bar codes for different lanes should be splitted by ';'")
parser.add_argument("new_path", help="Destination path")
parser.add_argument("sample_name", help="Name of the sample")

args = parser.parse_args()

output_folder = os.path.join(args.new_path, args.run_name, args.sample_name)

if not os.path.isdir(output_folder):
    os.makedirs(output_folder)

lanes = args.lanes.split("/")
lanes_bar_codes = [lane_bar_codes.split(",") for lane_bar_codes in args.bar_codes.split("/")]

if len(lanes) != len(lanes_bar_codes):
    logging.error("Number of lanes is not equal to number of bar codes groups")
    exit(1)

for lane, lane_bar_codes in zip(lanes, lanes_bar_codes):
    input_folder = os.path.join(args.path_to_run, args.run_name, "L0{}".format(lane))
    for bar_code in lane_bar_codes:
        for read in ["1", "2"]:
            file_name = "{}_L0{}_{}_{}.fq.gz".format(args.run_name, lane, bar_code, read)
            copy(os.path.join(input_folder, file_name), os.path.join(output_folder, file_name))

for read in ["1", "2"]:
    pattern = "**_{}.fq.gz".format(read)
    pattern_with_path = os.path.join(output_folder, pattern)
    files_to_concat = glob(pattern_with_path)
    output_filename = "{}_{}.fq.gz".format(args.sample_name, read)
    output_filepath = os.path.join(output_folder, output_filename)
    with open(output_filepath, "wb") as f:
        subprocess.check_call(["cat", *files_to_concat], stdout=f)

