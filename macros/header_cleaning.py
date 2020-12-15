#!/usr/bin/env python3
import subprocess

def remove_quaternions(filename):
    '''
    Remove the "WITH_QUATERNIONS" branch.
    '''

    command = f"cpp -undef -fdirectives-only {filename}"

    completed_process = subprocess.run(command.split(), capture_output = True)
    res = completed_process.stdout.decode('UTF-8').replace(';',';\\\n')
    return res
