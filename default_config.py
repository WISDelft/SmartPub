## folder config. Please take care that each path string ends with a /
folder_dblp_xml = './data/'
folder_content_xml = './data/content_xml/'
folder_pdf = './data/pdf/'
folder_log = './data/logs/'
folder_datasets = './data/datasets/'
folder_classifiers = './data/classifiers/'

## mongoDB
mongoDB_IP = '127.0.0.1'
mongoDB_Port = 27017  # default local port. change this if you use SSH tunneling on your machine (likely 4321 or 27017).
mongoDB_db = 'pub'

## pdf extraction
grobid_url = '127.0.0.1:8080'


## conferences we like
booktitles = ['JCDL','SIGIR','ECDL','TPDL','TREC', 'ICWSM', 'ESWC', 'ICSR','WWW', 'ICSE', 'HRI', 'VLDB', 'ICRA', 'ICARCV']


## journals we like
journals = ['IEEE Trans. Robotics' , 'IEEE Trans. Robotics and Automation', 'IEEE J. Robotics and Automation']


## Update process (for later use)
update = True

####################### XML processing configurations #######################

# set to true if you want to persist to a local mongo DB (default connection)
storeToMongo = True

# set to true if you want to skip downloading EE entries (pdf URLs) which have been accessed before (either sucessfully or unsucessfully)
# this only works if storeToMongo is set to True because the MongoDB must be accessed for that. (if you set storeToMongo to false, I will
# just assume that MongoDB is simply not active / there
skipPreviouslyAccessedURLs = True

# the categories you are interested in
CATEGORIES = {'article', 'inproceedings', 'proceedings', 'book', 'incollection', 'phdthesis', 'mastersthesis', 'www'}

# the categories you are NOT interested in
SKIP_CATEGORIES = {'phdthesis', 'mastersthesis', 'www', 'proceedings'}

# the fields which should be in your each data item / mongo entry
DATA_ITEMS = ["title", "booktitle", "year", "journal", "crossref", "ee"]

statusEveryXdownloads = 100
statusEveryXxmlLoops = 1000

###############################################################################
