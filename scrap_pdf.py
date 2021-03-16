import re
import requests
import io
import pdfplumber
from PIL import Image
from time import time


class PDFScraper():
    def __init__(self, url):
        self.url = self.get_pdf_url(url)
        self.file_io = self.open_pdf_as_IO(self.url)
        self.lines = self.return_first_lines(self.file_io)
        self.img = self.return_img(self.file_io)
        self.words = self.return_words(self.file_io)
        self.pages = self.return_pages(self.file_io)

    # If the url provided takes directly to the pdf file, that is used as self.url
    # else this method searches for a link to the file and uses that as self.url
    def get_pdf_url(self, url):
        if url.endswith('.pdf'):
            return url
        else:
            res = requests.get(url)
            pdf_url = re.search(r'(\"https?:\/\/([^\"]*)\.pdf\")', res.text).group(0)
            pdf_url = pdf_url.replace('"', '')
            return pdf_url

    # Returns a byte-stream file version of the pdf
    def open_pdf_as_IO(self, pdf_url):
        res_pdf = requests.get(pdf_url)
        file_io = io.BytesIO(res_pdf.content)
        return file_io

    # Returns the first lines in the pdf - should figure out how to transform them in Title, summary, etc
    def return_first_lines(self, file):
        with pdfplumber.open(file) as pdf:
            first_page = pdf.pages[0]
            first_page_text = first_page.extract_text()
            lines = first_page_text.splitlines()
            first_line = lines[0]
            second_line = lines[1]
            third_line = lines[2]
            fourth_line = lines[3]
        return first_line, second_line, third_line, fourth_line

    # If there's a grabbable img in the first page, will return it, else will return an custom pdf icon
    def return_img(self, file):
        with pdfplumber.open(file) as pdf:
            first_page = pdf.pages[0]
            if not first_page.images:
                img = Image.open(
                    "pdf_img.png")  # Return a default image of a pdf if there is no usable img on the first page
            else:
                img = first_page.images[0]
        return img

    # Returns number of pdf pages
    def return_pages(self, file):
        with pdfplumber.open(file) as pdf:
            n_pages = len(pdf.pages)
         return n_pages

    # Returns n° of word in pdf using bytes stream
    def return_words(self, file):
        with pdfplumber.open(file) as pdf:
            counter = 0
            for page in pdf.pages:
                page_text = page.extract_text()
                counter += len(page_text.strip().split(" "))
        return counter


if __name__ == "__main__":
    test_url = ["https://dash.harvard.edu/bitstream/handle/1/3403038/darnton_historybooks.pdf",
                "http://www.axmag.com/download/pdfurl-guide.pdf",
                "https://www.research.gov/common/attachment/Desktop/How_do_I_create_a_PDF-A_file.pdf",
                "https://library.princeton.edu/special-collections/sites/default/files/Creating_PDFA.pdf",
                "http://www.umass.edu/preferen/gintis/hypercognition.pdf",
                "https://www.researchgate.net/publication/315905287_INTRODUCTION_TO_ANTHROPOLOGY",
                "https://theologicalstudies.org.uk/pdf/anthropology_cameron.pdf",
                "https://www.researchgate.net/publication/327430054_Business_Anthropology",
                "http://ijhssnet.com/journals/Vol_4_No_10_1_August_2014/19.pdf",
                "http://marcuse.faculty.history.ucsb.edu/classes/201/articles/78KelleyPublicHistoryOriginsTPH0001.pdf"]
    t0 = time()
    for url in test_url:
        try:
            test_pdf = PDFScraper(url)
            print(test_pdf.img)
            print(test_pdf.url)
            print(test_pdf.lines)
            print(test_pdf.pages)
        except:
            print(f"unable to retrieve {url}")
    t1 = time()
    print(f"it took {t1 - t0} secs")


# counting words: used 10 random PDFs; some with 500 words, others with 10000+. It took 109 secs
# counting pages: used 10 random PDFs. It took 45 secs
# counting neither pages nor words, using the same 10 random PDFs, took 42 secs