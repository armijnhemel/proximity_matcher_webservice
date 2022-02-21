import multiprocessing
import sys

import click
import requests
import tlsh

def lookup_hash(tlsh_queue):
    while True:
        tlsh_hash = tlsh_queue.get()
        try:
            req = requests.get('http://127.0.0.1:5000/tlsh/%s' % tlsh_hash)
            print(req.json())
            sys.stdout.flush()
        except requests.exceptions.RequestException:
            pass

        tlsh_queue.task_done()


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

    processmanager = multiprocessing.Manager()

    # create a queue for scanning files
    tlsh_queue = processmanager.JoinableQueue(maxsize=0)
    processes = []

    threads = multiprocessing.cpu_count()

    for t in tlsh_hashes:
        tlsh_queue.put(t)

    # create processes for unpacking archives
    for i in range(0, threads):
        process = multiprocessing.Process(target=lookup_hash,
                                          args=(tlsh_queue,))
        processes.append(process)

    # start all the processes
    for process in processes:
        process.start()

    tlsh_queue.join()

    # Done processing, terminate processes
    for process in processes:
        process.terminate()


if __name__ == "__main__":
    main()
