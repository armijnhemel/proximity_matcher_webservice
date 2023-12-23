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

import csv
import hashlib
import pathlib

import tlsh
import click


@click.command(short_help='process')
@click.option('--output', '-o', required=True, help='path to output CSV file', type=click.File('w'))
@click.option('--directory', '-d', required=True, help='path to samples directory',
              type=click.Path(exists=True, path_type=pathlib.Path))
def main(output, directory):
    fieldnames = ['sha1', 'sha256', 'tlsh', 'normalized_sha256', 'normalized_tlsh']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    # read every file in the collection. First open the file in
    # text mode to get rid of the files that do not contain valid
    # UTF-8 characters.
    for sample in directory.glob('**/*'):
        if not sample.is_file():
            continue
        try:
            sha1sum = sample.name
            with sample.open(mode='r') as license_file:
                # read the data
                data = license_file.read()

                # tokenize to get rid of all the whitespace
                tokens = data.split()

                # reconstruct a "normalized" license text
                license_data = " ".join(tokens)

                # convert to bytes
                binary_license_data = license_data.encode()

                # compute tlsh hash
                normalized_tlsh_hash = tlsh.hash(binary_license_data)

            # compute SHA256 but only in case if there is a valid TLSH
            if normalized_tlsh_hash not in ['TNULL', '']:
                sha256sum = hashlib.new('sha256')
                sha256sum.update(binary_license_data)
                normalized_sha256 = sha256sum.hexdigest()

                with sample.open(mode='rb') as license_file:
                    # reread original data (as binary) and compute sha256
                    data = license_file.read()
                    sha256sum = hashlib.new('sha256')
                    sha256sum.update(data)
                    tlsh_hash = tlsh.hash(data)
                writer.writerow({'sha1': sha1sum, 'sha256': sha256sum.hexdigest(),
                                 'tlsh': tlsh_hash, 'normalized_sha256': normalized_sha256,
                                 'normalized_tlsh': normalized_tlsh_hash})
        except:
            pass

if __name__ == "__main__":
    main()
