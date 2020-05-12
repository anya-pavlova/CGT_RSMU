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

if len(input_files) == 2:
    not_sorted_files = [file1, file2]
else:
    not_sorted_files = [file1]

sorted_files = []

for input_file in not_sorted_files:
    # /home/bioinf/programs/fastq_sort/fastq-tools-0.8/src/fastq-sort --id 2019127_1.fq.gz > 2019127_1_sort.fq.gz

    name_parts = input_file.split(".")
    name_without_extension = name_parts[0]

    subprocess.check_call(["gunzip", "-k", os.path.join(path, input_file)])
    file_without_gz_extension = ".".join((name_without_extension, name_parts[1]))

    output_file = ".".join((name_without_extension + "_sort", name_parts[1]))
    output_path = os.path.join(path, output_file)

    with open(output_path, "wb") as out:
        subprocess.check_call(
            [
                "/home/bioinf/programs/fastq_sort/fastq-tools-0.8/src/fastq-sort",
                "--id", os.path.join(path, file_without_gz_extension)
            ],
            stdout=out
        )

    sorted_files.append(output_file)
    print(str(datetime.now() - startTime) + " for sort fq")

# for trimming!!!!!!!!!!!!!!!!!!make_CROP_system!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! and change places with fastqc
process = subprocess.check_call(["java", "-jar",
                                 "/home/bioinf/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                                 "SE", "-threads", "2", path + "/" + sorted_files[0], path + "/trimmed" + file1,
                                 "HEADCROP:3"])
if input_file_types == "PE fq":
    process = subprocess.check_call(["java", "-jar",
                                     "/home/bioinf/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                                     "SE", "-threads", "2", path + "/" + sorted_files[1], path + "/trimmed" + file2,
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

# maybe indexing
os.chdir(path)
process = subprocess.check_call(["/home/bioinf/programs/samtools/samtools-1.9/samtools",
                                 "index",
                                 "marked_" + sample_name + ".bam"])
print(str(datetime.now() - startTime) + " for indexing")
if do_until == "marked_bam":
    sys.exit("marked_bam done")

# for NGSrich (may be some problems with path)
os.chdir("/home/bioinf/programs/ngsrich/NGSrich_0.7.8/bin")
process = subprocess.check_call(["java", "NGSrich", "evaluate",
                                 "-r", path + "/marked_" + sample_name + ".bam",
                                 "-u", "hg19",
                                 "-t", "/home/bioinf/data/target/S31285117_Covered.bed",
                                 "-o", path + "/NGSrich"])
os.chdir(path)

print(str(datetime.now() - startTime) + " for NGSrich")

# v6 bed /home/bioinf/dont_change/Exome-Agilent_V6.bed
# v7 bed /home/bioinf/data/target/S31285117_Covered.bed

# for mosdepth
os.system(
    "/home/bioinf/programs/miniconda3/bin/mosdepth --by /home/bioinf/data/target/S31285117_Covered.bed " + sample_name + " " + path + "/marked_" + sample_name + ".bam")
process = subprocess.check_call(
    ["python", "/home/bioinf/programs/miniconda3/pkgs/mosdepth-0.2.5-hb763d49_0/plot-dist.py",
     path + "/" + sample_name + ".mosdepth.global.dist.txt"])
print(str(datetime.now() - startTime) + " for mosdepth")

# for insert size
process = subprocess.check_call(
        ["java", "-jar", "/home/bioinf/programs/Picard/picard.jar", "CollectInsertSizeMetrics",
         "I=" + path + "/marked_" + sample_name + ".bam",
         "O=" + path + "/insert_size_metrics.txt", "H=" + path + "/insert_size_histogram.pdf",
         "STOP_AFTER=10000000", "M=0.5"])
print(str(datetime.now() - startTime) + " for insert size")
if do_until == "coverage":
    sys.exit("coverage done")
if do_until == "analysis":
    sys.exit("analysis done here at insert size")

# for vcf
process = subprocess.check_call(["/home/bioinf/programs/bcftools/bcftools-1.9/./bcftools", "mpileup",
                                 path + "/marked_" + sample_name + ".bam", "-o", path + "/" + sample_name + ".vcf",
                                 "-Ov", "-f",
                                 "/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome.fa"])
print(str(datetime.now() - startTime) + " for vcf")

# filter vcf from empty strings and stars
process = subprocess.check_call(["python3.5", "/home/bioinf/pipeline/vcf_filter.py",
                                 path + "/" + sample_name + ".vcf",
                                 path + "/filtered_" + sample_name + ".vcf"])
process = subprocess.check_call(["/home/bioinf/programs/bcftools/bcftools-1.9/./bcftools",
                                 "call", "-c", "--variants-only",
                                 "-Ov", "-o",
                                 path + "/" + sample_name + "_no_stars.vcf",
                                 path + "/filtered_" + sample_name + ".vcf"])
print(str(datetime.now() - startTime) + " filter vcf from empty strings")
if do_until == "vcf" or do_until == "vcf_only":
    sys.exit("vcf done")

# for annotation
process = subprocess.check_call(["/home/bioinf/programs/ensembl-vep/vep",
                                 "-i", path + "/" + sample_name + "_no_stars.vcf",
                                 "-o", path + "/ann_" + sample_name + ".vcf",
                                 "--port", "3337", "--cache",
                                 "--dir_cache", "/home/anyapavlova/.vep/",
                                 "--force_overwrite"])
print(str(datetime.now() - startTime) + " for annotation")
if do_until == "ann":
    sys.exit("ann done")

# for pathogenenicity level
process = subprocess.check_call(["python3.5", "/home/bioinf/programs/intervar/InterVar/Intervar.py",
                                 "-b", "hg19",
                                 "-i", path + "/" + sample_name + "_no_stars.vcf", "--input_type=VCF",
                                 "-o", path + "/" + sample_name + "_InterVar",
                                 "--table_annovar=/home/bioinf/programs/annovar/table_annovar.pl",
                                 "--convert2annovar=/home/bioinf/programs/annovar/convert2annovar.pl",
                                 "--annotate_variation=/home/bioinf/programs/annovar/annotate_variation.pl",
                                 "--database_intervar=/home/bioinf/programs/intervar/InterVar/intervardb",
                                 "--database_locat=/home/bioinf/programs/intervar/InterVar/humandb"])
print(str(datetime.now() - startTime) + " for pathogenenicity level")

# for snpEff
os.system(
    "java -Xmx8g -jar /home/bioinf/programs/snpEff/snpEff/snpEff.jar -c /home/bioinf/programs/snpEff/snpEff/snpEff.config -v hg19 " + path + "/" + sample_name + "_no_stars.vcf > " + path + "/filtered_" + sample_name + ".ann.vcf")
print(str(datetime.now() - startTime) + " for snpEff")

# os.remove(path+"/trimmed"+file1)
# os.remove(path+"/trimmed"+file2)
# os.remove(path+"/"+sample_name+".sam")
# os.remove(path+"/"+sample_name+".bam")
# os.remove(path+"/marked_"+sample_name+".bam")
# os.remove(path+"/filtered_"+sample_name+".vcf")
# os.remove(path+"/"+sample_name+"_no_stars.vcf")
# os.remove(path+"/ann_"+sample_name+".vcf")