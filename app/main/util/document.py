from pymilvus import utility, Collection
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from ..constant.document import ACCEPTED_FILES, DOCUMENT_READERS, CHUNK_SIZE, CHUNK_OVERLAP, NUMBER_RETRIEVAL
from ...main import embedding_model


def check_document_validation(tag:str) -> bool:
    return tag in ACCEPTED_FILES


def check_collection_validation(collection_name:str) -> bool:
    return utility.has_collection(collection_name)


def check_document_exists(document_path:str) -> bool:
    return os.path.isfile(document_path)


def document_to_embeddings(content:str) -> list:
    return embedding_model.encode_documents(content)[0]


def read_file(file_path:str, tag:str):
    loader_cls = DOCUMENT_READERS[tag]
    return loader_cls(file_path).load()


def split_documents(document_data):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(document_data)


def retrieve_documents_from_vdb(embeddings, collection_name:str):
    collection = Collection(collection_name)
    params = { "metric_type": 'COSINE' }
    res = collection.search(data=[embeddings], anns_field='vector', param=params, limit=NUMBER_RETRIEVAL, output_fields=["document_id", "content"])
    return res
