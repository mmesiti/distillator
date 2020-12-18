#!/usr/bin/env python3

from sys import argv
from sources import remove_unused_functions_from_lines as clean_lines

if __name__ == "__main__":
    _input = argv[1]
    output = argv[2]
    unused_function_file = argv[3]

    unused_functions = open(unused_function_file).read().strip().split()

    unused_functions.remove('main')

    with open(_input ,'r') as f:
        lines = f.readlines()

    lines = clean_lines(unused_functions, lines)

    with open(output,'w') as out:
        out.write(''.join(lines))
