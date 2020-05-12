import subprocess
import sys
import glob
import os
from datetime import datetime
from shutil import unpack_archive, make_archive

path = sys.argv[1]
if sys.argv[1][-1:] == "/":
    path = sys.argv[1][:-1]
sample_name = path.split("/")[-1]

input_files = []
for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] == sample_name + "_1.fq.gz" or filename.split("/")[-1] == sample_name + "_2.fq.gz":
        input_files.append(filename)
if len(input_files) == 0:
    for filename in glob.glob(path + "/*"):
        if filename.split("/")[-1] != "nohup.out":
            input_files.append(filename)
input_files = sorted(input_files)
print(input_files)

input_file_types = "idk"
if len(input_files) == 2:
    file1 = input_files[0].split("/")[-1]
    file2 = input_files[1].split("/")[-1]
    input_file_types = "PE fq"

# make smarter bam switch

elif len(input_files) == 1:
    file1 = input_files[0].split("/")[-1]
    if input_files[0][-4:] == ".bam":
        input_file_types = "bam"
    elif file1[-3:] == ".fq" or file1[-3:] == "stq" or file1[-3:] == ".gz":
        input_file_types = "SE fq"
else:
    sys.exit("E: number of files in path not 1 or 2")

do_until = sys.argv[2]
do_until_list = ["trimming", "fastqc", "sam", "second_fastqc", "bam", "marked_bam", "coverage", "vcf", "vcf_only", "ann", "analysis",
                 "full"]
if do_until not in do_until_list:
    sys.exit("E: instead of \"" + sys.argv[
        2] + "\" you can choose: trimming, fastqc, sam, second_fastqc, bam, marked_bam, coverage, vcf, vcf_only, ann, analysis or full")

print(file1[-3:])
print(input_file_types)

startTime = datetime.now()
print(str(datetime.now() - startTime) + " starting")
os.chdir(path)

# sort fastq


# for trimming
process = subprocess.check_call(["java", "-jar",
                                 "/home/bioinf/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                                 "SE", "-threads", "2", path + "/" + file1, path + "/trimmed" + file1,
                                 "HEADCROP:3"])
if input_file_types == "PE fq":
    process = subprocess.check_call(["java", "-jar",
                                     "/home/bioinf/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                                     "SE", "-threads", "2", path + "/" + file2, path + "/trimmed" + file2,
                                     "HEADCROP:3"])
print(str(datetime.now() - startTime) + " for trimming")
if do_until != "analysis":
    os.chdir(path)
    os.system("sudo rm *.fq")
if do_until == "trimming":
    sys.exit("trimming done")

# for quality test
"""process = subprocess.check_call(["/home/anyapavlova/downloads/FastQC/fastqc", "-t", "2", "-o",
                                 path, path + "/trimmed" + file1])
if input_file_types == "PE fq":
    process = subprocess.check_call(["/home/anyapavlova/downloads/FastQC/fastqc", "-t", "2", "-o",
                                     path, path + "/trimmed" + file2])
print(str(datetime.now() - startTime) + " for quality test")
if do_until == "fastqc":
    sys.exit("fastqc done")"""

# for mapping
os.system("bwa mem " +
          "/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/BWAIndex/version0.7.12/genome.fa " +
          path + "/trimmed" + file1 + " " + path + "/trimmed" + file2 + " -t 2 > " + path + "/" + sample_name + ".sam")
if do_until == "sam":
    sys.exit("sam done")

if do_until != "analysis":
    os.remove(path + "/trimmed" + file1)
    if input_file_types == "PE fq":
        os.remove(path + "/trimmed" + file2)
print(str(datetime.now()-startTime)+" for mapping")

# for converting sam to bam
process = subprocess.check_call(["/home/bioinf/programs/samtools/samtools-1.9/samtools",
                                 "view", "-bS",
                                 "-o", path + "/" + sample_name + ".bam",
                                 path + "/" + sample_name + ".sam"])
print(str(datetime.now() - startTime) + " for converting sam to bam")
if do_until == "bam":
    sys.exit("bam done")

if do_until != "analysis":
    os.remove(path + "/" + sample_name + ".sam")

# here second fastqc
"""if do_until != "vcf_only":
    if not os.path.isdir(path + "/second"):
        os.makedirs(path + "/second")
    process = subprocess.check_call(["/home/anyapavlova/downloads/FastQC/fastqc", "-o",
                                     path + "/second", path + "/" + sample_name + ".sam"])
    print(str(datetime.now() - startTime) + " for second fastqc")
    if do_until == "second_fastqc":
        sys.exit("second_fastqc done")"""

# for sorting bams
process = subprocess.check_call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "sort", "-o",
                                 path + "/sorted_" + sample_name + ".bam", path + "/" + sample_name + ".bam"])
print(str(datetime.now() - startTime) + " for sorting bams")

if do_until != "analysis":
    os.remove(path + "/" + sample_name + ".bam")

# for cleaning from duplicates
process = subprocess.check_call(["java", "-jar", "/home/bioinf/programs/Picard/picard.jar",
                                 "MarkDuplicates", "I=" + path + "/" + "sorted_" + sample_name + ".bam",
                                 "O=" + path + "/marked_" + sample_name + ".bam",
                                 "M=" + path + "/marked_dup_metrics.txt",
                                 "REMOVE_DUPLICATES=true"])
print(str(datetime.now() - startTime) + " for cleaning from duplicates")
if do_until != "analysis":
    os.remove(path + "/sorted_" + sample_name + ".bam")
