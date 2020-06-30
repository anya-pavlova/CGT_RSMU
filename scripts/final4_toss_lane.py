import argparse
import os
from shutil import copyfile

import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument("path_to_run", help="Source path to run")
parser.add_argument("new_path", help="Destination path")
parser.add_argument("samples_table", help="Path to samples table")

args = parser.parse_args()


def input_file_path(lane, adaptor, read):
    run_name = os.path.split(args.path_to_run)[-1]
    input_folder = os.path.join(args.path_to_run, "L0{}".format(lane))
    input_filename = "{}_L0{}_{}_{}.fq.gz".format(run_name, lane, adaptor, read)
    return os.path.join(input_folder, input_filename)


def output_file_path(project, sample_name, lane, adaptor, read, make_dir=True):
    output_folder = os.path.join(
        args.new_path,
        project,
        sample_name,
        "lane_{}".format(lane),
        "adaptor_{}".format(adaptor)
    )
    if make_dir:
        os.makedirs(output_folder, exist_ok=True)

    output_filename = "{}_L0{}_{}.fq.gz".format(sample_name, lane, read)
    return os.path.join(output_folder, output_filename)


def process_one_row(row):
    for lane in range(1, 5):
        adaptors = row['lane {}'.format(lane)]
        if not adaptors:
            continue

        adaptors = str(adaptors).split(",")

        for adaptor in adaptors:
            for read in ["1", "2"]:
                copyfile(
                    input_file_path(lane, adaptor, read),
                    output_file_path(row["proekty"], row["library"], lane, adaptor, read)
                )


samples_table = pd.read_csv(args.samples_table, sep='\t', dtype=str, na_filter=False)
for _, row in samples_table.iterrows():
    process_one_row(row)
