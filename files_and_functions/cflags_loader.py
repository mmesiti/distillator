#!/usr/bin/env python3
from yaml import load, Loader


def read_compiler_dflags_lib(filename="cpp_flags.yaml"):

    with open(filename, "r") as f:
        dflags = load(f, Loader=Loader)
    return dflags


def get_groupreps(filename="cpp_flags.yaml", dflags=None):
    if dflags is None:
        dflags = read_compiler_dflags_lib(filename=filename)

    return [gr for gr in dflags.keys() if not gr.startswith("base")]


def get_cpp_dflags(group_repr, dflags):
    dflags = dflags["baseflags"] + dflags[group_repr]
    return ["-D" + df for df in dflags]
