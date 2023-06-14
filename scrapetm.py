import os
import csv
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

class BookScraper:
    def __init__(self, download_folder="books", csv_filename="book_info.csv"):
        self.download_folder = download_folder
        self.csv_filename = csv_filename

    def get_book_info(self, url):
        try:
          response = requests.get(url)
          soup = BeautifulSoup(response.text, 'html.parser')
        except:
          pass

        try:
            title = soup.find('h1', itemprop='name').text.strip()
        except:
            title = None

        try:
            author = soup.find('td', text='Awtor:').find_next('td').text.strip()
        except:
            author = None

        try:
            year = soup.find('div', itemprop='datePublished').text.strip()
        except:
            year = None

        try:
            category = soup.find('td', text='Bölüm:').find_next('td').text.strip()
        except:
            category = None

        try:
            format = soup.find('td', text='Formaty:').find_next('td').text.strip()
        except:
            format = None

        try:
            tags = soup.find('td', text='Tags:').find_next('td').text.strip()
        except:
            tags = None

        try:
            pdf_link_tag = soup.find('a', {'class': 'download-link'})
            pdf_link = f"{url.rsplit('/', 2)[0]}{pdf_link_tag['href']}" if pdf_link_tag else None
        except:
            pdf_link = None

        pdf_filename = None
        if pdf_link:
            pdf_filename = f"{title}_{author}_{year}_{category}.{format}"
            self.download_pdf(pdf_link, pdf_filename)

        return {
            'Title': title,
            'Author': author,
            'Year': year,
            'Category': category,
            'Format': format,
            'Tags': tags,
            'PDF Filename': pdf_filename
        }

    def download_pdf(self, pdf_url, filename):
        response = requests.get(pdf_url)
        filepath = os.path.join(self.download_folder, filename)

        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        with open(filepath, 'wb') as f:
            f.write(response.content)

        return filepath

    def save_book_info_to_csv(self, book_info):
        file_exists = os.path.isfile(self.csv_filename)

        with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Author', 'Year', 'Category', 'Format', 'Tags', 'PDF Filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(book_info)



book_scraper = BookScraper()

# books from 1 to 2666
for i in tqdm(range(1, 2667)):
    url = "https://www.kitaphana.net/book/" + str(i)
    book_info = book_scraper.get_book_info(url)
    book_scraper.save_book_info_to_csv(book_info)
