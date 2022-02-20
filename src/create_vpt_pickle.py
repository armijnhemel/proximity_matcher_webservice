import pickle
import sys

import tlsh
import vpt

tlsh_hashes = []
tlsh_to_sha256 = {}

with open('/tmp/tlsh-hashes.txt', 'r') as tlsh_file:
    for i in tlsh_file:
        (sha256_hash, tlsh_hash) = i.strip().split(',')
        if not tlsh_hash in tlsh_to_sha256:
            tlsh_to_sha256[tlsh_hash] = []
            tlsh_hashes.append(tlsh_hash)
        tlsh_to_sha256[tlsh_hash].append(sha256_hash)

tlsh_objects = []

for h in tlsh_hashes:
    try:
        t = tlsh.Tlsh()
        t.fromTlshStr(h)
    except ValueError:
        continue

    tlsh_objects.append(t)
    node = vpt.Node(t)

tidx_list = range(0, len(tlsh_hashes))
root = vpt.vpt_grow(tlsh_objects, tidx_list)

with open('/tmp/bla.pickle', 'wb') as pickle_file:
    vpt.pickle_tree(root, pickle_file)
