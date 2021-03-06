#!/usr/bin/env python
__author__ = "mmussomele"

"""Attempts to spellcheck and correct failed cd commands"""

import os
from difflib import get_close_matches
from thefuck.utils import sudo_support
from thefuck.rules import cd_mkdir

MAX_ALLOWED_DIFF = 0.6


def _get_sub_dirs(parent):
    """Returns a list of the child directories of the given parent directory"""
    return [child for child in os.listdir(parent) if os.path.isdir(os.path.join(parent, child))]


@sudo_support
def match(command, settings):
    """Match function copied from cd_mkdir.py"""
    return (command.script.startswith('cd ')
            and ('no such file or directory' in command.stderr.lower()
                 or 'cd: can\'t cd to' in command.stderr.lower()))


@sudo_support
def get_new_command(command, settings):
    """
    Attempt to rebuild the path string by spellchecking the directories.
    If it fails (i.e. no directories are a close enough match), then it 
    defaults to the rules of cd_mkdir. 
    Change sensitivity by changing MAX_ALLOWED_DIFF. Default value is 0.6
    """
    dest = command.script.split()[1].split(os.sep)
    if dest[-1] == '':
        dest = dest[:-1]
    cwd = os.getcwd()
    for directory in dest:
        if directory == ".":
            continue
        elif directory == "..":
            cwd = os.path.split(cwd)[0]
            continue
        best_matches = get_close_matches(directory, _get_sub_dirs(cwd), cutoff=MAX_ALLOWED_DIFF)
        if best_matches:
            cwd = os.path.join(cwd, best_matches[0])
        else:
            return cd_mkdir.get_new_command(command, settings)
    return 'cd "{0}"'.format(cwd)


enabled_by_default = True
