import requests  # for making HTTP requests
from bs4 import BeautifulSoup  # for parsing HTML
import sqlite3  # integrating a database for storing all scraped PDF links

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

# Database Operations
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

# Fetching & Parsing
# Script will navigate through all the pages, find the PDF links, and save them to a list
# Set the base URL and total number of pages
base_url = 'https://www.theccc.org.uk/publications'
total_pages = 33

# The Main Logic to orchestrate scraping
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

def fetch_content(url):
    """Fetches content from the given URL and returns the BeautifulSoup object."""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

def extract_publication_links(soup):
    """Parses the soup object to extract publication links."""
    return [a['href'] for a in soup.find_all('a', href=True) if 'publication/' in a['href']]

def extract_pdf_links(soup):
    """Parses the soup object to extract PDF links."""
    return [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]

def get_publication_links(page_url):
    """Fetch content and extract publication links."""
    soup = fetch_content(page_url)
    return extract_publication_links(soup)

def get_pdf_links(publication_url):
    """Fetch content and extract PDF links."""
    soup = fetch_content(publication_url)
    return extract_pdf_links(soup)

def main():
    # Execution of the scraping process
    all_pdf_links = collect_all_pdf_links(base_url, total_pages)

    # Deduplicate the links
    all_pdf_links = list(set(all_pdf_links))

    print(all_pdf_links[:10])  # First 10 links

if __name__ == "__main__":
    main()
    conn.close()  # Close the database connection