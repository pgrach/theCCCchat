import requests # for making HTTP requests
from bs4 import BeautifulSoup # for parsing HTML
import sqlite3 # integrating a database for storing all scraped PDF links


from langchain.document_loaders import PyPDFLoader # to load and split the PDFs into smaller text segments

# For creating Semantic Embeddings
import os
import getpass
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

os.environ['OPENAI_API_KEY'] = getpass.getpass('OpenAI API Key:')


# Connect to SQLite database
conn = sqlite3.connect('links.db')
cursor = conn.cursor()

# Create a table for storing PDF links if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS pdf_links (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE
)
''')

conn.commit()

def store_link_in_db(link):
    """Store a link in the database."""
    try:
        cursor.execute("INSERT INTO pdf_links (url) VALUES (?)", (link,))
        conn.commit()
    except sqlite3.IntegrityError:
        # This link already exists in the database
        pass

def is_link_in_db(link):
    """Check if a link is already in the database."""
    cursor.execute("SELECT 1 FROM pdf_links WHERE url=?", (link,))
    return cursor.fetchone() is not None

# Script will navigate through all the pages, find the PDF links, and save them to a list

# Set the base URL and total number of pages
base_url = 'https://www.theccc.org.uk/publications'
total_pages = 33

# The main function to orchestrate the scraping
def collect_all_pdf_links(base_url, total_pages):
    all_pdf_links = []
    for page_number in range(1, total_pages + 1):
        page_url = f"{base_url}/page/{page_number}/?topic&type=0-report" # Construct the URL for each page

        # Skip the page if it's been scraped before
        if is_link_in_db(page_url):
            print(f"Skipping already scraped page: {page_url}")
            continue

        print(f"Scraping page: {page_url}") # Logging the scrapping process (it takes a while...)

        publication_links = get_publication_links(page_url)
        for publication_url in publication_links:
                # Check if the publication URL has already been scraped
            if not is_link_in_db(publication_url):
                pdf_links = get_pdf_links(publication_url)
                all_pdf_links.extend(pdf_links)
                # Store the new links in the database
                for link in pdf_links:
                    store_link_in_db(link)
            else:
                print(f"Skipping already scraped publication: {publication_url}")
    return all_pdf_links

# Scrape through the main publications pages to collect links to individual publication pages:
def get_publication_links(page_url):
    response = requests.get(page_url) # send GET request to the page URL to retrieve the page content
    response.raise_for_status()  # Check if the request was successful
    soup = BeautifulSoup(response.content, 'html.parser')
    publication_links = [a['href'] for a in soup.find_all('a', href=True) if 'publication/' in a['href']]
    return publication_links

# Visit each publication page to find and collect links to PDFs
def get_pdf_links(publication_url):
    response = requests.get(publication_url)
    response.raise_for_status()  # Check if the request was successful
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
    return pdf_links

# Execution of the scraping process
all_pdf_links = collect_all_pdf_links(base_url, total_pages)

# Deduplicate the links
all_pdf_links = list(set(all_pdf_links))

print(all_pdf_links[:10])  # First 10 links


# Breaking Down PDFs
def process_pdf(pdf_url):
    response = requests.get(pdf_url)
    with open('temp.pdf', 'wb') as temp_pdf_file:
        temp_pdf_file.write(response.content)
    
    loader = PyPDFLoader('temp.pdf')
    pages = loader.load_and_split()


# Creating Semantic Embeddings
def create_embeddings(pages):
    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
    return faiss_index

# Efficient Storage and Retrieval


# Iterating PROCESSING through All PDFs:
cursor.execute("SELECT url FROM pdf_links")
pdf_urls = cursor.fetchall()

for pdf_url in pdf_urls:
    pdf_url = pdf_url[0]  # Extract URL from tuple
    print(f"Processing {pdf_url}")
    process_pdf(pdf_url)