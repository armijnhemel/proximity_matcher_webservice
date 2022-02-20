# Matching license texts from Software Heritage

This directory contains scripts to process license data from Software Heritage
and to enable proximity matching with TLSH.

## Data

The data can be downloaded from Software Heritage. In this example the data set
from March 2021 was used:

<https://annex.softwareheritage.org/public/dataset/license-blobs/2021-03-23/>

The license texts are found in the file `blobs.tar.zst`. This is a Zstandard
compressed tar file. Unpack it as follows:

```
$ tar xf /path/to/blobs.tar.zst
```

The result will be a directory with 6,009,466 files. You will need around
52 GiB of disk space to store these files.

Also download the files `blobs-origins.csv.zst` and `license-blobs.csv.zst`.
The file `license-blobs.csv.zst` contains a CSV file mapping SHA1 checksums to
Software Heritage identifiers (`swhid`) and file names. The file
`blobs-origins.csv.zst` maps Software Heritage identifiers to origins (like
GitHub repositories).

## Preparing the Software Heritage data

By default Software Heritage does not compute TLSH hashes for files, so these
have to be computed first. The SHA1 checksums are already known (as the file
name of the file is the SHA1 checksum of the file).

The script `walk_software_heritage_blobs.py` processes the files extracted from 
blobs.tar.zst` and computes `sha256` and `TLSH` hashes, as well as "normalized"
versions where the data is first cleaned up to get rid of excessive whitespace,
different line endings, and so on (which are sometimes the only differences
between files).

The end result is a CSV file that has the following columns:

```
sha1,sha256,tlsh,normalized_sha256,normalized_tlsh
```

This data can later be cross correlated with `swhid` and origins from
`license-blobs.csv.zst` and `blobs-origins.csv.zst`.

## Selecting the right data for the proximity matching server

Depending on your preferences you either might want to select the regular
TLSH, or the "normalized" TLSH. When using the latter, it is recommended
to preprocess every file that is being scanned, before a TLSH hash is being
computed for it. Normalized TLSH hashes generally give better matches than
not-normalized hashes.

Selecting the right column can be done with a simple `grep` command:

```
$ cut -f 3 -d , /path/to.csv | tail -n +2 > /path/to/output
```

or (for the normalized TLSH hashes):

```
$ cut -f 5 -d , /path/to.csv | tail -n +2 > /path/to/output
```

## Converting the data to a pickle

The output then needs to be converted to a `.pickle` file using the script
`create_vpt_pickle.py`:

```
```

## Loading the pickle into the server and starting the server


After starting the server queries can be sent to it.

# Example

Open the Python console, load a file, compute the TLSH hash

```
>>> import tlsh
>>> a = open('/tmp/LICENSE', 'rb').read()
>>> b = a.split()
>>> c = b" ".join(b)
>>> tlsh.hash(c)
'T1D011461E72610773289613A055656CC5F26FB15F7AAF1684146DF284133746CD1FF844'
```

The last line is the TLSH hash, which you can and paste it into your web browser:

<http://127.0.0.1:5000/tlsh/T1D011461E72610773289613A055656CC5F26FB15F7AAF1684146DF284133746CD1FF844>

As in this case this particular hash is already known in the data the TLSH
distance will be 0 and the returned JSON will look like this:

```
{"distance":0,"match":true,"tlsh":"T1D011461E72610773289613A055656CC5F26FB15F7AAF1684146DF284133746CD1FF844"}
```

# Statistics

Some statistics about the data, memory use, and so on. The Python pickle of
the normalized TLSH hashes is a bit less than 500 MiB on disk:

```
$ ls -lh licenses-tlsh.pickle
-rw-rw-r-- 1 armijn armijn 479M Feb 20 15:11 licenses-tlsh.pickle
```

and contains 5,184,281 unique TLSH hashes.

When loaded into the server, the server takes around 3 GiB of memory:

```
  20303 armijn    20   0 3241960   3.0g  10548 S   0.0   9.6   0:19.13 .flask-wrapped
```

(output taken from `top`).

Querying the server and getting a result takes around 0.6 seconds or less.
