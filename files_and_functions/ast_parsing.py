# coding: utf-8
from pycparser import c_parser, c_ast
from cflags_loader import read_compiler_dflags_lib, get_cpp_dflags
from c_preprocessing import preprocess


def parse_text(text):
    parser = c_parser.CParser()
    ast = parser.parse(text, filename="<none>")

    return ast


def get_ast(grouprep, filename, include_paths, cpp_flags_file):
    dflags = read_compiler_dflags_lib(cpp_flags_file)

    grouprep_dflags = get_cpp_dflags(grouprep, dflags)
    text = preprocess(filename, grouprep_dflags, include_paths)
    return parse_text(text)


def get_asts_for_all_files(grouprep, include_paths, source_files, cpp_flags_file):
    return dict(
        print(f"Processing {filename}")
        or (filename, get_ast(grouprep, filename, include_paths, cpp_flags_file))
        for filename in source_files
    )


def ast_rec_iterator(node, tag="", level=0):
    yield tag, node
    if hasattr(node, "children"):
        for tag, child in node.children():
            yield from ast_rec_iterator(child, tag, level + 1)


def find_function_definitions(ast):

    return dict(
        (node.decl.name, node)
        for _, node in ast_rec_iterator(ast)
        if isinstance(node, c_ast.FuncDef)
    )


def find_function_call_names(ast):

    fcalls = set(
        node.name.name
        for _, node in ast_rec_iterator(ast)
        if isinstance(node, c_ast.FuncCall)
    )

    ids =  set(
        node.name
        for _, node in ast_rec_iterator(ast)
        if isinstance(node, c_ast.ID)
    )

    return set.union(ids,fcalls)
