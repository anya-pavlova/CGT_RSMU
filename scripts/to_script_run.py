import glob
import os
import subprocess
import sys

path = sys.argv[1]

for filename in glob.glob(path + "/*"):
    subprocess.Popen(["sudo", "nohup", "python3.5", "/home/bioinf/scripts/full_pipe_bwa_edition.py",
                      filename, "coverage"])
