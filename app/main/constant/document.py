from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader

import os


DOCUMENT_DIR = os.getenv('DOCUMENT_DIR')
ACCEPTED_FILES = ['pdf', 'txt', 'md']
DOCUMENT_READERS = {
    'pdf': PyPDFLoader,
    'txt': TextLoader,
    'md': UnstructuredMarkdownLoader
}
CHUNK_SIZE = 256
CHUNK_OVERLAP = 0
NUMBER_RETRIEVAL = 5

