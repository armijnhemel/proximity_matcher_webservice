#/usr/bin/env python3
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

import pathlib
import sys

import click
import tlsh

@click.command(short_help='process files and look them up in the webservice')
@click.option('--in_directory', '-i', required=True, help='path to TLSH hashes', type=click.Path(exists=True))
@click.option('--outfile', '-o', required=True, help='out path to TLSH hashes', type=click.File('w'))
def main(in_directory, outfile):

    in_dir = pathlib.Path(in_directory)

    # should be a real directory
    if not in_dir.is_dir():
        print("%s is not a directory, exiting." % in_dir, file=sys.stderr)
        sys.exit(1)

    for result in in_dir.glob('**/*'):
        if not result.is_file():
            continue
        with open(result, 'rb') as infile:
            try:
                data = b" ".join(infile.read().split())
                tlsh_res = tlsh.hash(data)
                if tlsh_res is not None and tlsh_res != '' and tlsh_res != 'TNULL':
                    outfile.write("%s\n" % tlsh_res)
            except Exception as e:
                pass


if __name__ == "__main__":
    main()
