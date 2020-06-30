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

where_to_start = sys.argv[2]
where_to_start_list = ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                       "bam_index", "coverage", "vcf", "ann"]
if where_to_start not in where_to_start_list:
    sys.exit("E: instead of \"" + sys.argv[3] +
             "\" you can choose: fq, fastq_sort, fastqc, trimming, sam, second_fastqc, bam, coverage, vcf or " +
             "ann")

do_until = sys.argv[3]
do_until_list = ["trimming", "fastqc", "sam", "second_fastqc", "bam", "marked_bam", "coverage", "vcf", "vcf_only",
                 "ann", "analysis",
                 "full"]
if do_until not in do_until_list:
    sys.exit("E: instead of \"" + sys.argv[
        2] + "\" you can choose: trimming, fastqc, sam, second_fastqc, bam, marked_bam, coverage, vcf, vcf_only, ann, analysis or full")

if where_to_start in ["fq", "fastq_sort"]:
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

if where_to_start in ["fq", "fastq_sort"]:
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
                    "/data/programs/fastq-tools/fastq-tools/src/fastq-sort",
                    "--id", os.path.join(path, file_without_gz_extension)
                ],
                stdout=out
            )

        sorted_files.append(output_file)
        print(str(datetime.now() - startTime) + " for sort fq")

# for trimming!!!!!!!!!!!!!!!!!!make_CROP_system!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! and change places with fastqc
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming"]:
    process = subprocess.check_call(["java", "-jar",
                                     "/data/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                                     "SE", "-threads", "2", path + "/" + sorted_files[0], path + "/trimmed" + file1,
                                     "HEADCROP:3"])
    if input_file_types == "PE fq":
        process = subprocess.check_call(["java", "-jar",
                                         "/data/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
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
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam"]:
    os.system("bwa mem " +
              "/data/ref_and_beds/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/BWAIndex/version0.7.12/genome.fa " +
              path + "/trimmed" + file1 + " " + path + "/trimmed" + file2 + " -t 2 > " + path + "/" + sample_name + ".sam")
    if do_until == "sam":
        sys.exit("sam done")

    if do_until != "analysis":
        os.remove(path + "/trimmed" + file1)
        if input_file_types == "PE fq":
            os.remove(path + "/trimmed" + file2)
    print(str(datetime.now() - startTime) + " for mapping")

# for converting sam to bam
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam"]:
    process = subprocess.check_call(["/data/programs/samtools/samtools-1.9/samtools",
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
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort"]:
    process = subprocess.check_call(["/data/programs/samtools/samtools-1.9/samtools", "sort", "-o",
                                     path + "/sorted_" + sample_name + ".bam", path + "/" + sample_name + ".bam"])
    print(str(datetime.now() - startTime) + " for sorting bams")

    if do_until != "analysis":
        os.remove(path + "/" + sample_name + ".bam")

# for cleaning from duplicates
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort",
                      "bam_dup"]:
    process = subprocess.check_call(["java", "-jar", "/data/programs/picard/picard.jar",
                                     "MarkDuplicates", "I=" + path + "/" + "sorted_" + sample_name + ".bam",
                                     "O=" + path + "/marked_" + sample_name + ".bam",
                                     "M=" + path + "/marked_dup_metrics.txt",
                                     "REMOVE_DUPLICATES=true"])
    print(str(datetime.now() - startTime) + " for cleaning from duplicates")
    if do_until != "analysis":
        os.remove(path + "/sorted_" + sample_name + ".bam")

# maybe indexing
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index"]:
    os.chdir(path)
    process = subprocess.check_call(["/data/programs/samtools/samtools-1.9/samtools",
                                     "index",
                                     "marked_" + sample_name + ".bam"])
    print(str(datetime.now() - startTime) + " for indexing")
    if do_until == "marked_bam":
        sys.exit("marked_bam done")

# for NGSrich (may be some problems with path)
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort",
                      "bam_dup",
                      "bam_index", "coverage"]:
    os.chdir("/data/programs/NGSrich/NGSrich_0.7.8/bin")
    process = subprocess.check_call(["java", "NGSrich", "evaluate",
                                     "-r", path + "/marked_" + sample_name + ".bam",
                                     "-u", "hg19",
                                     "-t", "/data/ref_and_beds/dont_change/target/S31285117_Covered.bed",
                                     "-o", path + "/NGSrich"])
    os.chdir(path)

    print(str(datetime.now() - startTime) + " for NGSrich")

# v6 bed /data/ref_and_beds/dont_change/Exome-Agilent_V6.bed
# v7 bed /data/ref_and_beds/dont_change/target/S31285117_Covered.bed

# for mosdepth
"""os.system(
    "/home/bioinf/programs/miniconda3/bin/mosdepth --by /home/bioinf/data/target/S31285117_Covered.bed " + sample_name + " " + path + "/marked_" + sample_name + ".bam")
process = subprocess.check_call(
    ["python", "/home/bioinf/programs/miniconda3/pkgs/mosdepth-0.2.5-hb763d49_0/plot-dist.py",
     path + "/" + sample_name + ".mosdepth.global.dist.txt"])
print(str(datetime.now() - startTime) + " for mosdepth")"""

# for insert size
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort",
                      "bam_dup",
                      "bam_index", "coverage"]:
    process = subprocess.check_call(
        ["java", "-jar", "/data/programs/picard/picard.jar", "CollectInsertSizeMetrics",
         "I=" + path + "/marked_" + sample_name + ".bam",
         "O=" + path + "/insert_size_metrics.txt", "H=" + path + "/insert_size_histogram.pdf",
         "STOP_AFTER=10000000", "M=0.5"])
    print(str(datetime.now() - startTime) + " for insert size")
    if do_until == "coverage":
        sys.exit("coverage done")
    if do_until == "analysis":
        sys.exit("analysis done here at insert size")

# for vcf
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "coverage", "vcf"]:
    process = subprocess.check_call(["/data/programs/bcfrools/bcftools-1.9/./bcftools", "mpileup",
                                     path + "/marked_" + sample_name + ".bam", "-o", path + "/" + sample_name + ".vcf",
                                     "-Ov", "-f",
                                     "/data/ref_and_beds/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome.fa"])
    print(str(datetime.now() - startTime) + " for vcf")

