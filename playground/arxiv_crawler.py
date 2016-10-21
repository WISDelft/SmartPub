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
                Introduction=ngram_analysis.get_section(link.href, "INTRODUCTION")
                sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
                intro_sent = (sent_detector.tokenize(Introduction.strip()))
                for intro in intro_sent:
                    introctions_list.append(intro)

                """
                for each section of the paper perform n-gram analysis
                """
                #ngram_analysis.get_2grams(Introduction,'introduction')
                #ngram_analysis.get_3grams(Introduction, 'introduction')
                #footnotes=ngram_analysis.get_Links(link.href)
                #ngram_analysis.get_2grams(footnotes, 'footnotes')
                #fig_table=ngram_analysis.get_fig_table(link.href)
                #ngram_analysis.get_2grams(fig_table, 'fig_table')
                #ngram_analysis.get_3grams(footnotes, 'footnotes')
                #ngram_analysis.get_3grams(fig_table, 'fig_table')

                method = ngram_analysis.get_section(link.href, "METHOD")
                if method:

                    method_sent = (sent_detector.tokenize(method.strip()))
                    for intro in method_sent:
                        methods_list.append(intro)
                #    ngram_analysis.get_2grams(method, 'method')
                #    ngram_analysis.get_3grams(method, 'method')


                dataset= ngram_analysis.get_section(link.href, "DATASET")
                if dataset:

                    dataset_sent = (sent_detector.tokenize(dataset.strip()))
                    for intro in dataset_sent:
                        datasets_list.append(intro)
                #    ngram_analysis.get_2grams(dataset, 'dataset')
                #    ngram_analysis.get_3grams(dataset, 'dataset')


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
        #ngram_analysis.get_2grams(entry.summary, 'abstract')
        #ngram_analysis.get_3grams(entry.summary, 'abstract')

    #topic_extractor.get_topic(entry.summary, 2,'abstract')
    #topic_extractor.get_topic(introctions_list, 2, 'introduction')
    #topic_extractor.get_topic(datasets_list, 2, 'dataset')
    #topic_extractor.get_topic(methods_list, 2, 'method')




