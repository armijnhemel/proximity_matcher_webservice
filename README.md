# Webservice for proximity matching using TLSH and Vantage Point Trees 

This repository contains a proof of concept webservice for proximity matching
to quickly find the closest match for a file in a collection of known files.

One use case could be to find the closest match for an open source license
text in a collection of known license texts (as license texts tend to very
slightly), or to find a file in collection of known files, for example files
that have already been vetted or cleared by an open source software compliance
team or security audit team.

## TLSH and exact matches

## Vantage Point Trees, HAC-T and other related work

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
python3 create_vpt_pickle.py -i /tmp/tlsh-hashes.txt -o /tmp/licenses-tlsh.pickle
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

* <http://tlsh.org/>
