import subprocess
import sys
import glob
import os
from datetime import datetime
from shutil import unpack_archive, make_archive
import shlex
import tempfile

path = sys.argv[1]
if sys.argv[1][-1:] == "/":
    path = sys.argv[1][:-1]
sample_name = path.split("/")[-1]

where_to_start = sys.argv[2]
where_to_start_list = ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc",
                      "bam", "bam_sort", "bam_dup", "bam_index", "bam_merge", "coverage", "vcf",
                      "vcf_filter", "ann_vep", "ann_inter", "full_ann"]
if where_to_start not in where_to_start_list:
    sys.exit("E: instead of \"" + sys.argv[3] +
             "\" you can call Robert for help")

do_until = sys.argv[3]
do_until_list = ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc",
                      "bam", "bam_sort", "bam_dup", "bam_index", "bam_merge", "coverage", "vcf",
                      "vcf_filter", "ann_vep", "ann_inter", "full_ann", "full"]
if do_until not in do_until_list:
    sys.exit("E: instead of \"" + sys.argv[
        2] + "\" you can call Robert for help")

#  bed will be here

startTime = datetime.now()
print(str(datetime.now() - startTime) + " starting")
os.chdir(path)

for dir_with_fq in glob.glob(path + "/*"):
    if dir_with_fq.split("/")[-1] in ["lane_1", "lane_2", "lane_3", "lane_4"]:
        input_files = []
        for filename in glob.glob(dir_with_fq + "/*"):
            if filename.split("/")[-1] != "nohup.out":
                input_files.append(filename)
        input_files = sorted(input_files)
        print(input_files)
        file1 = input_files[0].split("/")[-1]
        file2 = input_files[1].split("/")[-1]

        input_file_types = "idk"
        if len(input_files) == 2:
            input_file_types = "PE fq"

        # for trimming!!!!!!!!!!!!!!!!!!make_CROP_system!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! and change places with fastqc
        if where_to_start in ["fq", "trimming"]:
            process = subprocess.check_call(["java", "-jar",
                                             "/data/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                                             "SE", "-threads", "1", dir_with_fq + "/" + file1,
                                             dir_with_fq + "/trimmed" + file1,
                                             "HEADCROP:3"])
            if input_file_types == "PE fq":
                process = subprocess.check_call(["java", "-jar",
                                                 "/data/programs/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar",
                                                 "SE", "-threads", "1", dir_with_fq + "/" + file2,
                                                 dir_with_fq + "/trimmed" + file2,
                                                 "HEADCROP:3"])
            print(str(datetime.now() - startTime) + " for trimming")
            if do_until == "trimming":
                sys.exit("trimming done")

        # for quality test
        """
        if where_to_start in ["fq", "trimming", "fastqc"]:
            process = subprocess.check_call(["/home/anyapavlova/downloads/FastQC/fastqc", "-t", "2", "-o",
                                             dir_with_fq, dir_with_fq + "/trimmed" + file1])
            if input_file_types == "PE fq":
                process = subprocess.check_call(["/home/anyapavlova/downloads/FastQC/fastqc", "-t", "2", "-o",
                                                 dir_with_fq, dir_with_fq + "/trimmed" + file2])
            print(str(datetime.now() - startTime) + " for quality test")
            if do_until == "fastqc":
                sys.exit("fastqc done")
        """

        # for mapping
        if where_to_start in ["fq", "trimming", "fastqc", "sam"]:
            os.system("bwa mem " +
                      "/data/ref_and_beds/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/BWAIndex/version0.7.12/genome.fa " +
                      dir_with_fq + "/trimmed" + file1 + " " + dir_with_fq + "/trimmed" + file2 + " -t 1 > " + dir_with_fq + "/" + sample_name + ".sam")
            if do_until == "sam":
                sys.exit("sam done")

            if do_until != "analysis":
                os.remove(dir_with_fq + "/trimmed" + file1)
                if input_file_types == "PE fq":
                    os.remove(dir_with_fq + "/trimmed" + file2)
            print(str(datetime.now() - startTime) + " for mapping")

        # for converting sam to bam
        if where_to_start in ["fq", "trimming", "fastqc", "sam", "second_fastqc", "bam"]:
            process = subprocess.check_call(["/data/programs/samtools/samtools-1.9/samtools",
                                             "view", "-bS",
                                             "-o", dir_with_fq + "/" + sample_name + ".bam",
                                             dir_with_fq + "/" + sample_name + ".sam"])
            print(str(datetime.now() - startTime) + " for converting sam to bam")
            if do_until == "bam":
                sys.exit("bam done")

            if do_until != "analysis":
                os.remove(dir_with_fq + "/" + sample_name + ".sam")

        # here second fastqc
        """
        if where_to_start in ["fq", "trimming", "fastqc", "sam", "second_fastqc"]:
            if do_until != "vcf_only":
                if not os.path.isdir(dir_with_fq + "/second"):
                    os.makedirs(dir_with_fq + "/second")
                process = subprocess.check_call(["/home/anyapavlova/downloads/FastQC/fastqc", "-o",
                                                 dir_with_fq + "/second", dir_with_fq + "/" + sample_name + ".sam"])
                print(str(datetime.now() - startTime) + " for second fastqc")
                if do_until == "second_fastqc":
                    sys.exit("second_fastqc done")"""

        # for sorting bams
        if where_to_start in ["fq", "trimming", "fastqc", "sam", "second_fastqc", "bam", "bam_sort"]:
            process = subprocess.check_call(["/data/programs/samtools/samtools-1.9/samtools", "sort", "-o",
                                             dir_with_fq + "/sorted_" + sample_name + ".bam",
                                             dir_with_fq + "/" + sample_name + ".bam"])
            print(str(datetime.now() - startTime) + " for sorting bams")

            if do_until != "analysis":
                os.remove(dir_with_fq + "/" + sample_name + ".bam")
            if do_until == "bam_sort":
                sys.exit("bam_sort done")

        # for cleaning from duplicates
        if where_to_start in ["fq", "trimming", "fastqc", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup"]:
            process = subprocess.check_call(["java", "-jar", "/data/programs/picard/picard.jar",
                                             "MarkDuplicates",
                                             "I=" + dir_with_fq + "/" + "sorted_" + sample_name + ".bam",
                                             "O=" + dir_with_fq + "/marked_" + sample_name + ".bam",
                                             "M=" + dir_with_fq + "/marked_dup_metrics.txt",
                                             "REMOVE_DUPLICATES=true"])
            print(str(datetime.now() - startTime) + " for cleaning from duplicates")
            if do_until != "analysis":
                os.remove(dir_with_fq + "/sorted_" + sample_name + ".bam")
            if do_until == "bam_dup":
                sys.exit("bam_dup done")

        # maybe indexing                       is it really necessary
        if where_to_start in ["fq", "trimming", "fastqc", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                              "bam_index"]:
            os.chdir(dir_with_fq)
            process = subprocess.check_call(["/data/programs/samtools/samtools-1.9/samtools",
                                             "index",
                                             "marked_" + sample_name + ".bam"])
            print(str(datetime.now() - startTime) + " for indexing")
            if do_until == "bam_index":
                sys.exit("bam_index done")

# for merging bam files
if where_to_start in ["fq", "trimming", "fastqc", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup", "bam_merge"]:
    bam_files = []
    for dir_with_fq in glob.glob(path + "/*"):
        if dir_with_fq.split("/")[-1] in ["lane_1", "lane_2", "lane_3", "lane_4"]:
            bam_files.append(dir_with_fq + "/marked_" + sample_name + ".bam")
    os.system("/data/programs/samtools/samtools-1.9/samtools merge " +
              path + "/marked_" + sample_name + ".bam " + " ".join(bam_files))
    print(str(datetime.now() - startTime) + " for merging bam")

    if do_until == "bam_merge":
        sys.exit("bam_merge done")

# for NGSrich (may be some problems with path)
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort",
                      "bam_dup", "bam_index", "bam_merge", "coverage"]:
    os.chdir("/data/programs/NGSrich/NGSrich_0.7.8/bin")
    process = subprocess.check_call(["java", "NGSrich", "evaluate",
                                     "-r", path + "/marked_" + sample_name + ".bam",
                                     "-u", "hg19",
                                     "-t", "/data/ref_and_beds/dont_change/target/S31285117_Covered.bed",
                                     "-o", path + "/NGSrich"])
    os.chdir(path)
    print(str(datetime.now() - startTime) + " for NGSrich")

    os.system("rm -r " + path + "/NGSrich/chromosomes")
    os.system("rm -r " + path + "/NGSrich/data")
    os.system("rm -r " + path + "/NGSrich/plots")

    print(str(datetime.now() - startTime) + " for NGSrich deleting")

# v6 bed /home/bioinf/dont_change/Exome-Agilent_V6.bed
# v7 bed /home/bioinf/data/target/S31285117_Covered.bed

# for mosdepth
"""os.system(
    "/home/bioinf/programs/miniconda3/bin/mosdepth --by /home/bioinf/data/target/S31285117_Covered.bed " + sample_name + " " + path + "/marked_" + sample_name + ".bam")
process = subprocess.check_call(
    ["python", "/home/bioinf/programs/miniconda3/pkgs/mosdepth-0.2.5-hb763d49_0/plot-dist.py",
     path + "/" + sample_name + ".mosdepth.global.dist.txt"])
print(str(datetime.now() - startTime) + " for mosdepth")"""

# for insert size
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort",
                      "bam_dup", "bam_index", "bam_merge", "coverage"]:
    process = subprocess.check_call(
        ["java", "-jar", "/data/programs/picard/picard.jar", "CollectInsertSizeMetrics",
         "I=" + path + "/marked_" + sample_name + ".bam",
         "O=" + path + "/insert_size_metrics.txt", "H=" + path + "/insert_size_histogram.pdf",
         "STOP_AFTER=10000000", "M=0.5"])
    print(str(datetime.now() - startTime) + " for insert size")
    if do_until == "coverage":
        sys.exit("coverage done")
    if do_until == "analysis":
        sys.exit("analysis done here at insert size (change pipe if u want go further)")

