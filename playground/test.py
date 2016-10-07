import dblp_xml_processing


url="http://doi.acxxxm.org/10.1145/2911451.2911492"
# url="http://dblp.uni-trier.de/db/conf/sigir/index.html"
print(dblp_xml_processing.extract_paper_from_ACM(url, "acm.pdf"))