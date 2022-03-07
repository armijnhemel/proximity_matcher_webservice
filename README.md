# Webservice for proximity matching using TLSH and Vantage Point Trees 

This repository contains a proof of concept webservice for proximity matching
to quickly find the closest match for a hash in a collection of known hash.

One use case could be to find the closest match for an open source license
text in a collection of known license texts (as license texts tend to very
slightly), or to find a file in collection of known files, for example files
that have already been vetted or cleared by an open source software compliance
team or security audit team.

This tool should not be used in production as is but should serve as an
example of how to do these things.

## TLSH and exact matches

TLSH stands for "Trendmicro Locality Sensitive Hash" and, as the name implies,
it is a locality sensitive hash (LSH). Whereas regular cryptographic hashes
such as MD5 or SHA256 were designed in such a way that changing a single
byte would result in vastly different hashes (barring some edge cases) TLSH
was designed in such a way that similar files generate similar hashes, making
it possible to compute a distance between the two hashes (and thus files).

With regular cryptographic hashes it is only possible to answer the question
"are these two files identical?" but with TLSH it is possible to answer the
question "how close are these two files?" as well.

When combining these two approaches a few questions become much clearer to
answer, such as "how close is my source code tree to upstream?", or "is there
a maintenance risk?", and so on.

As TLSH is signficantly slower than MD5, SHA1 or SHA256 usually it makes
sense to first filter using normal hashes and when there is no match use
TLSH.

## Vantage Point Trees, HAC-T and other related work

It is easy when having a TLSH to compare it to a list of TLSH hashes
sequentially, but as more hashes are added it becomes more and more expensive
to do. Researchers at Trendmicro bumped into the same problem and wanted to
fix this. As malware is continuously morphing to evade detection using regular
hashes TLSH is used to find close matches to known malware. To do efficient
lookups and correctly label malware they use an algorithm named "HAC-T"[2],
which is based on Vantage Point Trees and clustering. Vantage Point Trees
with TLSH allow much quicker lookups than using a regular list[3].

Because for me there was no need for clustering (which requires labeling
files) only a modified version of the Vantage Point Tree part of HAC-T is
used here. The modifications are:

* removing dead code
* inlining code for performance
* pickling support
* cleanups to make things more Python and less C++

The original code can be found in the TLSH Github repository in the
directory `tlshCluster`.

# Running the proximity matching server

## Requirements

To run the proximity matching server you need a recent Python 3, plus a few
external packages:

* `click`
* `flask`
* `gevent`
* `gunicorn`
* `requests`
* `tlsh`

Be warned: some of these might be called different on different distributions.
Also, some distributions ship old versions of `tlsh`. In case you are using
the Nix package manager there is also a `shell.nix` file that you can use to
quickly set up your environment.

## Preparing the data set

To prepare the data you need to first have a list of TLSH hashes. This can
be done for example by looking at a directory of files, computing the TLSH
checksums for each file and adding the TLSH checksum to the file. See the
directory `examples` for inspiration.

After you have a file with TLSH hashes run the `create_vpt_pickle.py` tool
to create a vantage point tree and save it to a Python pickle. As creating
the vantage point tree can take some time this is not something that should
be done at startup of the webservice (unless it is the only way, see below).

The `create_vpt_pickle.py` tool can be invoked as follows:

```
$ python3 create_vpt_pickle.py -i /tmp/tlsh-hashes.txt -o /tmp/licenses-tlsh.pickle
```

The data structure uses `__slots__` to squeeze more performance out of the
code. This means that the data structure is static and cannot be changed while
the program is running. If a dataset needs to be changed, it should be
regenerated.

## Starting the server

Note: currently the location of the pickle file is still hardcoded to
`/tmp/licenses-tlsh.pickle`. This will be changed in the future.

### Flask

```
$ export FLASK_APP=proximity_server.py
$ flask run
```

This will launch the webservce, which can then be accessed on the advertised
URL.

There is also an optimized version of the server called
`proximity_server_opt.py` that keeps an additional list of TLSH hashes that
are known in the data set in memory, to be able to very quickly send responses
for already known hashes. Currently the list of the hashes (one TLSH hash per
line) is hardcoded to `/tmp/tlsh-hashes.txt`. This will be changed in the
future. Starting the webservice should be changed accordingly:

```
$ export FLASK_APP=proximity_server_opt.py
$ flask run
```

The optimized version can use significantly more memory. If it is already
possible to filter known hashes before sending the hashes to the webservice
then it is recommended to use the regular version.

### Gunicorn

When using the Gunicorn WSGI server it is easier to use multiple workers.
Please note: right now a complete copy of all the data is kept in memory per
worker. The `--preload` option is to reduce memory usage. Sharing data to
reduce memory further is a TODO.

```
$ gunicorn -w 4 -b 127.0.0.1:5000 --preload proximity_server:app
```

