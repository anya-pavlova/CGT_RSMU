import sys

with open(sys.argv[1], mode='r') as vcf:
    data = vcf.read()
    data = data.replace(',Version="3"', "")
    new_file_name = 'tapes_' + sys.argv[1]
    file = open(new_file_name, "w")
    file.write(data)
    file.close()
