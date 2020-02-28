import subprocess
import sys
import glob
import os
from datetime import datetime

path = sys.argv[1]
if sys.argv[1][-1:] == "/":
    path = sys.argv[1][:-1]
sample_name = path.split("/")[-1]

do_until = sys.argv[2]
do_until_list = ["trimming","fastqc","sam","second_fastqc","bam","coverage","vcf","vcf_only","ann","analysis","full"]
if do_until not in do_until_list:
    sys.exit("E: instead of \""+sys.argv[2]+"\" you can chouse: trimming, fastqc, sam, second_fastqc, bam, coverage, vcf, vcf_only, ann, analysis or full")


startTime = datetime.now()
print(str(datetime.now()-startTime)+" starting")
os.chdir(path)


# for cleaning from duplicates
process=subprocess.call(["java", "-jar", "/home/bioinf/programs/Picard/picard.jar",
                         "MarkDuplicates", "I="+path+"/"+"sorted_"+sample_name+".bam",
                         "O="+path+"/marked_"+sample_name+".bam", "M="+path+"/marked_dup_metrics.txt",
                         "REMOVE_DUPLICATES=true"])
print(str(datetime.now()-startTime)+" for cleaning from duplicates")

if do_until != "analysis":
    os.remove(path+"/sorted_"+sample_name+".bam")


# maybe indexing
os.chdir(path)
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools",
                         "index",
                         "marked_"+sample_name+".bam"])
print(str(datetime.now()-startTime)+" for indexing")


# for NGSrich (may be some problems with path)
os.chdir("/home/bioinf/programs/ngsrich/NGSrich_0.7.8/bin")
process=subprocess.call(["java","NGSrich","evaluate",
                         "-r", path+"/marked_"+sample_name+".bam",
                         "-u", "hg19",
                         "-t", "/home/bioinf/data/target/S31285117_Covered.bed",
                         "-o", path+"/NGSrich"])
os.chdir(path)
print(str(datetime.now()-startTime)+" for NGSrich")

# v6 bed /home/bioinf/dont_change/Exome-Agilent_V6.bed

# for mosdepth
os.system("/home/bioinf/programs/miniconda3/bin/mosdepth --by /home/bioinf/data/target/S31285117_Covered.bed "+sample_name+" "+path+"/marked_"+sample_name+".bam")
process=subprocess.call(["python", "/home/bioinf/programs/miniconda3/pkgs/mosdepth-0.2.5-hb763d49_0/plot-dist.py", path +"/"+sample_name+".mosdepth.global.dist.txt"])
print(str(datetime.now()-startTime)+" for mosdepth")
if do_until == "coverage":
    sys.exit("coverage done")


# for vcf
process=subprocess.call(["/home/bioinf/programs/bcftools/bcftools-1.9/./bcftools", "mpileup",
                         path+"/marked_"+sample_name+".bam", "-o", path+"/"+sample_name+".vcf",
                         "-Ov", "-f",
                         "/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome.fa"])
print(str(datetime.now()-startTime)+" for vcf")


# filter vcf from empty strings and stars
process=subprocess.call(["python3.5", "/home/bioinf/pipeline/vcf_filter.py",
                         path+"/"+sample_name+".vcf",
                         path+"/filtered_"+sample_name+".vcf"])
process=subprocess.call(["/home/bioinf/programs/bcftools/bcftools-1.9/./bcftools",
                         "call", "-c", "--variants-only",
                         "-Ov", "-o",
                         path+"/"+sample_name+"_no_stars.vcf",
                         path+"/filtered_"+sample_name+".vcf"])
print(str(datetime.now()-startTime)+" filter vcf from empty strings")
if do_until == "vcf" or do_until == "vcf_only":
    sys.exit("vcf done")


# for annotation
process=subprocess.call(["/home/bioinf/programs/ensembl-vep/vep",
                         "-i", path+"/"+sample_name+"_no_stars.vcf",
                         "-o", path+"/ann_"+sample_name+".vcf",
                         "--port", "3337", "--cache",
                         "--dir_cache", "/home/anyapavlova/.vep/",
                         "--force_overwrite"])
print(str(datetime.now()-startTime)+" for annotation")
if do_until == "ann":
    sys.exit("ann done")


# for pathogenenicity level
process=subprocess.call(["python3.5", "/home/bioinf/programs/intervar/InterVar/Intervar.py",
                         "-b", "hg19",
                         "-i", path+"/"+sample_name+"_no_stars.vcf", "--input_type=VCF",
                         "-o", path+"/"+sample_name+"_InterVar",
                         "--table_annovar=/home/bioinf/programs/annovar/table_annovar.pl",
                         "--convert2annovar=/home/bioinf/programs/annovar/convert2annovar.pl",
                         "--annotate_variation=/home/bioinf/programs/annovar/annotate_variation.pl",
                         "--database_intervar=/home/bioinf/programs/intervar/InterVar/intervardb",
                         "--database_locat=/home/bioinf/programs/intervar/InterVar/humandb"])
print(str(datetime.now()-startTime)+" for pathogenenicity level")


# for snpEff
os.system("java -Xmx8g -jar /home/bioinf/programs/snpEff/snpEff/snpEff.jar -c /home/bioinf/programs/snpEff/snpEff/snpEff.config -v hg19 "+path+"/"+sample_name+"_no_stars.vcf > "+path+"/filtered_"+sample_name+".ann.vcf")
print(str(datetime.now()-startTime)+" for snpEff")


#os.remove(path+"/trimmed"+file1)
#os.remove(path+"/trimmed"+file2)
#os.remove(path+"/"+sample_name+".sam")
#os.remove(path+"/"+sample_name+".bam")
#os.remove(path+"/marked_"+sample_name+".bam")
#os.remove(path+"/filtered_"+sample_name+".vcf")
#os.remove(path+"/"+sample_name+"_no_stars.vcf")
#os.remove(path+"/ann_"+sample_name+".vcf")



