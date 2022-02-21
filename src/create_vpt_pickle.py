import pickle
import sys

import click
import tlsh

import vpt

@click.command(short_help='process TLSH hashes and turn into a pickle')
@click.option('--infile', '-i', required=True, help='file with TLSH hashes', type=click.File('r'))
@click.option('--outfile', '-o', help='output file for VPT pickle', type=click.File('wb'))
def main(infile, outfile):
    tlsh_hashes = set()

    with infile as tlsh_file:
        for i in tlsh_file:
            tlsh_hash = i.strip()
            if tlsh_hash in tlsh_hashes:
                continue
            tlsh_hashes.add(tlsh_hash)

    tlsh_objects = []

    for h in tlsh_hashes:
        try:
            t = tlsh.Tlsh()
            t.fromTlshStr(h)
        except ValueError:
            continue

        tlsh_objects.append(t)

    if tlsh_objects != []:
        root = vpt.vpt_grow(tlsh_objects)

        vpt.pickle_tree(root, outfile)

if __name__ == "__main__":
    main()
