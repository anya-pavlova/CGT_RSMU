import sys

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as in_file:
        with open(sys.argv[2], 'a') as out_file:
            for line in in_file:
                if line.startswith("#"):
                    out_file.write(line)
                else:
                    if line.split("\t")[4] != '<*>' and line.split("\t")[4] != '.':
                        out_file.write(line)
    print(line)

