from os import path

def get_files_matching_template(directory,template,cases):
    return [path.join(directory,template.format(case = c)) for c in cases]

# NOTE: SU3AS is named incorrectly, should be SU3S, but su3as is the name currently used.
groupreps = ["sp4","sp4adj","su2","su2adj","su3","su3as"]

def get_suN_like_files(directory):
    return get_files_matching_template(directory,
                                       r"{case}.h",
                                       groupreps)

def get_suN_types_like_files(directory):
    return get_files_matching_template(directory,
                                       r"{case}_types.h",
                                       groupreps)

def get_suN_repr_func_like_files(directory):
    return get_files_matching_template(directory,
                                       r"{case}_repr_func.h",
                                       groupreps)
