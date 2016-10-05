from pyhelpers import tools
from html.parser import HTMLParser
import json
import requests


tools.downloadFileWithProgress('http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=5089263', incrementKB=10 * 1024, localfilename="1.pdf", overwrite=False)
tools.downloadFileWithProgress('http://dl.acm.org/ft_gateway.cfm?id=2964799&ftid=1751125&dwn=1&CFID=847673629&CFTOKEN=22464829', localfilename="2.pdf", incrementKB=10 * 1024, overwrite=False)

class PageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.doc = {'references':[], 'citedby':[]}
        self.section = None

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            d = dict(attrs)
            if 'name' in d and d['name'].startswith('citation_'):
                name = d['name'][9:]
                content = d['content']
                self.doc[name] = content
        elif tag == 'a':
            d = dict(attrs)
            if 'name' in d:
                name = d['name']
                self.section = name if name in ['references', 'citedby'] else None
            if self.section is not None and 'href' in d and d['href'].startswith('citation.cfm?'):
                query = d['href'][13:]
                for p in query.split('&'):
                    a = p.split('=')
                    if a[0] == 'id':
                        self.doc[self.section].append(a[1])


cookies = {}
def download_doc(uid):
    global cookies
    url = 'http://dl.acm.org/citation.cfm?id=' + uid + '&preflayout=flat'
    r = requests.get(url, cookies = cookies, headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36'})
    cookies.update(r.cookies)
    parser = PageParser()
    parser.feed(r.text)
    return parser.doc



#uid = '2387905'
# docs = download_doc(uid)