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

import pickle
import statistics

import tlsh


class Node:
    '''Vantage point tree'''
    def __init__(self, tobj, idx=-1, threshold=0):
        self.left_child = None
        self.right_child = None
        self.tobj = tobj
        self.threshold = threshold

def vpt_grow(tlsh_object_list, tlsh_index_list):
    '''Grow a Vantage Point Tree given a list of objects and indexes'''
    lenList = len(tlsh_object_list)

    vantage_point_object = tlsh_object_list[0]
    vantage_point_index = tlsh_index_list[0]

    if lenList == 1:
        thisNode = Node(vantage_point_object, vantage_point_index, -1)
        return thisNode

    # compute the TLSH distances for each object
    distances_list = [vantage_point_object.diff(h1) for h1 in tlsh_object_list]

    # determine the median
    med = statistics.median_low(distances_list)

    thisNode = Node(vantage_point_object, vantage_point_index, med)

    # split data into two lists: left child and right
    # child depending on the TLSH distance to vantage_point_object
    tlsh_objects_left = []
    tlsh_indexes_left = []

    tlsh_objects_right = []
    tlsh_indexes_right = []

    for li in range(1, lenList):
        if distances_list[li] < med:
            tlsh_objects_left.append(tlsh_object_list[li])
            tlsh_indexes_left.append(tlsh_index_list[li])
        else:
            tlsh_objects_right.append(tlsh_object_list[li])
            tlsh_indexes_right.append(tlsh_index_list[li])

    # recursively walk the data, unless there is no more data
    if tlsh_objects_left != []:
        thisNode.left_child = vpt_grow(tlsh_objects_left, tlsh_indexes_left)
    else:
        thisNode.left_child = None
    if tlsh_objects_right != []:
        thisNode.right_child = vpt_grow(tlsh_objects_right, tlsh_indexes_right)
    else:
        thisNode.right_child = None
    return thisNode

extra_constant = 20

def vpt_search(node, search_item, best):
    '''Search a TLSH hash in a VPT'''
    if node is None:
        return

    # compute the TLSH distance between the item
    # to be searched and the node of the tree
    d = search_item.diff(node.tobj)
    if d < best['dist']:
        best['dist'] = d
        best['hash'] = node.tobj.hexdigest()

    if d == 0:
        return best

    if d <= node.threshold:
        best_child = vpt_search(node.left_child, search_item, best)
        if (d + best['dist'] + extra_constant) >= node.threshold:
            best_child = vpt_search(node.right_child, search_item, best)
    else:
        best_child = vpt_search(node.right_child, search_item, best)
        if (d - best['dist'] - extra_constant) <= node.threshold:
            best_child = vpt_search(node.left_child, search_item, best)

    if best_child is not None:
        if best_child['dist'] < best['dist']:
            best = best_child

    return best

# pickle related methods
def pickle_tree(root, pickle_file):
    pickle_prep(root)
    pickle.dump(root, pickle_file)

def pickle_prep(node):
    if node:
        #del node.tobj
        node.tobj = node.tobj.hexdigest()
        pickle_prep(node.left_child)
        pickle_prep(node.right_child)

def pickle_restore(node):
    if node:
        h = tlsh.Tlsh()
        h.fromTlshStr(node.tobj)
        node.tobj = h
        pickle_restore(node.left_child)
        pickle_restore(node.right_child)
        return node
