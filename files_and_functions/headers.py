#!/usr/bin/env python3
import re
import os


def get_included_headers(source_filename):
    headers = set()

    with open(source_filename, 'r') as f:
        for line in f.readlines():
            match = re.search(r'#include\s+["<](\w+.h)[">]', line)
            if match:
                headers.add(match.groups()[0])

    return headers


def get_all_included_headers(filenames):
    return set.union(*[get_included_headers(f) for f in filenames])


def look_for_existing_version(header_basename, includepaths):
    header_path_candidates = [
        full_path for includepath in ([''] + includepaths) if os.path.exists((
            full_path := os.path.join(includepath, header_basename)))
    ]
    if header_path_candidates:
        return header_path_candidates[0]


def get_included_headers_recursive(filename, includepaths):
    headers = get_all_included_headers([filename])

    additional_headers = set()

    for header in headers:
        header_path = look_for_existing_version(header, includepaths)
        if header_path:
            child_headers = get_included_headers_recursive(
                header_path, includepaths)
            if child_headers:
                additional_headers = additional_headers.union(child_headers)

    return headers.union(additional_headers)


def get_all_included_headers_recursive(filenames, includepaths):
    headers = set.union(*[get_included_headers_recursive(f, includepaths) for f in filenames])

    return [
        fp for header in headers
        if (fp := look_for_existing_version(header, includepaths))
    ]
