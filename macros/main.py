#!/usr/bin/env python3
import whole_repo_operations as repop
import find_macros as fm
import macro_sets as ms
from os import path, makedirs
import macro_versions as mv
from sys import argv

rootdir = argv[1]
tmpdir = argv[2]
includedir = path.join(rootdir, "Include")


def check_all_macros(directory):
    all_fund_macros = ms.get_suN_like_all_macros(directory)
    print(len(all_fund_macros))
    all_repr_func_macros = ms.get_suN_repr_func_like_all_macros(directory)
    print(len(all_repr_func_macros))


def get_used_macros(rootdir, includedir, all_macros_set):

    macro_counter = fm.MacroCounter(all_macros_set)
    _ = repop.iterate_on_all_lines(
        rootdir,
        lambda line, *args, **kwargs: macro_counter.line_contain_macros(
            fm.process_line, line, *args, **kwargs))

    counts = macro_counter.get_counts()
    #[print(k, v) for k, v in counts.items() if not k.startswith('__')]
    return ((k, l) for k, v in counts.items() if (l := len(v)) != 0)


def print_header(_message, motif='+'):
    message = ' '.join((motif,_message,motif))
    print(len(message) * motif)
    print(message)
    print(len(message) * motif)


def print_nuses(macros_nuses):
    message = "Number of times each macro is used (not in suN.h or suN_repr_func.h):"
    print_header(message)
    for mname, nuses in macros_nuses.items():
        print(f"{mname}:{nuses}")
    print(len(message) * '+')


def save_used_macro_list(macros_nuses, macros_set_name,save_dir):
    used_macros_names_filename = path.join(save_dir,f"used_macros{macros_set_name}.txt")
    print(f"writing used macro list in {used_macros_names_filename}")
    with open(used_macros_names_filename, 'w') as f:
        for mname in macros_nuses:
            f.write(f"{mname}\n")


def write_macro_files_by_name(all_macros_versions, macros_set_name,
                              macros_selection,save_dir):
    # writing out files with macro versions - one file per macro
    # other view of array
    all_bodies_by_macro = [
        (macro_name,
         mv.collect_versions_of_single_macro(all_macros_versions, macro_name))
        for macro_name in macros_selection
    ]

    macros_versions_filedir = path.join(save_dir, f"used_macros_by_name{macros_set_name}")
    makedirs(macros_versions_filedir, exist_ok=True)
    for macro_name, macro_body_versions in all_bodies_by_macro:
        all_bodies_text = mv.assemble_macro_groupreps_bodies(
            macro_body_versions)
        macro_filename = path.join(macros_versions_filedir,
                                   f"macro{macro_name}.h")
        print(f"Saving {macro_filename}")
        with open(macro_filename, 'w') as f:
            f.write(all_bodies_text)


def write_macro_files_by_version(all_macros_versions, macros_set_name,
                                 macros_selection,save_dir):
    all_used_bodies_by_version = [
        (grouprep,
         mv.collect_macros_for_single_versions(all_macros_versions, grouprep,
                                               macros_selection))
        for grouprep in mv.incfiles.groupreps
    ]

    grouprep_filedir = path.join(save_dir,f"used_macros_by_grouprep{macros_set_name}")
    makedirs(grouprep_filedir, exist_ok=True)
    for grouprep, macros in all_used_bodies_by_version:
        all_bodies_text = '\n\n'.join(macros) + "\n\n"
        grouprep_filename = path.join(grouprep_filedir, f"{grouprep}{macros_set_name}.h")
        print(f"Saving {grouprep_filename}")
        with open(grouprep_filename, 'w') as f:
            f.write(all_bodies_text)

def complete_macro_names_set(detected_used_macro_names, all_macros_versions):
    # we make sure that all the macro that are referenced in other used macros
    # are counted in.

    groupreps = set(gr for gr, _, _ in all_macros_versions)

    used_macro_names_groupreps = []
    for grouprep in groupreps:
        used_macro_names = frozenset(detected_used_macro_names)

        all_macros = dict((name, body)
                          for gr, name, body in all_macros_versions
                          if gr == grouprep)

        while True:
            enlarged_macro_names = set(used_macro_names)

            for macro_name in all_macros:
                for used_macro in used_macro_names:
                    if used_macro in all_macros and macro_name in all_macros[used_macro]:
                        enlarged_macro_names.add(macro_name)

            if used_macro_names == enlarged_macro_names:
                break
            else:
                used_macro_names = frozenset(enlarged_macro_names)

        used_macro_names_groupreps.append(used_macro_names)

    used_macro_names = frozenset.union(*used_macro_names_groupreps)

    return used_macro_names


def select_macros(rootdir, includedir, macros_set_name, macros_set, save_dir):
    # collecting used macros
    macros_nuses = dict(get_used_macros(rootdir, includedir, macros_set))

    # Get all the bodies and versions of all the macros
    all_macros_versions = mv.get_all_macros_versions(includedir)


    print_nuses(macros_nuses)

    used_macro_names = complete_macro_names_set(macros_nuses.keys(), all_macros_versions)

    # printing file with a list of the names of the used macros
    save_used_macro_list(used_macro_names , macros_set_name, save_dir)


    # writing out files with macro versions - one file per macro
    # other view of array
    write_macro_files_by_name(all_macros_versions, macros_set_name,
                              used_macro_names,save_dir)

    # writing out files with macro versions - one file version
    # other view of array
    write_macro_files_by_version(all_macros_versions, macros_set_name,
                                 used_macro_names,save_dir)


if __name__ == "__main__":
    all_fund_macros_set = ms.get_suN_like_all_macros_set(includedir)
    all_repr_func_macros_set = ms.get_suN_repr_func_like_all_macros_set(
        includedir)

    print('\n\n\n')
    print_header("Selecting fundamental macros", '#')
    select_macros(rootdir, includedir, '', all_fund_macros_set,tmpdir)

    print('\n\n\n')
    print_header("Selecting 'repr_func' macros", '#')
    select_macros(rootdir, includedir, "_repr_func",
                  all_repr_func_macros_set,tmpdir)
