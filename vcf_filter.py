import sys
import csv

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as in_file:
        for line in in_file:
            if line.startswith("#"):
                print(line, end='')
            else:
                columns = line.split("\t")
                if columns[4] != '.':
                    print(line, end='')