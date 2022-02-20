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

To prepare the 

## Starting the server

```
$ export FLASK_APP=proximity_server.py
$ flask run
```

# Links

* <http://tlsh.org/>
