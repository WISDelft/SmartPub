## INSPIRED BY https://github.com/ppwwyyxx/SoPaper

import logging
from urllib.parse import urlparse
import tools
import requests

HOSTNAME = 'dl.acm.org'
DEFAULT_TIMEOUT = '300.0'   # 5 minutes
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'

def download(url):
    # tools.downloadFileWithProgress(downloadinfo['url'], barlength = 0, overwrite = False, folder = cfg.folder_pdf, localfilename=filename, incrementPercentage=0, incrementKB=0)
    logging.info("Custom Directly Download with URL {0} ...".format(url))
    headers = {'Host': urlparse(url).netloc,
               'User-Agent': USER_AGENT,
               'Connection': 'Keep-Alive'
              }

    resp = requests.get(url, headers=headers, allow_redirects=False)
    pdfurl = resp.headers.get('location')
    if pdfurl:
        headers['Host'] = urlparse(pdfurl).netloc
        return tools.downloadFileWithProgress(url, barlength = 0, overwrite = True, folder = ".", localfilename="x.pdf", incrementPercentage=0, incrementKB=0, headers=headers)
    else:
        return tools.downloadFileWithProgress(url, barlength = 0, overwrite = True, folder = ".", localfilename="x.pdf", incrementPercentage=0, incrementKB=0)