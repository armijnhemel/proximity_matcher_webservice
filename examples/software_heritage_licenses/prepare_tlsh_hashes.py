#!/usr/bin/env python3
#
# Copyright 2022-2023 - Armijn Hemel
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

@click.command(short_help='Calculate TLSH hashes for files and write to a file')
@click.option('--in_directory', '-i', required=True, help='path to TLSH hashes',
              type=click.Path(exists=True, path_type=pathlib.Path))
@click.option('--outfile', '-o', required=True, help='out path to TLSH hashes',
              type=click.File('w'))
def main(in_directory, outfile):
    # should be a real directory
    if not in_directory.is_dir():
        print(f"{in_dir} is not a directory, exiting.", file=sys.stderr)
        sys.exit(1)

    for result in in_directory.glob('**/*'):
        if not result.is_file():
            continue
        with open(result, 'rb') as infile:
            try:
                data = b" ".join(infile.read().split())
                tlsh_res = tlsh.hash(data)
                if tlsh_res is not None and tlsh_res != '' and tlsh_res != 'TNULL':
                    outfile.write(f"{tlsh_res}\n")
            except Exception:
                pass


if __name__ == "__main__":
    main()
