# Webservice for proximity matching using TLSH and Vantage Point Trees 

This repository contains a proof of concept webservice for proximity matching
to quickly find the closest match for a file in a collection of known files.

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

It is easy to when having a TLSH has to compare it to a list of TLSH hashes
sequentially, but as more hashes are added it becomes more and more expensive
to do. Researchers at Trendmicro bumped into the same problem and wanted to
fix this. As malware is continuously morphing to evade detection using regular
hashes TLSH is used to find close matches to known malware. To do efficient
hashes they use an algorithm named "HAC-T"[2], which is based on Vantage
Point Trees and clustering. Vantage Point Trees with TLSH allow much quicker
lookups than by using a regular list.

Because for me there was no need for clustering (which requires labeling
files) only a modified version of the Vantage Point Tree part of HAC-T was
used. The modifications are:

* removing dead code
* inlining code for performance
* pickling support
* cleanups to make things more Python and less C++

The original code can be found in the TLSH Github repository in the
directory `tlshCluster`.

# Running the proximity matching server

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

## Starting the server

Note: currently the location of the pickle file is still hardcoded to
`/tmp/licenses-tlsh.pickle`. This will be changed in the future.

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
looking it up in an external database.

# Caveats

The VPT trees are not necessarily balanced. This is because the properties
of the nodes and subtrees are not transitive.

Because the VPT is a recursive data structure stored in a pickle it could
mean that you get errors like this:

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
webservice is started

# Links

1. <http://tlsh.org/>
2. <http://tlsh.org/papers.html>
