from __future__ import print_function
import sys

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        lines = iter(f)
        while True:
            try:
                print(next(lines), end='')
                print(next(lines)[9:], end='')
            except StopIteration:
                break
