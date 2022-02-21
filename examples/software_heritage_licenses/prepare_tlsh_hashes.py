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
