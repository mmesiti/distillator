import find_macros as fm
import include_filenames as incfiles


def get_all_macros_versions(includedir):
    fund_files = incfiles.get_suN_like_files(includedir)
    repr_files = incfiles.get_suN_repr_func_like_files(includedir)

    return [
        (grouprep,macroname,macrobody)
        for grouprep,fund_file,repr_file
        in zip(incfiles.groupreps, fund_files, repr_files)
        for macroname, macrobody in {
                **fm.get_macro_and_bodies(fund_file),
                **fm.get_macro_and_bodies(repr_file),
        }.items() ]


def collect_versions_of_single_macro(all_macros_versions_bodies, macro):

    groupreps_bodies = [ (grouprep,macrobody)
               for grouprep,macroname,macrobody
               in all_macros_versions_bodies
               if macroname == macro
              ]

    return groupreps_bodies

def collect_macros_for_single_versions(all_macros_versions_bodies,grouprep_name, macro_selection):
    bodies = [ macrobody
               for grouprep,macroname,macrobody
               in all_macros_versions_bodies
               if grouprep == grouprep_name 
               and macroname in macro_selection
              ]
    return bodies

def assemble_macro_groupreps_bodies(groupreps_bodies):
    return '\n'.join(string
                     for grouprep,macrobody in groupreps_bodies
                     for string in [ f"// {grouprep}", macrobody + '\n' ])