or the optimized version (see documentation above):

```
$ gunicorn -w 4 -b 127.0.0.1:5000 -t 60 --preload proximity_server_opt:app
```

Please note that the optimized server uses the `-t` setting, which indicates
a time out.

If you want to use `keep-alive` connections, you need to add the
`--worker-class gevent` parameter, for example:

```
$ gunicorn -w 8 -b 127.0.0.1:5000 --worker-class gevent --preload proximity_server_opt:app
```

Whether or not this will make performance a lot better depends on your data.

# Interpreting results

The results of the webservice are JSON that is fairly minimal and looks like
this:

```
{'distance': 24, 'match': True, 'tlsh': 'T1D931A61B13441BE75BF2178236AABDC4B08DC02EBB276E01186DF388537B12ED4B7190'}
{'distance': 0, 'match': True, 'tlsh': 'T16082932E774543B206C203916A4F6CCFA32BD478723E11656469C1AD236BE35C3BFAD9'}
{'distance': 0, 'match': True, 'tlsh': 'T13BB2553EA74513B206D202505A0F94DFE32BD07C32678A646499C15D23ABD3593FFBEA'}
{'distance': 0, 'match': True, 'tlsh': 'T1D731658B13481BA756E216D3B266BDC4F15AE02E3B135E02186DE394576B83EC0F7495'}
{'distance': 17, 'match': True, 'tlsh': 'T15231B54702841FA30AE2174231AAAEC0708DC02D3F236E041C7AF244537B42FD9B7081'}
```

Each line is a valid JSON response (as returned by the webserver). The results:

1. `distance`: the TLSH distance. `0` means that there is no difference with a
file known to the webservice.
2. `match`: whether or not there was a match. Right now if a valid TLSH hash
was used as a parameter the result is always `True`. Only if the parameter is
not a valid TLSH hash the result will be `False`. In case thresholds are
implemented (which is the plan) this might be changed.
3. `tlsh`: the TLSH hash of the match found by the webservice.

As the webservice does not include any of the "business logic" but is only used
for finding the closest match this means that the data has to be further
processed for example by cross-correlating with other data. Alternatively the
served could be extended to also return this information, for example by
loading it from an external database or some other resource.

# Caveats

There are some caveats when creating the database.

## Not all files are suitable

There are some files that are not very suitable for this approach, because of
the file format, where the structure of the file either enforces that there is
a lot of similarity, or where compression makes sure that there is very little
or a combination of both.

As an example, PNG files always start with a very similar header (often only
differing a few bytes) which will cause TLSH to say those parts are very
similar, but the payload of the data (the `iDAT` chunks) are zlib-compressed
and compression might lead to vastly different outcomes. Metadata, such as
XMP data (if not compressed) could also lead to strange results.

Examples of other files that are not very suitable are files with a lot of
markup or that are generated, sich as SVG files or Visual Studio build files.

## Unbalanced trees

Although the VPT trees try to be balanced they are not necessarily. Because the
VPT is a recursive data structure stored in a pickle it could mean that you get
errors like the following:

```
Traceback (most recent call last):
  File "/home/armijn/git/proximity_matcher_webservice/src/create_vpt_pickle.py", line 34, in <module>
    vpt.pickle_tree(root, pickle_file)
  File "/home/armijn/git/proximity_matcher_webservice/src/vpt/__init__.py", line 111, in pickle_tree
    pickle.dump(root, pickle_file)
RecursionError: maximum recursion depth exceeded while calling a Python object
```

This is observed when for example first sorting the TLSH hashes. Some proposed
solutions:

1. do not sort the TLSH hashes
2. use less data
3. do not use a pickle, but recreate the vantage point tree whenever the
webservice is started. This might be expensive (several minutes) if a lot of data
is involved.
4. do not include useless data where there will not be a useful match such as
graphics files
5. partition the data and use multiple instances of the webservice. A good
partitioning could for example be by programming language, or extension.
6. raise the recursion limit (currently already raised to `1000` above the
system default)

# Comparison to snippet matching

Although the proximity matching method seems like what snippet scanners do
there are some very clear differences:

1. the method used here works on whole files only, whereas snippet scans work
by searching for snippets (hence the name) of known files
2. the result is a (shortest) distance to a known file in a set of files,
while the result of snippet scanners is a match with for example a percentage
("files A and B match for 97%") and line numbers or byte ranges where the
files match.
3. proximity matching code will not be easily/reliably able to detect reuse of
small pieces of code.

Snippet scanning and proximity matching each have their own uses and can be
used to solve different problems. They complement each other but should *not*
be used in place of each other.

# Links

1. <http://tlsh.org/> - official TLSH website
2. <http://tlsh.org/papers.html> - papers describing HAC-T and vantage point trees
3. <https://www.youtube.com/watch?v=wMt0mVkhRA0> - explanation of TLSH and vantage point trees (first 13 minutes)
