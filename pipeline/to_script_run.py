import glob
import os
import subprocess
import sys

path = sys.argv[1]

for filename in glob.glob(path + "/*"):
    subprocess.Popen(["sudo", "nohup", "python3.5", "/home/bioinf/pipeline/full_pipe_bowtie2_edition_V6.py",
                      filename, "coverage", ">", filename+"/nohup.out"])
