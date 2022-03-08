#!/usr/bin/env python3
#
# Copyright 2022 - Armijn Hemel
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import multiprocessing
import pickle
import sys

import tlsh
from flask import Flask

from flask import abort, jsonify

from werkzeug.serving import WSGIRequestHandler

import vpt

processmanager = multiprocessing.Manager()

# data structure filled with data to speed up looking up known files
tlsh_hashes = set()

tlsh_hashes_file = '/tmp/tlsh-hashes.txt'
with open(tlsh_hashes_file, 'r') as tlsh_file:
    for h in tlsh_file:
        tlsh_hashes.add(h.strip())

# turn into a dict shared between all threads
tlsh_hashes = dict.fromkeys(tlsh_hashes, None)
tlsh_hashes = processmanager.dict(tlsh_hashes)

# data structure that is currently not used, but could be filled
# with data to return some useful information directly to the clients,
# without needing to do an extra lookup in an external file or database.
tlsh_to_sha256 = {}

# load tlsh VPT
tlsh_pickle_file = '/tmp/licenses-tlsh.pickle'
with open(tlsh_pickle_file, 'rb') as pickle_file:
    root = vpt.pickle_restore(pickle.load(pickle_file))

WSGIRequestHandler.protocol_version = "HTTP/1.1"
app = Flask(__name__)

@app.route("/tlsh/<tlsh_hash>")
def process_tlsh(tlsh_hash):
    # first verify if the TLSH hash is a correct hash
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

    best_vpt = {"dist": sys.maxsize, "hash": None}

    vpt_result = vpt.vpt_search(root, h, best_vpt)
    if vpt_result is not None:
        #res = {'match': True, 'tlsh': vpt_result['hash'].hexdigest(), 'distance': vpt_result['dist'], 'closest_sha256_hashes': tlsh_to_sha256[vpt_result['hash']]}
        res = {'match': True, 'tlsh': vpt_result['hash'].hexdigest(), 'distance': vpt_result['dist']}
    else:
        res = {'match': False}

    return jsonify(res)
