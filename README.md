# SmartPub
Processing pipeline for smart metadata extraction from full-text publications.

You will need Python 3 for this (maybe it works with Python 2... did not test it yet), and the required packages are listed in requirements.txt.
Currently, it will download and process files into the "data" subfolder of this directory.

# Preparation
- Likely, you do not want to install all the following things on your machine. Probably you want to skip to the next section...
- You need a local installation of MongoDB. Currently, there is no support for user mangement, so make sure that your Mongo is not open to the whole internet
- For PDF processing, you need grobid installed. Grobid is a rather heavy collection of tools, and the easiest way to get it up and running as as follows:
    - Install Docker
    - run ```docker pull lfoppiano/grobid:0.4.1-SNAPSHOT``` to install the Docker version of grobid
    - start grobid via ```docker run -t --rm -p 8080:8080 lfoppiano/grobid:0.4.1-SNAPSHOT```
    - test if it works by going to http://localhost:8080
 - Create your own config file (see below)   
 
# Using data hosted on SERVsara
- If you want to access the MongoDB on SERVsara, you need to create an SSH tunnel first. This can be easily done by ```ssh -L 4321:localhost:27017 ubuntu@SERVSara_IP```. Then, you can access MongoDB on ```localhost:4321``` from your local machine. 
You will need to register your public RSA key first! (ask Christoph) The name of the database is ```pub```.
- Check ```access_fulltexts.py``` to see how to access stuff from MongoDB
    - I also like Mongoclient (http://www.mongoclient.com/) for fiddeling around with data 
- The schema of the publication entries (collection "publication") is as follows:

```javascript
{ // note that if a data key could not be parsed or is not available, that key is not used 
    "_id" : "..."                   // internal MongoDB id, identical to DBLP_ID
    "dblpkey" : "..."               // key as used in dblp, with '/' replaces with '_'
    "title": "..."                  // title of the publication
    "type" : "..."                  // type of the publication. Right now, we only crawl 'article', 'inproceedings', 'book', and 'incollection'
    "journal" : "..."               // name of the jounral if an article
    "book" : "..."                  // name of the book if book, or name of conference if inproceedings or incollection
    "year" : "..."                  // year of publication
    "authors" : {"...", "..."}      // list of author strings as used in DBLP (e.g., names only with numbering in case of dublicates)
    "ee" : "..."                    // link to a potential PDF. Note: In the MongoDB, we ONLY have papers for which this link was valid. All papers with invalid links or DOIs behind paywalls are discarded!
    "content" :
    { // note that the stuff in content is probabilistically extracted from the PDF. It will not always be correct. Also, there is more information available currently not in mongoDB, as e.g., chapter structure or tables & figures
        "abstract" : "..."          // plain text abstract as string
        "fulltext" : "..."          // plain text fulltext as string, with all additional info / tags stripped
        "notes" : {"...", "..."}    // list of footnotes (or other types of notes) as plain strings
        "keywords" : {"...", "..."} // list of author-provided keywords as plain strings
        "references" :              // list of references
        {
            "ref_title" : "..."     // name of the reference
            "authors"   : "..."     // list of author names of the reference (these are not DBLP authors, but text extracted from the PDF)
            "journal_pubnote" :     // detailed metadata on the reference if available
            {
                "in" : "..."        // name of the journal or conference
                "journal_volume" : "..." 
                "journal_issue" : "..." 
                "year" : "..." 
                "page_range": "..." 
            }
        }
    }
}
```

# Quick Overview of relevant files:

- **config_default.py**: Default config file. Copy this file, and rename it ```config.py```, and change it in order to have your own configuration. 
One thing you might want to change is for example the MongoDB port to 4321 if you use the remote Mongo instance on SURFsara. 

- **config.py**: This file should not exist, and you create it yourself as described above. Don't check the new ```config.py``` into GitHub... Put it into your ```.gitignore```

- **dblp_xml-processing.py**: This will download the full XML file from DBLP, scan through it, find all PDF links, and tries to download the respective papers. 
If a paper could be downloaded, an entry with limited metadata (title, authors, journal/conference, year) will be stored in a local MongoDB database named "pub", in a collection named "publications".
It also logs each attempt of downloading something in a collection called "downloads". By default, you can simple start this file, and it will skip all papers / downloads it has tried before, therefore it is suitable
for incrementally building a library. Use ```nohup python dblp_xml_processing.py &``` to run this on the server. You likely do not want to run this on your own machine.

- **pdf_text_extractor.py**: Work in progress. You can specify a MongoDB search string, and then it tries to extract content from all papers which match that search. 
Grobid needs to be installed and running on the machine in order for this to work. As grobid is rather slow, the resulting TEI XML will be cached. Then, the script extracts relevant content from the TEI and 
stores it back into the MongoDB entry of the publication (currently, that will be the abstract and a stripped version of the fulltext). Note that currently, the script seems to support only UTF-8 characters. Weird UTF-16-only characters
gets lost during extraction. se ```nohup python pdf_text_extractor.py &``` to run this on the server. You likely do not want to run this on your own machine.

- **access_fulltexts.py**: Simple example script for demonstrating how you can access the fulltexts via MongoDB and the aforementioned SSH tunnel from the SURFsara server (assuming you configured ````config.py```correctly)

- **show_statistics.py**: Print a small set of statistics about the data (number of PDFs, number of failed links, etc.)


- all things named test* or *.ipynb: You can ignore these files. I use them for experimenting with code and libraries, and they will likely be cleaned later.


- **pyhelpers/**: Folder containing some helper methods, as e.g., a downloading function and similar things.
- **oldstuff/**: Old code I did not yet want to discard...

