import subprocess
import sys
import glob
import os
from datetime import datetime

sample_name = sys.argv[1]
path = sys.argv[2]
if sys.argv[2][-1:] == "/":
    path = sys.argv[2][:-1]


startTime = datetime.now()
print(str(datetime.now()-startTime)+" starting")


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


"""
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
os.system("java -Xmx8g -jar /home/bioinf/programs/snpEff/snpEff/snpEff.jar -c /home/bioinf/programs/snpEff/snpEff/snpEff.config -v hg19 "+path+"/filtered_"+sample_name+".vcf > "+path+"/filtered_"+sample_name+".ann.vcf")
print(str(datetime.now()-startTime)+" for snpEff")
"""

#os.remove(path+"/trimmed"+file1)
#os.remove(path+"/trimmed"+file2)
#os.remove(path+"/"+sample_name+".sam")
#os.remove(path+"/"+sample_name+".bam")
#os.remove(path+"/marked_"+sample_name+".bam")
#os.remove(path+"/filtered_"+sample_name+".vcf")
#os.remove(path+"/"+sample_name+"_no_stars.vcf")
#os.remove(path+"/ann_"+sample_name+".vcf")



