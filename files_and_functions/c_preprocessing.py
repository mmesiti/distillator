#!/usr/bin/env python3
import subprocess, os


def preprocess(filepath, flags, include_paths):

    include_flags = ["-I" + p for p in include_paths]
    all_cpp_flags = include_flags + flags
    cpp = "cpp"

    tmp_filepath = filepath + "_cpptmp.c"
    text = "#define __attribute__(x)\n"
    text += "#define complex _Complex\n"
    text += "#define __inline\n"

    with open(filepath, "r") as f:
        text += f.read()

    with open(tmp_filepath, "w") as f:
        f.write(text)
    output = subprocess.run([cpp] + all_cpp_flags + [tmp_filepath], capture_output=True)
    stderr = output.stderr.decode("UTF-8")
    if stderr:
        print("STDERR:", stderr)
    os.remove(tmp_filepath)
    return output.stdout.decode("UTF-8")
