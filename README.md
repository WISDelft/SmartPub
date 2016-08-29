# SmartPub
Processing pipeline for smart metadata extraction from full-text publications.

You will need Python 3 for this (maybe it works with Python 2... did not test it yet), and the required packages are listed in requirements.txt.
Currently, it will download and process files into the "data" subfolder of this directory.

# Preparation
- You need a local installation of MongoDB. Currently, there is no support for user mangement, so make sure that your Mongo is not open to the whole internet
- For PDF processing, you need grobid installed. Grobid is a rather heavy collection of tools, and the easiest way to get it up and running as as follows:
-- Install Docker
-- run ```docker pull lfoppiano/grobid:0.4.1-SNAPSHOT``` to install the Docker version of grobid
-- start grobid via ```docker run -t --rm -p 8080:8080 lfoppiano/grobid:0.4.1-SNAPSHOT```
-- test if it works by going to http://localhost:8080

# Quick Overview of relevant files:

- **dblp_xml-processing.py**: This will download the full XML file from DBLP, scan through it, find all PDF links, and tries to download the respective paper. 
If a paper could be downloaded, an entry with limited metadata (title, authors, journal/conference, year) will be stored in a local MongoDB database named "pub", in a collection named ""publications".
It also logs each attempt of downloading something in a collection called "downloads". By default, you can simple start this file, and it will skip all papers / downloads it has tried before, therefore it is suitable
for incrementally building a library. 
- **tools.py**: This contains some helper methods, as e.g., a downloading function and similar things.
- all things named test* or *.ipynb: You can ignore these files. I use them for experimenting with code and libraries, and they will likely be cleaned later.


