#!/usr/bin/env python3
from sys import argv
from sources import remove_unused_functions_from_lines as clean_lines
from sources import remove_print_compiling_info


if __name__ == "__main__":
    _input = argv[1]
    output = argv[2]
    unused_function_file = argv[3]

    unused_filenames_functions = open(unused_function_file).read().strip().split()

    unused_functions = [
        line.split(':')[1]
        for line in unused_filenames_functions
        if line.split(':')[0] == _input ]

    n_unused = len(unused_functions)
    if n_unused == 0:
        print(f"File {_input} has NO unused functions.")
    else:
        print(f"File {_input} has {n_unused} unused functions.")

    if 'main' in unused_functions:
        unused_functions.remove('main')

    with open(_input ,'r') as f:
        lines = f.readlines()

    lines = clean_lines(unused_functions,lines)
    lines = remove_print_compiling_info(lines)

    with open(output,'w') as out:
        out.write(''.join(lines))
