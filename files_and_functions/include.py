#!/usr/bin/env python3
import os


def get_paths(sombrero_root, pycparser_root):

    sombrero_inc = sombrero_include(sombrero_root)
    fake_libc = os.path.join(pycparser_root, "utils", "fake_libc_include")

    return [fake_libc, sombrero_inc]


def sombrero_include(sombrero_root):
    return os.path.join(sombrero_root, "Include")


def source_files(filename_filter_function, *roots):

    return [
        os.path.join(dirpath, filename)
        for root in roots
        for dirpath, directories, filenames in os.walk(root)
        for filename in filenames
        if filename.endswith(".c")
        and filename_filter_function(os.path.join(dirpath, filename))
    ]
