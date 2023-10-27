import requests
import sqlite3
from tqdm import tqdm  # Import tqdm for progress bar
import matplotlib.pyplot as plt  # Import Matplotlib for plotting
from concurrent.futures import ThreadPoolExecutor # to execute calls asynchronously allowing higher speed


# Connect to links.db database in order to store faulty links in a separate table
conn = sqlite3.connect('links.db')
cursor = conn.cursor()

def get_pdf_size(url):
    try:
        # HEAD request to get the headers without downloading the PDF
        response = requests.head(url, timeout=10)
        response.raise_for_status()  # Check if the request was successful
        return int(response.headers.get('Content-Length', 0))
    except (requests.RequestException, ValueError) as e:
        print(f"Failed to get size of {url}: {e}")
        store_faulty_link(url)
        return None  # Return None for faulty links

def store_faulty_link(link):
    """Store a faulty link in a separate table in the database."""
    # a new database connection and cursor to avoid the ProgrammingError:
    local_conn = sqlite3.connect('links.db')
    local_cursor = local_conn.cursor()
    
    local_cursor.execute('''
    CREATE TABLE IF NOT EXISTS faulty_links (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE
    )
    ''')
    local_conn.commit()
    
    try:
        local_cursor.execute("INSERT INTO faulty_links (url) VALUES (?)", (link,))
        local_conn.commit()
    except sqlite3.IntegrityError:
        # This link already exists in the database
        pass
    
    # Close the local connection and cursor
    local_cursor.close()
    local_conn.close()

def get_all_pdf_sizes(pdf_urls):
    with ThreadPoolExecutor() as executor:
        sizes = list(tqdm(executor.map(get_pdf_size, (url[0] for url in pdf_urls)), total=len(pdf_urls), desc="Processing PDFs"))
    return sizes

# Get all PDF URLs from the database
cursor.execute("SELECT url FROM pdf_links")
pdf_urls = cursor.fetchall()

# Get all PDF sizes
pdf_sizes_bytes = get_all_pdf_sizes(pdf_urls)

# Filter out None values (faulty links)
pdf_sizes_bytes = [size for size in pdf_sizes_bytes if size is not None]

# Convert bytes to MB for easier readability
pdf_sizes_mb = [size / (1024 * 1024) for size in pdf_sizes_bytes]

# Plot a histogram of PDF sizes
plt.hist(pdf_sizes_mb, bins=30, edgecolor='black')
plt.title('Distribution of PDF File Sizes')
plt.xlabel('File Size (MB)')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

# Sum the sizes
total_size_bytes = sum(pdf_sizes_bytes)

# Convert bytes to MB for easier readability
total_size_mb = total_size_bytes / (1024 * 1024)

print(f"Total size of PDFs: {total_size_mb:.2f} MB")