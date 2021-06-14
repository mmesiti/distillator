#!/usr/bin/env python3
import callgraph as cg
from sys import argv
import cflags_loader as cfl
import headers
from include import sombrero_include


def is_filename_relevant(filename):
    res = ("sombrero/sombrero.c" in filename
            or "sombrero/hmc_utils.c" in filename
            or ("LibHR" in filename and "remez" not in filename
                and "Observable" not in filename and "mon" not in filename
                and "flt" not in filename and "integrator" not in filename
                and "force" not in filename and "update.c" not in filename
                ))
    return res


def get_functions(grouprep, sombrero_root, pycparser_root, cpp_flags_file):

    call_graph, file_function_dict = cg.get_callgraph(grouprep, sombrero_root,
                                                      pycparser_root,
                                                      is_filename_relevant,
                                                      cpp_flags_file)

    all_defined = cg.get_all_defined_functions(call_graph)
    used, undefined = cg.get_all_used_functions(call_graph)

    unused = all_defined.difference(used)
    return (
        dict(used_functions=used,
             unused_functions=unused,
             undefined_functions=undefined),
        file_function_dict,
    )


def write_function_lists(file_prefix, used_functions, unused_functions,
                         undefined_functions, **kwargs):
    for fbasename, flist in [
        ("used_functions.txt", used_functions),
        ("unused_functions.txt", unused_functions),
        ("undefined_functions.txt", undefined_functions),
    ]:

        fname = f"{file_prefix}_{fbasename}"
        print(f"Writing {fname}...")
        with open(fname, "w") as f:
            for fun in flist:
                f.write(f"{fun}\n")


def _write_name_list(name_list, fname):
    print(f"Writing {fname}...")
    with open(fname, "w") as f:
        for name in name_list:
            f.write(f"{name}\n")


def write_used_file_list(prefix, file_list):
    fname = f"{prefix}_used_sources.txt"
    _write_name_list(file_list, fname)


def write_used_header_list(header_list):
    fname = "used_headers.txt"
    _write_name_list(header_list, fname)


def write_function_lists_for_all_groupreps(groupreps, function_sets_gr):
    for grouprep in groupreps:
        fsets = dict((k + "_functions", s)
                     for (k, gr), s in function_sets_gr.items()
                     if gr == grouprep)
        write_function_lists(grouprep, **fsets)


def get_function_sets_gr(groupreps, sombrero_root, pycparser_root,
                         cpp_flags_file):
    used_files_sets = []
    function_sets_gr = dict()
    all_file_used_function_dict = dict()
    for grouprep in groupreps:
        print(f"Processing {grouprep} case")

        function_sets, file_function_dict = get_functions(
            grouprep, sombrero_root, pycparser_root, cpp_flags_file)
        function_sets_gr[("used", grouprep)] = function_sets["used_functions"]

        for f in function_sets["used_functions"]:
            if f not in function_sets["undefined_functions"]:
                all_file_used_function_dict[(grouprep,
                                             f)] = file_function_dict[f]

        function_sets_gr[("all",
                          grouprep)] = set.union(*function_sets.values())

        function_sets_gr[("undefined",
                          grouprep)] = function_sets["undefined_functions"]

        function_sets_gr[("unused",
                          grouprep)] = function_sets["unused_functions"]

        used_files = set(file_function_dict[f]
                         for f in function_sets["used_functions"]
                         if f not in function_sets["undefined_functions"])
        used_files_sets.append(used_files)

    return used_files_sets, function_sets_gr, all_file_used_function_dict


def write_gr_function_file_dict(gr_function_file_dict, tag):
    fname = f"{tag}_gr_function_file_table.txt"
    with open(fname, 'w') as outfile:
        for (gr, fun), filename in gr_function_file_dict.items():
            outfile.write(f"{gr} {fun} {filename}\n")


if __name__ == "__main__":
    cpp_flags_file = argv[1]
    sombrero_root = argv[2]
    pycparser_root = argv[3]

    groupreps = cfl.get_groupreps(cpp_flags_file)

    (used_files_sets, function_sets_gr,
     all_file_used_function_dict) = get_function_sets_gr(
         groupreps, sombrero_root, pycparser_root, cpp_flags_file)

    write_gr_function_file_dict(all_file_used_function_dict, "all")

    write_function_lists_for_all_groupreps(groupreps, function_sets_gr)

    def select_and_collapse_gr(function_sets_gr, tag):
        return set.union(
            *[s for (t, gr), s in function_sets_gr.items() if t == tag])

    used_functions_set = select_and_collapse_gr(function_sets_gr, "used")
    all_functions_set = select_and_collapse_gr(function_sets_gr, "all")
    undefined_function_set = select_and_collapse_gr(function_sets_gr,
                                                    "undefined")

    functions_sets = dict(
        used_functions=used_functions_set,
        unused_functions=all_functions_set.difference(used_functions_set),
        undefined_functions=undefined_function_set,
    )

    write_function_lists("all", **functions_sets)

    used_files = set.union(*used_files_sets)

    write_used_file_list("all", used_files)

    used_headers = headers.get_all_included_headers_recursive(
        used_files, [sombrero_include(sombrero_root)])

    write_used_header_list(used_headers)