# filter vcf from empty strings and stars
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "coverage", "vcf"]:
    process = subprocess.check_call(["python3", "/data/CGT_RSMU/pipeline/vcf_filter.py",
                                     path + "/" + sample_name + ".vcf",
                                     path + "/filtered_" + sample_name + ".vcf"])
    process = subprocess.check_call(["/data/programs/bcfrools/bcftools-1.9/./bcftools",
                                     "call", "-c", "--variants-only",
                                     "-Ov", "-o",
                                     path + "/" + sample_name + "_no_stars.vcf",
                                     path + "/filtered_" + sample_name + ".vcf"])
    print(str(datetime.now() - startTime) + " filter vcf from empty strings")
    if do_until == "vcf" or do_until == "vcf_only":
        sys.exit("vcf done")

# for annotation
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "coverage", "vcf", "ann"]:
    process = subprocess.check_call(["/data/programs/vep/ensembl-vep/vep",
                                     "-i", path + "/" + sample_name + "_no_stars.vcf",
                                     "-o", path + "/ann_" + sample_name + ".vcf",
                                     "--port", "3337", "--cache",
                                     "--dir_cache", "/home/pavlova/.vep/",
                                     "--force_overwrite"])
    print(str(datetime.now() - startTime) + " for annotation")
    if do_until == "ann":
        sys.exit("ann done")

# for pathogenenicity level
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "coverage", "vcf", "ann"]:
    process = subprocess.check_call(["python3", "/home/bioinf/programs/intervar/InterVar/Intervar.py",
                                     "-b", "hg19",
                                     "-i", path + "/" + sample_name + "_no_stars.vcf", "--input_type=VCF",
                                     "-o", path + "/" + sample_name + "_InterVar",
                                     "--table_annovar=/data/programs/annovar/annovar/table_annovar.pl",
                                     "--convert2annovar=/data/programs/annovar/annovar/convert2annovar.pl",
                                     "--annotate_variation=/data/programs/annovar/annovar/annotate_variation.pl",
                                     "--database_intervar=/data/programs/intervar/InterVar/intervardb",
                                     "--database_locat=/data/programs/intervar/InterVar/humandb"])
    print(str(datetime.now() - startTime) + " for pathogenenicity level")

# for snpEff
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "coverage", "vcf", "ann"]:
    os.system(
        "java -Xmx8g -jar /data/programs/SnpEff/snpEff/snpEff.jar -c /data/programs/SnpEff/snpEff/snpEff.config -v hg19 " + path + "/" + sample_name + "_no_stars.vcf > " + path + "/filtered_" + sample_name + ".ann.vcf")
    print(str(datetime.now() - startTime) + " for snpEff")

# os.remove(path+"/trimmed"+file1)
# os.remove(path+"/trimmed"+file2)
# os.remove(path+"/"+sample_name+".sam")
# os.remove(path+"/"+sample_name+".bam")
# os.remove(path+"/marked_"+sample_name+".bam")
# os.remove(path+"/filtered_"+sample_name+".vcf")
# os.remove(path+"/"+sample_name+"_no_stars.vcf")
# os.remove(path+"/ann_"+sample_name+".vcf")
