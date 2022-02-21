import pickle
import sys

import tlsh
from flask import Flask

from flask import abort, jsonify

import vpt

# two data structures that are currently not used, but could be filled
# with data to speed up looking up known files or used to return some
# useful information directly to the clients, without needing to do an
# extra lookup in an external file or database.
tlsh_hashes = set()
tlsh_to_sha256 = {}

with open('/tmp/tlsh-hashes.txt', 'r') as tlsh_file:
    for h in tlsh_file:
        tlsh_hashes.add(h.strip())

# load tlsh VPT
with open('/tmp/licenses-tlsh.pickle', 'rb') as pickle_file:
    root = vpt.pickle_restore(pickle.load(pickle_file))

app = Flask(__name__)

@app.route("/tlsh/<tlsh_hash>")
def process_tlsh(tlsh_hash):
    h = tlsh.Tlsh()
    try:
        h.fromTlshStr(tlsh_hash)
    except ValueError:
        abort(404, "invalid TLSH string")

    # immediately return the result if it is a known hash
    if tlsh_hash in tlsh_hashes:
        best = 0
        best_match = tlsh_hash
        res = {'match': True, 'tlsh': best_match, 'distance': best}
        return jsonify(res)

    # first verify if the TLSH hash is a correct hash
    best = sys.maxsize
    best_match = None

    best_vpt = {"dist": sys.maxsize, "hash": None}

    vpt_result = vpt.vpt_search(root, h, best_vpt)
    if vpt_result is not None:
        #res = {'match': True, 'tlsh': vpt_result['hash'], 'distance': vpt_result['dist'], 'closest_sha256_hashes': tlsh_to_sha256[vpt_result['hash']]}
        res = {'match': True, 'tlsh': vpt_result['hash'], 'distance': vpt_result['dist']}
    else:
        res = {'match': False}

    return jsonify(res)
