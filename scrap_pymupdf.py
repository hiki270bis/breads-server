import re, io, sys, json
import requests
import fitz
from PIL import Image
from time import time


class PDFScraper():
    def __init__(self, url):
        self.url = self.get_pdf_url(url)
        self.file_io = self.open_pdf_as_IO(self.url)
        self.lines = self.return_first_lines(self.file_io)
        #    self.img = self.return_img(self.file_io)
        self.img = ""
        self.words = self.return_words(self.file_io)
        self.pages = self.return_pages(self.file_io)
        self.domain = self.get_domain(self.url)

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

    # Returns the first lines in the pdf
    # Uses RegEx to rule out lines which don't describe the article
    def return_first_lines(self, file):
        try:
            first_page = file.load_page(0)
            first_page_text = first_page.get_text("text")
            lines = []
            date_regex = re.compile(
                r'(([0-9]{2})?(\/|-|(\s)*)?)([0-9]{2}|january|february|march|april|may|june|july|august|september|november|december)(\/|-|(\s)*)([0-9]{2,4})',
                re.IGNORECASE)
            invalid_regex = re.compile(r'^[\W\d]*$')
            pages_regex = re.compile(r'page[\s]*[\d]{1,2}', re.IGNORECASE)
            hour_regex = re.compile(r'[\d]{1,2}:[\d]{2}')
            too_short_regex = re.compile(r'[\w]{4,}')
            url_regex = re.compile(
                r'(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])')
            copyright = re.compile('copyright|journal', re.IGNORECASE)
            for line in first_page_text.splitlines():
                if line != "" and re.fullmatch(invalid_regex, line) is None \
                        and re.search(date_regex, line) is None \
                        and re.search(copyright, line) is None \
                        and re.search(url_regex, line) is None \
                        and re.search(pages_regex, line) is None \
                        and re.search(hour_regex, line) is None \
                        and re.search(too_short_regex, line) is not None:
                    lines.append(line)
            return lines
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

    # Returns domain
    def get_domain(self, url):
        try:
            domain = re.search(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]', url)
            domain = domain.group()
        except:
            domain = 'Unable to get domain'

        return domain


if __name__ == "__main__":

    # base_url = 'https://dash.harvard.edu/bitstream/handle/1/3403038/darnton_historybooks.pdf'

    base_url = sys.argv[1]

    # I don't think cache is useful when scraping pdf(?)
    # cached = 'https://webcache.googleusercontent.com/search?q=cache:' + BASE_URL

    try:
        pdf_site = PDFScraper(base_url)
    except:
        pass

    title = pdf_site.lines[0]
    domain = pdf_site.domain
    description = pdf_site.lines[1:]
    image = pdf_site.img
    word_count = pdf_site.words
    BASE_URL = pdf_site.url

    values = [
        title,
        domain,
        description,
        image,
        word_count,
        BASE_URL,
    ]

    # print to send data to node.js
    print(json.dumps(values))
