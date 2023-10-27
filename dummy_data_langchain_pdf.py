import os
from dotenv import load_dotenv
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.document_loaders import PyPDFLoader
import traceback

# Load environment variables from .env file
load_dotenv()

# Fetch OpenAI API key from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_env = os.getenv('PINECONE_ENVIRONMENT')

# Given path to your text file
pdf_url = "https://www.theccc.org.uk/wp-content/uploads/2023/09/230925-PF-MN-ZEV-Mandate-Response.pdf"  # Replace with your PDF URL
loader = PyPDFLoader(pdf_url)
pages = loader.load_and_split()
if not pages:
    print("Error: The text file is empty.")
    exit(1)
text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)  # Adjust chunk_size
splitted_docs = text_splitter.split_documents(pages)

# Initialize Pinecone with hardcoded values
pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)

index_name = "langchain-demo"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(name=index_name, metric='cosine', dimension=1536)

embeddings = OpenAIEmbeddings()
try:
    docsearch = Pinecone.from_documents(splitted_docs, embeddings, index_name=index_name)
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

print(f"Data saved into Pinecone index: {index_name}")

print(f'Number of documents loaded: {len(pages)}')
print(f'Number of documents after splitting: {len(splitted_docs)}')

result = Pinecone.from_documents(splitted_docs, embeddings, index_name=index_name)
print(f'Result: {result}')