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

import click
import tlsh

import proximity_matcher_webservice.vpt as vpt

@click.command(short_help='process TLSH hashes and turn into a pickle')
@click.option('--infile', '-i', required=True, help='file with TLSH hashes',
              type=click.File('r'))
@click.option('--outfile', '-o', required=True, help='output file for VPT pickle',
              type=click.File('wb'))
@click.option('--no-optimize', 'optimize', help='disable optimizing pickle',
              default=True, flag_value=False, is_flag=True)
def main(infile, outfile, optimize):
    tlsh_hashes = set()

    with infile as tlsh_file:
        for line in tlsh_file:
            tlsh_hash = line.strip()
            if tlsh_hash in tlsh_hashes:
                continue
            tlsh_hashes.add(tlsh_hash)

    tlsh_objects = []

    for tlsh_string in tlsh_hashes:
        try:
            tlsh_hash = tlsh.Tlsh()
            tlsh_hash.fromTlshStr(tlsh_string)
        except ValueError:
            continue

        tlsh_objects.append(tlsh_hash)

    if tlsh_objects:
        root = vpt.vpt_grow(tlsh_objects)

        vpt.pickle_tree(root, outfile, optimize)

if __name__ == "__main__":
    main()
