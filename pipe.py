import subprocess
import sys
import glob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sample_name = sys.argv[1]
path = sys.argv[2]
file1 = sys.argv[3]
file2 = sys.argv[4]

def post_there_want(to_adr,text):
    fromaddr = "galyakisaforever@gmail.com"
    mypass = "galya number 1"
    to_adr = "afas1robert@gmail.com"
 
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = to_adr
    msg['Subject'] = "Sample to vcf pipe" # Subject
 
    body = text
    msg.attach(MIMEText(body, 'plain'))
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, mypass)
    text = msg.as_string()
    server.sendmail(fromaddr, to_adr, text)
    server.quit()

# for mapping
process=subprocess.call(["bowtie2", "-x",
"/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome", 
"-1", path+"/"+file1, "-2", path+"/"+file2, "-S", path+"/"+sample_name+".sam"])
post_there_want("afas1robert@gmail.com","for mapping")

# for converting sam to bam
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "view", "-bS", 
                         "-o" , path+"/"+sample_name+".bam", path+"/"+sample_name+".sam"])
post_there_want("afas1robert@gmail.com","for converting sam to bam")

# maybe
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "index", 
                         path+"/"+sample_name+".bam"])
post_there_want("afas1robert@gmail.com","for indexing")

# for sorting bams
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "sort", "-o",
                         path+"/sorted_"+sample_name+".bam", path+"/"+sample_name+".bam"])
post_there_want("afas1robert@gmail.com","for sorting bams")

# for cleaning from duplicates
process=subprocess.call(["java", "-jar", "/home/bioinf/programs/Picard/picard.jar", 
                         "MarkDuplicates", "I="+path+"/"+"sorted_"+sample_name+".bam",
                         "O="+path+"/marked_"+sample_name+".bam", "M="+path+"/marked_dup_metrics.txt"])
post_there_want("afas1robert@gmail.com"," for cleaning from duplicates")

# for vcf
process=subprocess.call(["/home/bioinf/programs/samtools/samtools-1.9/samtools", "mpileup", "-uf",
"/home/bioinf/data/reference_human_hg19/Homo_sapiens/UCSC/hg19/Sequence/Bowtie2Index/genome.fa",
path+"/marked_"+sample_name+".bam", "|", "/home/bioinf/programs/bcftools/bcftools-1.9/./bcftools",
"call", "-c", ">", path+"/"+sample_name+".vcf"])
post_there_want("afas1robert@gmail.com"," for vcf")

start_time = datetime.now()
# for annotation
#process=subprocess.call([])
post_there_want("afas1robert@gmail.com"," for annotation")

#
#process=subprocess.call([])