# for vcf
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "bam_merge", "coverage", "vcf"]:
    process = subprocess.check_call(
        ["/data/programs/bcfrools/bcftools-1.9/./bcftools", "mpileup",
         path + "/marked_" + sample_name + ".bam", "-o", path + "/" + sample_name + ".vcf",
         "-Ov", "-f",
         "/data/ref_and_beds/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome.fa"])
    print(str(datetime.now() - startTime) + " for vcf")
    if do_until == "vcf":
        sys.exit("vcf done")

# filter vcf from empty strings and stars
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "bam_merge", "coverage", "vcf", "vcf_filter"]:
    process = subprocess.check_call(["python3", "/data/CGT_RSMU/pipeline/vcf_filter.py",
                                     path + "/" + sample_name + ".vcf",
                                     path + "/filtered_" + sample_name + ".vcf"])
    process = subprocess.check_call(["/data/programs/bcfrools/bcftools-1.9/./bcftools",
                                     "call", "-c", "--variants-only",
                                     "-Ov", "-o",
                                     path + "/" + sample_name + "_no_stars.vcf",
                                     path + "/filtered_" + sample_name + ".vcf"])
    print(str(datetime.now() - startTime) + " filter vcf from empty strings")
    if do_until == "vcf_filter" or do_until == "vcf_only":
        sys.exit("filtered vcf done")

