import find_macros as fm
import include_filenames as incfiles


def files_have_same_macros(filenames):
    '''This is actually not true: different representations
       will have different number of macros.'''
    def check_all_equal(container):
        return len(set(container)) == 1

    return check_all_equal(fm.get_macros(filename)
                           for filename in filenames)


def get_suN_like_common_macros_set(directory):
    filenames = incfiles.get_suN_like_files(directory)
    return fm.common_macro_names_set(filenames)

def get_suN_repr_func_like_common_macros_set(directory):
    filenames = incfiles.get_suN_repr_func_like_files(directory)
    return fm.common_macro_names_set(filenames)


# just to ckeck
def get_suN_like_all_macros_set(directory):
    filenames = incfiles.get_suN_like_files(directory)
    return fm.all_macro_names_set(filenames)

def get_suN_repr_func_like_all_macros_set(directory):
    filenames = incfiles.get_suN_repr_func_like_files(directory)
    return fm.all_macro_names_set(filenames)
