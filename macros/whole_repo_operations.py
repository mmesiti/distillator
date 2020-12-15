from os import path
from os import walk
import include_filenames as inc_files

def iterate_on_all_lines(root,fun,*args, **kwargs):
    res = []

    includedir = path.join(root,"Include")
    starting_includes = set.union(
        set(inc_files.get_suN_like_files(includedir)),
        set(inc_files.get_suN_types_like_files(includedir)),
        set(inc_files.get_suN_repr_func_like_files(includedir))
    )
    print("Starting includes:")
    print('\n'.join(starting_includes))


    def select_ch_avoid_suNh_and_fullize(dirpath,filenames):

         return (full_path for fname in filenames
                 if (full_path:=path.join(dirpath,fname))
                 not in starting_includes and #
                 (full_path.endswith('.c') or
                  full_path.endswith('.c.sdtmpl') or
                  full_path.endswith('.h') or
                  full_path.endswith('.cpp')) and
                 '/.' not in full_path # avoiding hidden directories
                 )

    for dirpath, directories, filenames in walk(root):

        for full_path in select_ch_avoid_suNh_and_fullize(dirpath,filenames):
           print(f"Processing {full_path}")
           with open(full_path, 'r') as f:
               for n,line in enumerate(f.readlines()):
                   r = fun(line,n,full_path,*args,**kwargs)
                   res.append(r)
    return res
