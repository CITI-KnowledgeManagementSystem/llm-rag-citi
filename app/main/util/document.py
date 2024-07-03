from pymilvus import utility, Collection
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from pymilvus import WeightedRanker, AnnSearchRequest
import paramiko

from ..constant.document import ACCEPTED_FILES, DOCUMENT_READERS, CHUNK_SIZE, CHUNK_OVERLAP, NUMBER_RETRIEVAL, DOCUMENT_DIR
from ...main import embedding_model
from ..response import HTTPRequestException


def check_document_validation(tag:str) -> bool:
    return tag in ACCEPTED_FILES


def check_collection_validation(collection_name:str) -> bool:
    return utility.has_collection(collection_name)


def check_document_exists(document_path:str) -> bool:
    return os.path.isfile(document_path)


def document_to_embeddings(content:str) -> list:
    return embedding_model.encode(content, show_progress_bar=True)


def read_file(file_path:str, tag:str):
    loader_cls = DOCUMENT_READERS[tag]
    return loader_cls(file_path).load()


def split_documents(document_data):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(document_data)


def retrieve_documents_from_vdb(embeddings, collection_name:str, reranking:bool=False, user_id=None):
    collection = Collection(collection_name)
    params = { "metric_type": 'IP' }

    if reranking == True:
        searchreq1 = {
            "data": [embeddings],
            "anns_field": "vector",
            "limit" : NUMBER_RETRIEVAL*2,
            "param": {
                "metric_type": 'IP'
            }, 
            "expr" : f"user_id == '{user_id}'"
        }

        req1 = AnnSearchRequest(**searchreq1)

        if collection_name == 'private' : 
            res = collection.hybrid_search(
                reqs=[req1],
                rerank=WeightedRanker(1),
                limit = NUMBER_RETRIEVAL,
                output_fields=["document_id", "content"]
            )
        else : 
            res = collection.hybrid_search(
                reqs=[req1],
                rerank=WeightedRanker(1),
                limit = NUMBER_RETRIEVAL,
                output_fields=["document_id", "content"]
            )

    else :
        if collection_name == 'private':
            res = collection.search(data=[embeddings], anns_field='vector', param=params, limit=NUMBER_RETRIEVAL, expr=f"user_id == '{user_id}'", output_fields=["document_id", "content"])
        else:
            res = collection.search(data=[embeddings], anns_field='vector', param=params, limit=NUMBER_RETRIEVAL, output_fields=["document_id", "content"])

    return res[0]

def create_sftp_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client

def retrieve_documents_from_sftp(user_id:str, document_id:str, tag:str, collection_name:str):
    sftp_client = create_sftp_client()
    print(os.getenv('QNAP_SFTP_IP'), os.getenv('QNAP_SFTP_PORT'), os.getenv('QNAP_SFTP_USERNAME'), os.getenv('QNAP_SFTP_PASSWORD'))
    try:
        sftp_client.connect(
            hostname=os.getenv('QNAP_SFTP_IP'),
            port=int(os.getenv('QNAP_SFTP_PORT')),
            username=os.getenv('QNAP_SFTP_USERNAME'),
            password=os.getenv('QNAP_SFTP_PASSWORD')
        )
    except Exception as e:
        print(e)
        raise HTTPRequestException(message="Failed to connect to the server", status_code=500)

    document_path = os.path.join(DOCUMENT_DIR, collection_name, document_id + '.' + tag)

    try:
        with sftp_client.open_sftp() as sftp_client:
            if collection_name == 'private':
                sftp_client.get(
                    remotepath=f"{os.getenv('QNAP_SFTP_PRIVATE_DIR')}/{user_id}/{document_id}.{tag}",
                    localpath=document_path
                )
            else :
                sftp_client.get(
                    remotepath=os.getenv('QNAP_SFTP_PUBLIC_DIR') + '/' + document_id + '.' + tag,
                    localpath=document_path
                )
    except Exception as e:
        print(e)
        raise HTTPRequestException(message="Failed to retrieve the document", status_code=500)

