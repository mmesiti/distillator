# coding: utf-8
import ast_parsing as ap
import include


def get_graph_from_callgraph_info(callgraph_info):
    '''Assuming that names are unique: can be false! '''
    call_graph = [(name, callees) for name, filename, storage, callees in call_graph_info]
    return dict(call_graph)

def get_file_function_dict_from_callgraph_info(callgraph_info):
    '''Assuming that names are unique: can be false! '''
    file_function_dict = dict((name, filename) for name, filename, callees in info)


def get_callgraph(
    grouprep,
    sombrero_root,
    pycparser_root,
    source_filename_filter_function,
    cpp_flags_file,
):
    source_files = include.source_files(source_filename_filter_function, sombrero_root)
    all_asts = ap.get_asts_for_all_files(
        grouprep,
        include.get_paths(sombrero_root, pycparser_root),
        source_files,
        cpp_flags_file,
    )
    callgraph_info = [
        (name, filename, storage, set(ap.find_function_call_names(node)))
        for filename, ast in all_asts.items()
        for name, storage, node in ap.find_function_definitions(ast)
    ]

    # used to return callgraph and file_function_dict
    return callgraph_info

class CallGraph:
    def __init__(self, call_graph_info, root_info):
        self.call_graph_info = call_graph_info
        self.defined_function_names = set(name for name,filename,storage,callees in call_graph_info)
        self.undefined_functions = set()
        self.root_function, self.root_file = root_info

    def find_func_candidates_by_name(self,func_name):
        return [(name,filename,storage,callees)
                    for name,filename,storage,callees
                    in self.call_graph_info
                    if name == func_name]

    def find_children(self,parent_name, filename):
        '''
        parent_name: name of the function
        filename: filename where the function is defined
        '''
        assert type(filename) == str, f"WRONG TYPE: {parent_name} {filename}"


        parent_candidates_info = self.find_func_candidates_by_name(parent_name)
        if not parent_candidates_info:
            return None
        try:
            parent_info = next( info for info in parent_candidates_info if info[1] == filename)
        except StopIteration:
            print("Problem in parent_info", parent_candidates_info)
            print(parent_name, filename)
            raise StopIteration

        name,filename,storage,callees = parent_info
        callee_infos = [ callee_info
                         for callee in callees
                         for callee_info in self.find_func_candidates_by_name(callee) ]

        name_file_children = [
            (name_callee, filename_callee)
            for name_callee,filename_callee,storage_callee,_ in callee_infos
            if storage_callee != ['static'] or filename_callee == filename
        ]

        return name_file_children

    def _iterate_children(self, parent_name, filename, stack=[]): # TODO: fix to use full callgraph info
        '''
        parent_name: name of the function
        filename: filename where the function is defined
        '''
        if parent_name in self.defined_function_names:
            children_info = self.find_children(parent_name,filename)
            for child_name,child_filename in children_info:
                yield child_name, child_filename
            for child_name,child_filename in children_info:
                if (child_name,child_filename) not in stack:
                    yield from self._iterate_children(child_name, child_filename, stack + [child_name,child_filename])
                else:
                    print(f"Recursion, {child_filename}:{child_name} in stack:")
                    print(stack)
        else:
            self.undefined_functions.add(parent_name)

    def __iter__(self):
        yield from self._iterate_children(self.root_function, self.root_file, ["main"])


def get_all_defined_functions(callgraph_info):
    return set(f"{filename}:{name}" for name,filename,storage,callees in callgraph_info)


def get_all_used_functions(callgraph, root_info):
    cg = CallGraph(callgraph, root_info)

    used_functions = set(f"{fn}:{n}" for n,fn in cg)

    undefined_functions = cg.undefined_functions

    return used_functions, undefined_functions
