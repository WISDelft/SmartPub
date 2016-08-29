# SmartPub
Processing pipeline for smart metadata extraction from full-text publications.

You will need Python 3 for this (maybe it works with Python 2... did not test it yet), and the required packages are listed in requirements.txt.
Currently, it will download and process files into the "data" subfolder of this directory.

# Preparation
- You need a local installation of MongoDB. Currently, there is no support for user mangement, so make sure that your Mongo is not open to the whole internet
- For PDF processing, you need grobid installed. Grobid is a rather heavy collection of tools, and the easiest way to get it up and running as as follows:
    - Install Docker
    - run ```docker pull lfoppiano/grobid:0.4.1-SNAPSHOT``` to install the Docker version of grobid
    - start grobid via ```docker run -t --rm -p 8080:8080 lfoppiano/grobid:0.4.1-SNAPSHOT```
    - test if it works by going to http://localhost:8080

# Quick Overview of relevant files:

- **dblp_xml-processing.py**: This will download the full XML file from DBLP, scan through it, find all PDF links, and tries to download the respective papers. 
If a paper could be downloaded, an entry with limited metadata (title, authors, journal/conference, year) will be stored in a local MongoDB database named "pub", in a collection named ""publications".
It also logs each attempt of downloading something in a collection called "downloads". By default, you can simple start this file, and it will skip all papers / downloads it has tried before, therefore it is suitable
for incrementally building a library. 
- **pdf_text_extractor.py**: Work in progress. You can specify a MongoDB search string, and then it tries to extract content from all papers which match that search. 
Grobid needs to be installed and running on the machine in order for this to work. As grobid is rather slow, the resulting TEI XML will be cached. Then, the script extracts relevant content from the TEI and 
stores it back into the MongoDB entry of the publication (currently, that will be the abstract and a stripped version of the fulltext). Note that currently, the script seems to support only UTF-8 characters. Weird UTF-16-only characters
gets lost during extration.
- **tools.py**: This contains some helper methods, as e.g., a downloading function and similar things.
- **config.py**: Config file. Right now, there is no real need for individual config, so you can simply go with the default. 
- all things named test* or *.ipynb: You can ignore these files. I use them for experimenting with code and libraries, and they will likely be cleaned later.


