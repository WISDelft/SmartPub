import urllib
import feedparser
import rdflib
import ngram_analysis
import topic_extractor
import nltk

"""
queryParameter: query papers based on a parameter--> e.g instagram + twitter
max_results: max number of papers
"""
def arxiv_crawler(queryParameter, max_results):

    introctions_list=[]
    datasets_list=[]
    methods_list = []
    search_query = 'all:'+queryParameter
    start = 0

    base_url = 'http://export.arxiv.org/api/query?';
    query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                         start,
                                                         max_results)

    # Opensearch metadata such as totalResults, startIndex,
    # and itemsPerPage live in the opensearch namespase.
    # Some entry metadata lives in the arXiv namespace.
    # This is a hack to expose both of these namespaces in
    # feedparser v4.1
    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

    # perform a GET request using the base_url and query
    response = urllib.urlopen(base_url+query).read()

    # change author -> contributors (because contributors is a list)
    response = response.replace('author','contributor')

    # parse the response using feedparser
    feed = feedparser.parse(response)

    # print out feed information
    print 'Feed title: %s' % feed.feed.title
    print 'Feed last updated: %s' % feed.feed.updated

    # print opensearch metadata
    print 'totalResults for this query: %s' % feed.feed.opensearch_totalresults
    print 'itemsPerPage for this query: %s' % feed.feed.opensearch_itemsperpage
    print 'startIndex for this query: %s'   % feed.feed.opensearch_startindex

    # Run through each entry, and print out information
    for entry in feed.entries:
     #   print 'e-print metadata'
        print 'arxiv-id: %s' % entry.id.split('/abs/')[-1]
        print 'Published: %s' % entry.published
        print 'Title:  %s' % entry.title

        print 'Authors:  %s' % ','.join(author.name for author in entry.contributors)
        arxiv_id=entry.id.split('/abs/')[-1]
        Published=entry.published
        Title=entry.title

        Authors=','.join(author.name for author in entry.contributors)

        # get the links to the abs page and pdf for this e-print
        for link in entry.links:
            if link.rel == 'alternate':
                print 'abs page link: %s' % link.href
            elif link.title == 'pdf':
                print 'pdf link: %s' % link.href
                
        # The journal reference, comments and primary_category sections live under
        # the arxiv namespace
        try:
            journal_ref = entry.arxiv_journal_ref
        except AttributeError:
            journal_ref = 'No journal ref found'
        print 'Journal reference: %s' % journal_ref

        try:
            comment = entry.arxiv_comment
        except AttributeError:
            comment = 'No comment found'
        print 'Comments: %s' % comment


        print 'Primary Category: %s' % entry.tags[0]['term']

        # Lets get all the categories
        all_categories = [t['term'] for t in entry.tags]
        print 'All Categories: %s' % (', ').join(all_categories)

        # The abstract is in the <summary> element
        print 'Abstract: %s' %  entry.summary
        

arxiv_crawler('ICWSM', 100)

