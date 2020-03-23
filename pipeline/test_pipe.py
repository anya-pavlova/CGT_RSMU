import subprocess
import sys
import glob
import os
from datetime import datetime

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

elif len(input_files) == 1:
    file1 = input_files[0].split("/")[-1]
    if input_files[0][-4:] == ".bam":
        input_file_types = "bam"
    elif file1[-3:] == ".fq" or file1[-3:] == "stq" or file1[-3:] == ".gz":
        input_file_types = "SE fq"
else:
    sys.exit("E: number of files in path not 1 or 2")

do_until = sys.argv[2]
do_until_list = ["trimming", "fastqc", "sam", "second_fastqc", "bam", "coverage", "vcf", "vcf_only", "ann", "analysis",
                 "full"]
if do_until not in do_until_list:
    sys.exit("E: instead of \"" + sys.argv[2] +
             "\" you can chouse: trimming, fastqc, sam," +
             " second_fastqc, bam, coverage, vcf, vcf_only, ann, analysis or full")

choose_ur_bed = sys.argv[3]
bed_list = ["V6", "V7"]
if choose_ur_bed not in bed_list:
    sys.exit("E: instead of \"" + sys.argv[3] +
             "\" you can chouse: V6 or V7")

print(file1[-3:])
print(input_file_types)

startTime = datetime.now()
print(str(datetime.now() - startTime) + " starting")
os.chdir(path)

# for quality test
process = subprocess.call(["/home/anyapavlova/downloads/FastQC/fastqc", "-t", "8", "-o",
                           path, path + "/" + file1])
if input_file_types == "PE fq":
    process = subprocess.call(["/home/anyapavlova/downloads/FastQC/fastqc", "-t", "8", "-o",
                               path, path + "/" + file2])
print(str(datetime.now() - startTime) + " for quality test")
if do_until == "fastqc":
    sys.exit("fastqc done")

# for trimming!!!!!!!!!!!!!!!!!!make_CROP_system!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! and change places with fastqc
process = subprocess.call(["java", "-jar",
                           "/home/bioinf/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                           "SE", "-threads", "8", path + "/" + file1, path + "/trimmed_" + file1, "HEADCROP:3"])
if input_file_types == "PE fq":
    process = subprocess.call(["java", "-jar",
                               "/home/bioinf/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                               "SE", "-threads", "8", path + "/" + file2, path + "/trimmed_" + file2, "HEADCROP:3"])
print(str(datetime.now() - startTime) + " for trimming")
if do_until == "trimming":
    sys.exit("trimming done")

# for mapping
if input_file_types == "PE fq":
    process = subprocess.call(["bowtie2", "-x",
                               "/home/bioinf/data/reference_human_hg19/Homo_" +
                               "sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome",
                               "-1", path + "/trimmed_" + file1, "-2", path + "/trimmed_" + file2, "-S",
                               path + "/" + sample_name + ".sam"])
elif input_file_types == "SE fq":
    process = subprocess.call(["bowtie2", "-x",
                               "/home/bioinf/data/reference_human_hg19/Homo_" +
                               "sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome",
                               "-U", path + "/trimmed_" + file1, "-S", path + "/" + sample_name + ".sam"])
print(str(datetime.now() - startTime) + " for mapping")

"""
OLD!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! os.system("bwa mem " +
            "/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/BWAIndex/version0.7.12/genome.fa " +
            path + "/trimmed_" + file1 + " " + path + "/trimmed_" + file2 + " > sudo " +
            path + "/" + sample_name + ".sam")"""

if do_until == "sam":
    sys.exit("sam done")

if do_until != "analysis":
    os.remove(path + "/trimmed_" + file1)
    if input_file_types == "PE fq":
        os.remove(path + "/trimmed_" + file2)

# for converting sam to bam
process = subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools",
                           "view", "-bS",
                           "-o", path + "/" + sample_name + ".bam",
                           "-@ 7",
                           path + "/" + sample_name + ".sam"])
print(str(datetime.now() - startTime) + " for converting sam to bam")
if do_until == "bam":
    sys.exit("bam done")

if do_until != "analysis":
    os.remove(path + "/" + sample_name + ".sam")

# here second fastqc
if do_until != "vcf_only":
    if not os.path.isdir(path + "/second"):
        os.makedirs(path + "/second")
    process = subprocess.call(["/home/anyapavlova/downloads/FastQC/fastqc", "-t", "8", "-o",
                               path + "/second", path + "/" + sample_name + ".sam"])
    print(str(datetime.now() - startTime) + " for second fastqc")
    if do_until == "second_fastqc":
        sys.exit("second_fastqc done")

# for sorting bams
process = subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "sort", "-o",
                           path + "/sorted_" + sample_name + ".bam", "--threads", "3", path + "/" + sample_name + ".bam"])
