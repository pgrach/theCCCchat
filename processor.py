# to be able to loop through the db
import sqlite3
import requests


# to load and split the PDFs into smaller text segments
from langchain.document_loaders import PyPDFLoader 

# For creating Semantic Embeddings
import os
import getpass
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

#to call API keys from .env
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Connect to SQLite database
conn = sqlite3.connect('links.db')
cursor = conn.cursor()

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


# Iterating PROCESSING through PDFs from 2022 and 2023:
cursor.execute("SELECT url FROM pdf_links WHERE url LIKE 'https://www.theccc.org.uk/wp-content/uploads/2023%' OR url LIKE 'https://www.theccc.org.uk/wp-content/uploads/2022%'")
pdf_urls = cursor.fetchall()

for pdf_url in pdf_urls:
    pdf_url = pdf_url[0]  # Extract URL from tuple
    print(f"Processing {pdf_url}")
    process_pdf(pdf_url)

conn.close()