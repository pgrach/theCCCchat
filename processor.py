# to be able to loop through the db
import sqlite3
import requests

#to allow concurrence
import hashlib 
from concurrent.futures import ThreadPoolExecutor

# to load and split the PDFs into smaller text segments
from langchain.document_loaders import PyPDFLoader 

# For creating Semantic Embeddings, storage and retrival
import os
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone

#to call API keys from .env
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file
openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_env = os.getenv('PINECONE_ENVIRONMENT')

# Connect to SQLite database
conn = sqlite3.connect('links.db')
cursor = conn.cursor()

# Breaking Down PDFs
def process_pdf(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Check if the request was successful
    except requests.RequestException as e:
        print(f"Failed to retrieve {pdf_url}: {e}")
        return None
    
    # Generate a unique hash for the current URL
    url_hash = hashlib.md5(pdf_url.encode()).hexdigest()
    temp_file_name = f'temp_{url_hash}.pdf'


    with open(temp_file_name, 'wb') as temp_pdf_file:
        temp_pdf_file.write(response.content)
    
    loader = PyPDFLoader(temp_file_name)
    pages = loader.load_and_split()
    
    return pages, temp_file_name  # Return pages and temp_file_name for further processing


# Creating Semantic Embeddings, Efficient Storage and Retrieval

# Initialize Pinecone
pinecone.init(
    api_key=pinecone_api_key,
    environment=pinecone_env
)

# Define your Pinecone index name
index_name = "langchain-retrieval-augmentation"

# Create a new index if it doesn't already exist
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        metric='cosine',
        dimension=1536  # Assuming the embeddings have a dimension of 1536 (double-checked)
    )

# Connect to the new index
index = pinecone.Index(index_name)

#Embedding Storage
def create_and_store_embeddings(pages, temp_file_name):
    documents = [page.page_content for page in pages]
    
    # Generate embeddings for the text segments
    embeddings_model = OpenAIEmbeddings()
    embeddings = embeddings_model.embed_documents(documents)
    
    # Store embeddings in Pinecone
    item_mapping = {f"item-{i}": embedding for i, embedding in enumerate(embeddings)}
    index.upsert(vectors=item_mapping)
    try:
        os.remove(temp_file_name)
        print(f'Successfully deleted {temp_file_name}')
    except Exception as e:
        print(f'Failed to delete {temp_file_name}: {e}')


def process_and_store(pdf_url):
    pdf_url = pdf_url[0]
    print(f"Processing {pdf_url}")
    pages, temp_file_name = process_pdf(pdf_url)
    if pages:
        print(f"Processed {len(pages)} pages from {pdf_url}")
        create_and_store_embeddings(pages, temp_file_name)
    else:
        print(f"Failed to process {pdf_url}")

# Iterating PROCESSING through PDFs from 2022 and 2023:
# cursor.execute("SELECT url FROM pdf_links WHERE url LIKE 'https://www.theccc.org.uk/wp-content/uploads/2023%' OR url LIKE 'https://www.theccc.org.uk/wp-content/uploads/2022%'")
cursor.execute("SELECT url FROM pdf_links WHERE id IN (1, 2, 3, 4)")
pdf_urls = cursor.fetchall()

# processing loop
with ThreadPoolExecutor() as executor:
    executor.map(process_and_store, pdf_urls)

conn.close()