print(str(datetime.now() - startTime) + " for sorting bams")

if do_until != "analysis":
    os.remove(path + "/" + sample_name + ".bam")

# for cleaning from duplicates
process = subprocess.call(["java", "-jar", "/home/bioinf/programs/Picard/picard.jar",
                           "MarkDuplicates", "I=" + path + "/" + "sorted_" + sample_name + ".bam",
                           "O=" + path + "/marked_" + sample_name + ".bam", "M=" + path + "/marked_dup_metrics.txt",
                           "REMOVE_DUPLICATES=true"])
print(str(datetime.now() - startTime) + " for cleaning from duplicates")

if do_until != "analysis":
    os.remove(path + "/sorted_" + sample_name + ".bam")

# maybe indexing
os.chdir(path)
process = subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools",
                           "index", "nthreads=8",
                           "marked_" + sample_name + ".bam"])
print(str(datetime.now() - startTime) + " for indexing")

# for NGSrich (may be some problems with path)
os.chdir("/home/bioinf/programs/ngsrich/NGSrich_0.7.8/bin")
if choose_ur_bed == "V6":
    process = subprocess.call(["java", "NGSrich", "evaluate",
                               "-r", path + "/marked_" + sample_name + ".bam",
                               "-u", "hg19",
                               "-t", "/home/bioinf/dont_change/Exome-Agilent_V6.bed",
                               "-o", path + "/NGSrich"])
elif choose_ur_bed == "V7":
    process = subprocess.call(["java", "NGSrich", "evaluate",
                               "-r", path + "/marked_" + sample_name + ".bam",
                               "-u", "hg19",
                               "-t", "/home/bioinf/data/target/S31285117_Covered.bed",
                               "-o", path + "/NGSrich"])
os.chdir(path)
print(str(datetime.now() - startTime) + " for NGSrich")

# v6 bed /home/bioinf/dont_change/Exome-Agilent_V6.bed
# v7 bed /home/bioinf/data/target/S31285117_Covered.bed

# for mosdepth
if choose_ur_bed == "V6":
    os.system("/home/bioinf/programs/miniconda3/bin/mosdepth -t 4 --by /home/bioinf/dont_change/Exome-Agilent_V6.bed "
              + sample_name + " " + path + "/marked_" + sample_name + ".bam")
    process = subprocess.call(["python", "/home/bioinf/programs/miniconda3/pkgs/mosdepth-0.2.5-hb763d49_0/plot-dist.py",
                               path + "/" + sample_name + ".mosdepth.global.dist.txt"])
elif choose_ur_bed == "V7":
    os.system("/home/bioinf/programs/miniconda3/bin/mosdepth -t 4 --by /home/bioinf/data/target/S31285117_Covered.bed "
              + sample_name + " " + path + "/marked_" + sample_name + ".bam")
    process = subprocess.call(["python", "/home/bioinf/programs/miniconda3/pkgs/mosdepth-0.2.5-hb763d49_0/plot-dist.py",
                               path + "/" + sample_name + ".mosdepth.global.dist.txt"])
print(str(datetime.now() - startTime) + " for mosdepth")
if do_until == "coverage":
    sys.exit("coverage done")
