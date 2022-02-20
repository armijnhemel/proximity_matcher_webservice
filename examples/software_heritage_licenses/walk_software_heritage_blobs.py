#!/usr/bin/env python3

import os
import sys
import csv
import hashlib
import pathlib

import tlsh
import click


@click.command(short_help='process')
@click.option('--output', '-o', required=True, help='path to output CSV file', type=click.File('w'))
@click.option('--directory', '-d', required=True, help='path to samples directory')
def main(output, directory):
    directory = pathlib.Path(directory)

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
            with sample.open(mode='r') as p:
                # read the data
                data = p.read()

                # tokenize to get rid of all the whitespace
                tokens = data.split()

                # reconstruct a "normalized" license text
                license_data = " ".join(tokens)

                # convert to bytes
                binary_license_data = license_data.encode()

                # compute sha256 and tlsh hashes
                normalized_tlsh_hash = tlsh.hash(binary_license_data)

            if normalized_tlsh_hash != 'TNULL' and normalized_tlsh_hash != '':
                sha256sum = hashlib.new('sha256')
                sha256sum.update(binary_license_data)
                normalized_sha256 = sha256sum.hexdigest()

                with sample.open(mode='rb') as p:
                    # reread original data (as binary) and compute sha256
                    data = p.read()
                    sha256sum = hashlib.new('sha256')
                    sha256sum.update(data)
                    tlsh_hash = tlsh.hash(data)
                writer.writerow({'sha1': sha1sum, 'sha256': sha256sum.hexdigest(), 'tlsh': tlsh_hash,
                                 'normalized_sha256': normalized_sha256, 'normalized_tlsh': normalized_tlsh_hash})
        except:
            pass

if __name__ == "__main__":
    main()
