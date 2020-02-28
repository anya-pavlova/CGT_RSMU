import sys
import glob
import os

sample_name = sys.argv[1]
chr_name = sys.argv[2]

os.system("sudo bash -c \"/home/bioinf/programs/samtools/samtools-1.9/samtools view -h marked_"+sample_name+".bam chr"+chr_name+" > "+sample_name+"_chr"+chr_name+"_raw.bam\"")
os.system("sudo bash -c \"/home/bioinf/programs/samtools/samtools-1.9/samtools view -h "+sample_name+"_chr"+chr_name+"_raw.bam > "+sample_name+"_chr"+chr_name+".sam\"")
os.system("sudo bash -c \"/home/bioinf/programs/samtools/samtools-1.9/samtools view -bSh "+sample_name+"_chr"+chr_name+".sam > "+sample_name+"_chr"+chr_name+".bam\"")
os.system("sudo bash -c \"/home/bioinf/programs/samtools/samtools-1.9/samtools index "+sample_name+"_chr"+chr_name+".bam\"")

