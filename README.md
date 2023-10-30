![GitHub stars](https://img.shields.io/github/stars/pgrach/theCCCchat?style=social)
![GitHub forks](https://img.shields.io/github/forks/pgrach/theCCCchat?style=social)

# Chatting with PDF Publications

Welcome to our project that enables AI-driven conversations with PDF content. This repository walks you through three phases of development: Ingestion, Processing, and Interaction.

## Table of Contents
- [Ingestion Phase](#1-ingestion-phase)
- [Processing Phase](#2-processing-phase)
- [Interaction Phase](#3-interaction-phase)
- [Future Ideas](#inspiration-for-future-ideas)
![image](https://github.com/pgrach/theCCCchat/assets/32228270/a09301b4-3356-43dc-8ad7-f57eb8881894)

## 1. Ingestion Phase

Our goal in this phase is to collect PDF links from the CCC publications website and store them in a SQLite database.

### Features:
- **Scraping Script**: Collect all the PDF URLs from the website by:
  - Scraping the main publications page to gather links to individual publication pages.
  - Navigating to each publication page to discover and collect links to PDFs.
  - Storing the identified links in an SQLite database named `links.db`.

**Success**: Successfully stored 1321 links in the SQLite database.

### Future Improvements:
- Address non-PDF publications using the `UnstructuredHTMLLoader`.
- Introduce a weekly schedule for scraping new publications.

## 2. Processing Phase

In this phase, we process and analyze the collected PDFs.

### Steps:
- **Scope Analysis**: Using `size.py`, we determined the total size to be 1942.27 MB, identifying 1267 unique functional pdfs from www.theccc.org.uk.
- **PDF Breakdown**: Utilize Langchain's `PyPDFLoader` and its `load_and_split` method to break down PDFs by pages.
- **Text Segmentation**: Segment the text into smaller chunks using Langchain's `RecursiveCharacterTextSplitter`.
- **Semantic Embeddings**: Generate semantic embeddings for the text segments with OpenAI embeddings.
- **Storage and Retrieval**: Efficiently store and retrieve embeddings using Pinecone.

**Success**: Efficiently processed both small and large PDF links, providing a progress bar for better user experience.

### Future Improvements:
- Current implementation has hardcoded PDF URL and Pinecone index name. This needs dynamic handling.
- Research and implement advanced indexing strategies for handling vast amounts of data.

## 3. Interaction Phase

This phase focuses on enabling user interactions with the processed content.

### Features:
- **Pinecone Initialization**: Set up document search using OpenAIEmbeddings and Langchain's vectorstores.
- **Language Model Setup**: Set up the language model and a question-answering chain using langchain.llms' OpenAI.
- **User Interaction**: Engage with users, understand their queries, and display results leveraging `similarity_search` via embeddings and vectorstores.

**Success**: Achieved an interactive chat functionality with the processed PDF content.

### Future Improvements:
- Enhance error handling mechanisms.
- Develop a web-based interface using Streamlit for a more intuitive user experience.

## Inspiration for Future Ideas:

Consider building a universal engine capable of interacting with any PDF publications directory on the web. This could revolutionize how we access and engage with content on the internet, offering a more interactive and personalized experience.

## Contact Information

For questions, feedback, or collaboration opportunities, feel free to reach out:

- **Email**: [gpu2003@gmail.com](mailto:gpu2003@gmail.com)
- **Twitter**: [@pgrache](https://twitter.com/pgrache)
- **LinkedIn**: [Pawel Grach](https://www.linkedin.com/in/pgrach/)
