import sys

import click
import requests
import tlsh

@click.command(short_help='process TLSH hashes and look them up in the webservice')
@click.option('--infile', '-i', required=True, help='path to TLSH hashes', type=click.File('r'))
def main(infile):

    tlsh_hashes = set()
    with infile as tlsh_file:
        for i in tlsh_file:
            tlsh_hash = i.strip()
            if tlsh_hash in tlsh_hashes:
                continue

            tlsh_hashes.add(tlsh_hash)

            try:
                t = tlsh.Tlsh()
                t.fromTlshStr(tlsh_hash)
            except ValueError:
                continue

            try:
                req = requests.get('http://127.0.0.1:5000/tlsh/%s' % tlsh_hash)
                print(req.json())
                sys.stdout.flush()
            except requests.exceptions.RequestException:
                pass

if __name__ == "__main__":
    main()
