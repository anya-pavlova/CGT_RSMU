import subprocess
import sys
import glob
import smtplib

sample_name = sys.argv[1]
path = sys.argv[2]
file1 = sys.argv[3]
file2 = sys.argv[4]

# for mapping
process=subprocess.call(["bowtie2", "-x",
"/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome", 
"-1", path+"/"+file1, "-2", path+"/"+file2, "-S", path+"/"+sample_name+".sam"])

# for converting sam to bam
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "view", "-bS", 
                         "-o" , path+"/"+sample_name+".bam", path+"/"+sample_name+".sam"])

# maybe
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "index", 
                         path+"/"+sample_name+".bam"])

# for sorting bams
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "sort", "-o",
                         path+"/sorted_"+sample_name+".bam", path+"/"+sample_name+".bam"])

# for cleaning from duplicates
process=subprocess.call(["java", "-jar", "/home/bioinf/programs/Picard/picard.jar", 
                         "MarkDuplicates", "I="+path+"/"+"sorted_"+sample_name+".bam",
                         "O="+path+"/marked_"+sample_name+".bam", "M="+path+"/marked_dup_metrics.txt"])

# for vcf
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "mpileup", "-uf",
"/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome.fa",
path+"/marked_"+sample_name+".bam", "|", "/home/bioinf/programs/bcftools/bcftools-1.9/./bcftools",
"call", "-c", ">", path+"/"+sample_name+".vcf"])

# for annotation
#process=subprocess.call([])

#
#process=subprocess.call([])


