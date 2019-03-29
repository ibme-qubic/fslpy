import glob
import os.path as op
from . import filetree
from pathlib import PurePath
from typing import Tuple, List
import re


tree_directories = ['.', op.join(op.split(__file__)[0], 'trees')]


def search_tree(name: str) -> str:
    """
    Searches for the file defining the specific tree

    Iteratively searches through the directories in ``tree_directories`` till a file named ${name}.tree is found

    :param name: Name of the tree
    :return: path to the file defining the tree
    """
    for directory in tree_directories:
        filename = op.join(directory, name)
        if op.exists(filename):
            return filename
        elif op.exists(filename + '.tree'):
            return filename + '.tree'
    raise ValueError("No file tree found for %s" % name)


def list_all_trees() -> List[str]:
    """Return a list containing paths to all tree files that can be found in
    :data:`tree_directories`
    """
    trees = []
    for directory in tree_directories:
        directory = op.abspath(directory)
        trees.extend(glob.glob(op.join(directory, '*.tree')))
    return trees


def read_line(line: str) -> Tuple[int, PurePath, str]:
    """
    Parses line from the tree file

    :param line: input line from a \*.tree file
    :return: Tuple with:

        - number of spaces in front of the name
        - name of the file or the sub_tree
        - short name of the file
    """
    if line.strip()[:1] == '->':
        return read_subtree_line(line)
    match = re.match(r'^(\s*)(\S*)\s*\((\S*)\)\s*$', line)
    if match is not None:
        gr = match.groups()
        return len(gr[0]), PurePath(gr[1]), gr[2]
    match = re.match(r'^(\s*)(\S*)\s*$', line)
    if match is not None:
        gr = match.groups()
        short_name = gr[1].split('.')[0]
        return len(gr[0]), PurePath(gr[1]), short_name
    raise ValueError('Unrecognized line %s' % line)


def read_subtree_line(line: str, directory: str) -> Tuple[int, "filetree.FileTree", str]:
    """
    Parses the line defining a sub_tree

    :param line: input line from a \*.tree file
    :param directory: containing directory
    :return: Tuple with

        - number of spaces in front of the name
        - sub_tree
        - short name of the sub_tree
    """
    match = re.match(r'^(\s*)->\s*(\S*)(.*)\((\S*)\)', line)
    if match is None:
        raise ValueError("Sub-tree line could not be parsed: {}".format(line.strip()))
    spaces, type_name, variables_str, short_name = match.groups()

    variables = {}
    if len(variables_str.strip()) != 0:
        for single_variable in variables_str.split(','):
            key, value = single_variable.split('=')
            variables[key.strip()] = value.strip()

    sub_tree = filetree.FileTree.read(type_name, directory, **variables)
    return len(spaces), sub_tree, short_name