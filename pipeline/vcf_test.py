import sys

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as in_file:
        for line in in_file:
            if line.startswith("#"):
                pass
            else:
                if line.split("\t")[4] == ("<*>"):
                    print(line.split("\t")[4])
                    print(line.split("\t"))
