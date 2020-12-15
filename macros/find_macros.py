#!/usr/bin/env python3
'''
This module contains a bunch of functions to find the macros that were used.
'''
import re
import header_cleaning as hc

macro_declaration_regexp = r"#define\s+(?P<name>\w+)\s*\("


def _is_macro_line(line):
    return re.search(macro_declaration_regexp, line) is not None


def _get_macro_name(line):
    return (re.search(macro_declaration_regexp, line).groupdict()["name"])


def get_macro_names_set(filename):
    text = hc.remove_quaternions(filename)
    lines = text.split('\n')

    res = frozenset(
        _get_macro_name(line) for line in lines if _is_macro_line(line))
    return res


def get_macro_and_bodies(filename):
    text = hc.remove_quaternions(filename)

    lines = text.replace("\\\n", '').split('\n')

    def add_newline_on_first_line(line):
        split_here = line.find(')') + 1
        return line[:split_here] + '\\\n' + line[split_here:]

    def split_line_at_semicolon(line):
        return line.replace(';', ';\\\n')

    def reformat(line):
        return split_line_at_semicolon(add_newline_on_first_line(line))

    macros = dict((_get_macro_name(line), reformat(line)) for line in lines
                  if _is_macro_line(line))

    return macros


def all_macro_names_set(filenames):
    return frozenset.union(
        *[get_macro_names_set(filename) for filename in filenames])


def common_macro_names_set(filenames):
    return frozenset.intersection(
        *[get_macro_names_set(filename) for filename in filenames])


def specific_macro_names_sets(filenames):
    cm_macros = common_macro_names_set(filenames)
    return dict((filename, get_macro_names_set(filename).difference(cm_macros))
                for filename in filenames)


class MacroCounter():
    def __init__(self, macros):
        self.macro_count = dict()
        self.macros = macros
        # compilation does not seem to save time
        self.regexp_macros = ["(^|\W)" + macro + "(\W|$)" for macro in macros]
        for macro in self.macros:
            self.macro_count[macro] = []

    def line_contain_macros(self, f, line, *args, **kwargs):
        for regexp_macro, macro in zip(self.regexp_macros, self.macros):
            if re.search(regexp_macro, line):
                self.macro_count[macro].append(f(line, *args, **kwargs))

    def get_counts(self):
        return self.macro_count


def process_line(line, *args, **kwargs):
    return (line, args, kwargs)

