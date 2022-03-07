################################################################
# TLSH is provided for use under two licenses: Apache OR BSD. Users
# may opt to use either license depending on the license
# restictions of the systems with which they plan to integrate the TLSH code.
#
# Apache License: # Copyright 2013 Trend Micro Incorporated
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may obtain a copy of the License at      http://www.apache.org/licenses/LICENSE-2.0
#
# BSD License: # Copyright (c) 2013, Trend Micro Incorporated. All rights reserved.
#
# see file "LICENSE
#################################################################

# Additional code was written by Armijn Hemel
# Pickle methods written by Imre Fodi and Tijmen van der Spijk
# as part of a research project for OS3 <https://www.os3.nl/>
# These contributions are under Apache 2.0
# SPDX-License-Identifier: Apache-2.0

import pickle
import pickletools
import statistics
import sys

import tlsh


class Tree:
    '''Vantage point tree'''
    __slots__ = ['tobj', 'threshold', 'left_child', 'right_child']

    def __init__(self, tobj, threshold=0):
        self.left_child = None
        self.right_child = None
        self.tobj = tobj
        self.threshold = threshold

def vpt_grow(tlsh_object_list):
    '''Grow a Vantage Point Tree given a list of objects and indexes'''
    lenList = len(tlsh_object_list)

    vantage_point_object = tlsh_object_list[0]

    if lenList == 1:
        thisTree = Tree(vantage_point_object, -1)
        return thisTree

    # compute the TLSH distances for each object
    distances_list = [vantage_point_object.diff(h1) for h1 in tlsh_object_list]

    # determine the median
    med = statistics.median_low(distances_list)

    thisTree = Tree(vantage_point_object, med)

    # split data into two lists: left child and right
    # child depending on the TLSH distance to vantage_point_object
    tlsh_objects_left = []

    tlsh_objects_right = []

    for li in range(1, lenList):
        if distances_list[li] < med:
            tlsh_objects_left.append(tlsh_object_list[li])
        else:
            tlsh_objects_right.append(tlsh_object_list[li])

    # recursively walk the data, unless there is no more data
    if tlsh_objects_left != []:
        thisTree.left_child = vpt_grow(tlsh_objects_left)
    else:
        thisTree.left_child = None
    if tlsh_objects_right != []:
        thisTree.right_child = vpt_grow(tlsh_objects_right)
    else:
        thisTree.right_child = None
    return thisTree

extra_constant = 20

def vpt_search(tree, search_item, best):
    '''Search a TLSH hash in a VPT'''
    if tree is None:
        return

    # compute the TLSH distance between the item
    # to be searched and the tree of the tree
    d = search_item.diff(tree.tobj)
    if d < best['dist']:
        best['dist'] = d
        best['hash'] = tree.tobj.hexdigest()

    if d == 0:
        return best

    if d <= tree.threshold:
        best_child = vpt_search(tree.left_child, search_item, best)
        if (d + best['dist'] + extra_constant) >= tree.threshold:
            best_child = vpt_search(tree.right_child, search_item, best)
    else:
        best_child = vpt_search(tree.right_child, search_item, best)
        if (d - best['dist'] - extra_constant) <= tree.threshold:
            best_child = vpt_search(tree.left_child, search_item, best)

    if best_child is not None:
        if best_child['dist'] < best['dist']:
            best = best_child

    return best

# pickle related methods
def pickle_tree(root, pickle_file, optimize=True):
    recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(recursion_limit + 1000)
    pickle_prep(root)
    if optimize:
        pickle_file.write(pickletools.optimize(pickle.dumps(root)))
    else:
        pickle.dump(root, pickle_file)

def pickle_prep(tree):
    if tree:
        tree.tobj = tree.tobj.hexdigest()
        pickle_prep(tree.left_child)
        pickle_prep(tree.right_child)

def pickle_restore(tree):
    if tree:
        h = tlsh.Tlsh()
        h.fromTlshStr(tree.tobj)
        tree.tobj = h
        pickle_restore(tree.left_child)
        pickle_restore(tree.right_child)
        return tree
