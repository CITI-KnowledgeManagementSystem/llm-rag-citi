from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader

import os


DOCUMENT_DIR = os.getenv('DOCUMENT_DIR')
ACCEPTED_FILES = ['pdf', 'txt', 'md']
DOCUMENT_READERS = {
    'pdf': PyPDFLoader,
    'txt': TextLoader,
    'md': UnstructuredMarkdownLoader
}
EMBEDDING_MODEL = "Alibaba-NLP/gte-large-en-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 10 
NUMBER_RETRIEVAL = 5

