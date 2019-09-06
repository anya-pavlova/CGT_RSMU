from __future__ import print_function
import sys

filename = sys.argv[1]

if __name__ == "__main__":
    with open(filename, 'r') as f:
        lines = iter(f)
        while True:
            try:
                print(next(lines), end='')
                print(next(lines)[9:], end='')
            except StopIteration:
                break
