# from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from llama_index.core import SimpleDirectoryReader
# from llama_index.readers.file import PyMuPDFReader, MarkdownReader, PptxReader, PandasCSVReader, PandasExcelReader
from llama_index.readers.file import (
    PyMuPDFReader, 
    MarkdownReader, 
    PandasCSVReader, 
    PandasExcelReader,
    ImageReader,
    IPYNBReader
)
from llama_index.readers.docling import DoclingReader
import os


DOCUMENT_DIR = os.getenv('DOCUMENT_DIR')
ACCEPTED_FILES = ['pdf', 'txt', 'md', 'docx', 'pptx', 'csv', 'xlsx', 'json', 'ipynb', 'py', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']
# DOCUMENT_READERS = {
#     'pdf': PyPDFLoader,
#     'txt': TextLoader,
#     'md': UnstructuredMarkdownLoader
# }
DOCUMENT_READERS_PYMU = {
    # Document formats
    'pdf': PyMuPDFReader,
    'txt': SimpleDirectoryReader,
    'md': MarkdownReader,
    'docx': SimpleDirectoryReader,
    'doc': SimpleDirectoryReader,  # Older Word documents
    'pptx': SimpleDirectoryReader,
    'ppt': SimpleDirectoryReader,  # Older PowerPoint presentations
    
    # Data formats
    'csv': PandasCSVReader,
    'xlsx': PandasExcelReader,
    'xls': PandasExcelReader,  # Older Excel format
    
    # Programming files
    'ipynb': IPYNBReader,
    'py': SimpleDirectoryReader,
    'json': SimpleDirectoryReader,
    
    # Image formats (if you want OCR capability)
    'jpg': ImageReader,
    'jpeg': ImageReader,
    'png': ImageReader,
    'bmp': ImageReader,
    'tiff': ImageReader
}

DOCUMENT_READERS_DOCLING = {
    # Document formats
    'pdf': DoclingReader,
    'txt': DoclingReader,
    'md': DoclingReader,
    'docx': DoclingReader,
    'doc': SimpleDirectoryReader,  # Older Word documents
    'pptx': DoclingReader,
    'ppt': SimpleDirectoryReader,  # Older PowerPoint presentations
    
    # Data formats
    'csv': DoclingReader,
    'xlsx': DoclingReader,
    'xls': PandasExcelReader,  # Older Excel format
    
    # Programming files
    'ipynb': IPYNBReader,
    'py': SimpleDirectoryReader,
    'json': DoclingReader,
    
    # Image formats (if you want OCR capability)
    'jpg': ImageReader,
    'jpeg': ImageReader,
    'png': ImageReader,
    'bmp': ImageReader,
    'tiff': ImageReader
}

EMBEDDING_MODEL = "Alibaba-NLP/gte-large-en-v1.5"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 10 
NUMBER_RETRIEVAL = 5

