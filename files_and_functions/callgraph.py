# coding: utf-8
import ast_parsing as ap
import include


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
    info = [
        (name, filename, set(ap.find_function_call_names(node)))
        for filename, ast in all_asts.items()
        for name, node in ap.find_function_definitions(ast).items()
    ]

    call_graph = dict((name, callees) for name, _, callees in info)
    file_function_dict = dict((name, filename) for name, filename, _ in info)

    return call_graph, file_function_dict


class CallGraph:
    def __init__(self, call_graph):
        self.call_graph = call_graph
        self.undefined_functions = set()

    def _iterate_children(self, parent_name, stack=[]):
        if parent_name in self.call_graph:
            for child_name in self.call_graph[parent_name]:
                yield child_name
            for child_name in self.call_graph[parent_name]:
                if child_name not in stack:
                    yield from self._iterate_children(child_name, stack + [child_name])
                else:
                    print(f"Recursion, {child_name} in stack:")
                    print(stack)
        else:
            self.undefined_functions.add(parent_name)

    def __iter__(self):
        yield from self._iterate_children("main", ["main"])


def get_all_defined_functions(callgraph):
    return set(callgraph.keys())


def get_all_used_functions(callgraph):
    cg = CallGraph(callgraph)

    used_functions = set(f for f in cg)

    undefined_functions = cg.undefined_functions

    return used_functions, undefined_functions
