#!/usr/bin/env python3
def _starts_comment(line):
    return "/*" in line and "*/" not in line[line.find("/*"):]


def _ends_comment(line):
    return "*/" in line and "/*" not in line[line.find("*/"):]


def next_comment_state(line, already_in_comment):
    res = ((not already_in_comment and _starts_comment(line))
           or already_in_comment and not _ends_comment(line))
    return res