# for annotation
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "bam_merge", "coverage", "vcf", "vcf_filter", "ann_vep"]:

    args = [
        "/data/programs/ensembl-vep/vep",
        "-i", path + "/" + sample_name + "_no_stars.vcf",
        "-o", path + "/ann_" + sample_name + ".vcf",
        "--port", "3337", "--cache",
        "--dir_cache", "/home/pavlova/.vep",
        "--force_overwrite"
    ]

    env = os.environ.copy()
    env["PATH"] = "/usr/bin:{}".format(env["PATH"])
    process = subprocess.check_call(args, env=env)

    print(str(datetime.now() - startTime) + " for annotation")
    if do_until == "ann_vep":
        sys.exit("ann_vep done")

# for pathogenenicity level
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "bam_merge", "coverage", "vcf", "vcf_filter", "ann_vep", "ann_inter"]:
    process = subprocess.check_call(["python3", "/data/programs/intervar/InterVar/Intervar.py",
                                     "-b", "hg19",
                                     "-i", path + "/" + sample_name + "_no_stars.vcf", "--input_type=VCF",
                                     "-o", path + "/" + sample_name + "_InterVar",
                                     "--table_annovar=/data/programs/annovar/annovar/table_annovar.pl",
                                     "--convert2annovar=/data/programs/annovar/annovar/convert2annovar.pl",
                                     "--annotate_variation=/data/programs/annovar/annovar/annotate_variation.pl",
                                     "--database_intervar=/data/programs/intervar/InterVar/intervardb",
                                     "--database_locat=/data/programs/intervar/InterVar/humandb"])
    print(str(datetime.now() - startTime) + " for pathogenenicity level")
    if do_until == "ann_inter":
        sys.exit("ann_inter done")

# for full ann
if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc",
                      "bam", "bam_sort", "bam_dup", "bam_index", "bam_merge", "coverage", "vcf",
                      "vcf_filter", "ann_vep", "ann_inter", "full_ann"]:
    os.chdir(path)
    process = subprocess.check_call(["python3", "/data/CGT_RSMU/scripts/delite_version_in_vcf.py",
                                     sample_name + "_no_stars.vcf"])

    process = subprocess.check_call(["python3", "/data/programs/tapes/tapes/tapes.py",
                                     "annotate",
                                     "-i", path + "/" + 'tapes_' + sample_name + "_no_stars.vcf",
                                     "-o", path + "/" + sample_name + '_tapes' + ".vcf", '--acmg'])

    os.chdir(path)
    process = subprocess.check_call(["python3", "/data/CGT_RSMU/scripts/join_tapes_intervar_all_read_depth.py",
                                     sample_name + '_tapes.hg19_multianno.vcf',
                                     sample_name + '_InterVar.hg19_multianno.txt',
                                     sample_name + "_no_stars.vcf",
                                     'ANNOT_' + sample_name + '.xlsx'])

    #  add panel filter here

    print(str(datetime.now() - startTime) + " for full_ann level")
    if do_until == "full_ann":
        sys.exit("full_ann done")

#
#
#
#
# for snpEff
"""if where_to_start in ["fq", "fastq_sort", "fastqc", "trimming", "sam", "second_fastqc", "bam", "bam_sort", "bam_dup",
                      "bam_index", "bam_merge", "coverage", "vcf", "vcf_filter", "ann_vep", "ann_inter", "ann_snpeff"]:
    os.system(
        "java -Xmx8g -jar /data/programs/SnpEff/snpEff/snpEff.jar -c /data/programs/SnpEff/snpEff/snpEff.config -v hg19 " + path + "/" + sample_name + "_no_stars.vcf > " + path + "/filtered_" + sample_name + ".ann.vcf")
    print(str(datetime.now() - startTime) + " for snpEff")
    if do_until == "ann_snpeff":
        sys.exit("ann_snpeff done")"""
