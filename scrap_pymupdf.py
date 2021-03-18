import re
import requests
import io
import fitz
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
        try:
            if url.endswith('.pdf'):
                return url
            else:
                res = requests.get(url)
                pdf_url = re.search(r'(\"https?:\/\/([^\"]*)\.pdf\")', res.text).group(0)
                pdf_url = pdf_url.replace('"', '')
                return pdf_url
        except:
            print("Unable to retrieve the url")
            return None

    # Returns a byte-stream file version of the pdf and passes it to the pdf reader
    def open_pdf_as_IO(self, pdf_url):
        try:
            res_pdf = requests.get(pdf_url)
            file_io = io.BytesIO(res_pdf.content)
            reader = fitz.Document(stream=file_io, filetype="pdf")
            return reader
        except:
            return None

    # Returns the first lines in the pdf - should figure out how to transform them in Title, summary, etc
    def return_first_lines(self, file):
        try:
            first_page = file.load_page(0)
            first_page_text = first_page.get_text("text")
            lines = first_page_text.splitlines()
            first_line = lines[0]
            second_line = lines[1]
            third_line = lines[2]
            fourth_line = lines[3]
            return first_line, second_line, third_line, fourth_line
        except:
            return None

    # If there's a grabbable img in the first page, will return it, else will return an custom pdf icon
    def return_img(self, file):
        first_page = file.load_page(0)
        try:
            img = first_page.get_pixmap()
        except:
            img = Image.open(
                "pdf_img.png")  # Return a default image of a pdf if there is no usable img on the first page
        return img

    # Returns number of pdf pages
    def return_pages(self, file):
        try:
            n_pages = file.page_count
        except:
            n_pages = None
        return n_pages

    # Returns n° of word in pdf using bytes stream
    def return_words(self, file):
        try:
            counter = 0
            for p in range(file.page_count):
                page = file.load_page(p)
                page_text = page.get_text("text")
                counter += len(page_text.strip().split(" "))
        except:
            counter = None
        return counter


if __name__ == "__main__":

    #
    # test_url = "https://dash.harvard.edu/bitstream/handle/1/3403038/darnton_historybooks.pdf"
    # t0 = time()
    # test_pdf = PDFScraper(test_url)
    # print(test_pdf.img)
    # print(test_pdf.url)
    # print(test_pdf.lines)
    # print(test_pdf.pages)
    # print(test_pdf.words)
    # t1 = time()
    # print(f"time = {t1-t0}")


    test_url = ["https://dash.harvard.edu/bitstream/handle/1/3403038/darnton_historybooks.pdf",
                "http://www.axmag.com/download/pdfurl-guide.pdf",
                "https://www.research.gov/common/attachment/Desktop/How_do_I_create_a_PDF-A_file.pdf",
                "https://library.princeton.edu/special-collections/sites/default/files/Creating_PDFA.pdf",
                "http://www.umass.edu/preferen/gintis/hypercognition.pdf",
                "https://www.researchgate.net/publication/315905287_INTRODUCTION_TO_ANTHROPOLOGY",
                "https://theologicalstudies.org.uk/pdf/anthropology_cameron.pdf",
                "https://www.researchgate.net/publication/327430054_Business_Anthropology",
                "http://ijhssnet.com/journals/Vol_4_No_10_1_August_2014/19.pdf",
                "http://marcuse.faculty.history.ucsb.edu/classes/201/articles/78KelleyPublicHistoryOriginsTPH0001.pdf",
                "https://cbmw.org/wp-content/uploads/2019/05/eikon_1_1_web.pdf"]
    times = []
    for url in test_url:
        t0 = time()
        test_pdf = PDFScraper(url)
        print(test_pdf.img)
        print(test_pdf.url)
        print(test_pdf.lines)
        print(test_pdf.pages)
        print(test_pdf.words)
        t1 = time()
        times.append(t1-t0)
    print(times)


# with pdfplumber: with both words and pages [24.76241636276245, 2.762158155441284, 5.287302494049072, 7.731441974639893, 24.89242386817932, 6.081347703933716, 10.33959150314331, 7.7054407596588135, 9.47854208946228, 17.02997398376465, 33.96194243431091]
# with pymupdf:    with both words and pages [5.303016662597656, 4.170005798339844, 2.7500038146972656, 3.900005578994751, 1.550002098083496, 1.3200018405914307, 0.872002363204956, 1.9300026893615723, 0.7500009536743164, 11.090015649795532, 4.360006093978882]
