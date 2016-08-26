# other things to consider:
# tabula: for extracting tables
# grobid: THAT is what we need. SERIOUSLY! https://github.com/kermitt2/grobid https://grobid.readthedocs.io/en/latest/Introduction/






filename = "./data/pdf/journals_pvldb_SelkeLB12.pdf"


def extract_pdfx():
    import pdfx
    pdf = pdfx.PDFx(filename)
    metadata = pdf.get_metadata()
    references_list = pdf.get_references()
    references_dict = pdf.get_references_as_dict()
    text=pdf.get_text()
    print(text)


def extract_pdfminer():
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from io import StringIO
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(filename, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    text = retstr.getvalue()
    retstr.close()
    print(text)


def main():
    # extract_pdfx()
    extract_pdfminer()


if __name__ == '__main__':
    main()