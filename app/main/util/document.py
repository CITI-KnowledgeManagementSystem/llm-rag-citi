from pymilvus import utility, Collection
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import SentenceSplitter
import os
from pymilvus import AnnSearchRequest, Function, FunctionType
import paramiko

from ..constant.document import ACCEPTED_FILES, DOCUMENT_READERS, CHUNK_SIZE, CHUNK_OVERLAP, NUMBER_RETRIEVAL, DOCUMENT_DIR
from ..response import HTTPRequestException

import requests
from typing import List, Dict
from ragas import evaluate

def check_document_validation(tag:str) -> bool:
    return tag in ACCEPTED_FILES


def check_collection_validation(collection_name:str) -> bool:
    return utility.has_collection(collection_name)


def check_document_exists(document_path:str) -> bool:
    return os.path.isfile(document_path)


# def document_to_embeddings(content:str) -> list:
#     response = requests.post("http://140.118.101.181:1234/embed", json=content)
#     if response.status_code == 200:
#         return response.json()["embeddings"]
#     else:
#         raise HTTPRequestException(message="Failed to get embeddings", status_code=response.status_code)

def document_to_embeddings(content: str) -> List[float]:
    """Original function - returns dense embeddings only"""
    try:
        embedding_url = os.getenv('EMBEDDING_URL')
        response = requests.post(
            f'{embedding_url}/embed/simple',  # Use simple endpoint
            json={"content": content},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["embeddings"]
        else:
            raise HTTPRequestException(
                message=response.json().get("detail", "Failed to get embeddings"),
                status_code=response.status_code
            )
    except requests.exceptions.RequestException as e:
        raise HTTPRequestException(
            message=str(e),
            status_code=getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        )

def document_to_embeddings_bge_m3(content: str) -> Dict:
    """
    BGE-M3 version - returns both dense and sparse embeddings
    Use this when you need hybrid search capabilities
    """
    try:
        embedding_url = os.getenv('EMBEDDING_URL')
        
        # Log the request details
        request_data = {
            "content": content,
            "model": "bge-m3",
            "return_dense": True,
            "return_sparse": True
        }
        print(f"Sending request to BGE-M3 service:")
        print(f"URL: {embedding_url}/embed")
        print(f"Content length: {len(content)}")
        print(f"Content preview: {content[:100]}...")
        
        response = requests.post(
            f'{embedding_url}/embed',
            json=request_data,
            timeout=30
        )
        
        print(f"BGE-M3 service response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"BGE-M3 service response keys: {list(result.keys())}")
            return {
                "dense": result["dense_embeddings"],
                "sparse": result["sparse_embeddings"]
            }
        else:
            print(f"BGE-M3 service error response: {response.text}")
            raise HTTPRequestException(
                message=response.json().get("detail", "Failed to get embeddings"),
                status_code=response.status_code
            )
    except requests.exceptions.RequestException as e:
        print(f"Request exception when calling BGE-M3 service: {e}")
        raise HTTPRequestException(
            message=f"Network error calling embedding service: {str(e)}",
            status_code=500
        )
    except Exception as e:
        print(f"Unexpected error in document_to_embeddings_bge_m3: {e}")
        raise HTTPRequestException(
            message=f"Embedding generation error: {str(e)}",
            status_code=500
        )

def read_file(file_path:str, tag:str):
    loader = DOCUMENT_READERS[tag]
    if tag in ['pdf', 'md',  'html', 'htm', 'ipynb', 
               'jpg', 'jpeg', 'png', 'bmp', 'tiff']:
        loader_cls = loader()
        return loader_cls.load_data(file_path)
    # Handle SimpleDirectoryReader for text-based files
    elif tag in ['txt', 'docx', 'doc','py', 'json', 'pptx', 'ppt']:
        return loader(input_files=[file_path]).load_data()
    # Handle pandas-based readers
    elif tag in ['csv', 'xlsx', 'xls']:
        loader_cls = loader()
        return loader_cls.load_data(file_path)


def split_documents(document_data):
    # splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, include_metadata=True)
    # splitter = 
    return splitter.get_nodes_from_documents(document_data)


# def retrieve_documents_from_vdb(embeddings, collection_name:str, reranking:bool=False, user_id=None):
#     collection = Collection(collection_name)
#     print('retrieving all documents from vdb: ', collection.num_entities)
#     params = { "metric_type": 'COSINE' }

#     if reranking == True:
#         searchreq1 = {
#             "data": [embeddings],
#             "anns_field": "vector",
#             "limit" : NUMBER_RETRIEVAL*2,
#             "param": {
#                 "metric_type": 'COSINE'
#             }
#         }
        
#         print('searchreq1', searchreq1)
        
#         if collection_name == 'private' : 
#             searchreq1["expr"] = f"user_id == '{user_id}'"
    
#         req1 = AnnSearchRequest(**searchreq1)
        
#         print('req1', req1)

#         res = collection.hybrid_search(
#             reqs=[req1],
#             rerank=WeightedRanker(1),
#             limit = NUMBER_RETRIEVAL,
#             output_fields=["document_id", "content"]
#         )
#     else :
#         if collection_name == 'private':
#             res = collection.search(data=[embeddings], anns_field='vector', param=params, limit=NUMBER_RETRIEVAL, expr=f"user_id == '{user_id}'", output_fields=["document_id", "content"])
#         else:
#             res = collection.search(data=[embeddings], anns_field='vector', param=params, limit=NUMBER_RETRIEVAL, output_fields=["document_id", "content"])

#     print('res', res)
#     print('res[0]', res[0])
    
#     return res[0]

def retrieve_documents_from_vdb(embeddings, collection_name:str, reranking:bool=False, user_id=None, query:str=None, sparse_embeddings=None):
    collection = Collection(collection_name)
    print('retrieving all documents from vdb: ', collection.num_entities)
    # params = {"metric_type": 'COSINE', "reranker": "jina-reranker-v1-base-en", "provider": "vllm", "queries": [query], "endpoint": "http://localhost:8080/v1/rerank"}
    base_params = {"metric_type": 'COSINE'}

    if reranking:
        if not query:
            raise ValueError("Query parameter is required when reranking is enabled")
        if sparse_embeddings is None:
            raise ValueError("Sparse embeddings are required for hybrid search")
            
        # Create dense vector search request
        dense_search_params = {
            "data": [embeddings],  # Dense embeddings
            "anns_field": "vector",
            "limit": NUMBER_RETRIEVAL * 2,
            "param": base_params
        }
        
        if collection_name == 'private': 
            dense_search_params["expr"] = f"user_id == '{user_id}'"
            
        # Create sparse vector search request  
        sparse_search_params = {
            "data": [sparse_embeddings],  # Sparse embeddings (different from dense)
            "anns_field": "sparse_vector", 
            "limit": NUMBER_RETRIEVAL * 2,
            "param": {"metric_type": "IP"}  # Sparse vectors typically use Inner Product
        }
        
        if collection_name == 'private': 
            sparse_search_params["expr"] = f"user_id == '{user_id}'"
    
        # Create AnnSearchRequest objects
        dense_req = AnnSearchRequest(**dense_search_params)
        sparse_req = AnnSearchRequest(**sparse_search_params)
        
                # Create vLLM reranker function
        vllm_ranker = Function(
            name="vllm_semantic_ranker",
            input_field_names=["content"],  # Field containing text to rerank
            function_type=FunctionType.RERANK,
            params={
                "reranker": "model",
                "provider": "vllm", 
                "queries": [query],
                "endpoint": "http://localhost:8080",  # Standard vLLM endpoint
                # "maxBatch": 64,
                # "truncate_prompt_tokens": 256,
            }
        )
        
        try:
            # Perform hybrid search with built-in reranking
            hybrid_results = collection.hybrid_search(
                collection_name=collection_name,
                reqs=[dense_req, sparse_req],
                ranker=vllm_ranker,
                limit=NUMBER_RETRIEVAL,
                output_fields=["document_id", "content"]
            )
            
            print('========================== HYBRID SEARCH RESULTS ==============================')
            print('hybrid_results', hybrid_results)
            
            return hybrid_results
            
        except Exception as e:
            print(f"Error with hybrid search: {e}")
            # Fallback to dense search only
            print("Falling back to dense search only...")
            
            if collection_name == 'private':
                fallback_results = collection.search(
                    data=[embeddings],
                    anns_field='vector',
                    param=base_params,
                    limit=NUMBER_RETRIEVAL,
                    expr=f"user_id == '{user_id}'",
                    output_fields=["document_id", "content"]
                )
            else:
                fallback_results = collection.search(
                    data=[embeddings],
                    anns_field='vector',
                    param=base_params,
                    limit=NUMBER_RETRIEVAL,
                    output_fields=["document_id", "content"]
                )
            return fallback_results
            
    else:
        # Non-reranking case - single vector search
        if collection_name == 'private':
            res = collection.search(
                data=[embeddings],
                anns_field='vector',  # Use specific field name
                param=base_params,
                limit=NUMBER_RETRIEVAL,
                expr=f"user_id == '{user_id}'",
                output_fields=["document_id", "content"]
            )
        else:
            res = collection.search(
                data=[embeddings],
                anns_field='vector',  # Use specific field name
                param=base_params,
                limit=NUMBER_RETRIEVAL,
                output_fields=["document_id", "content"]
            )
        return res

def create_sftp_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client

def retrieve_documents_from_sftp(user_id:str, document_id:str, tag:str, collection_name:str):
    sftp_client = create_sftp_client()
    print('ngambil docs');
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

    document_path = os.path.join(DOCUMENT_DIR, document_id + '.' + tag)
    
    print(document_path, collection_name)

    try:
        with sftp_client.open_sftp() as sftp_client:
            if collection_name == 'private':
                sftp_client.get(
                    remotepath=f"{os.getenv('QNAP_SFTP_PRIVATE_DIR')}/{user_id}/{document_id}.{tag}",
                    localpath=document_path
                )
            else :
                sftp_client.get(
                    remotepath=f"{os.getenv('QNAP_SFTP_PUBLIC_DIR')}/{user_id}/{document_id}.{tag}",
                    localpath=document_path
                )
    except Exception as e:
        print(e, 'here')
        raise HTTPRequestException(message="Failed to retrieve the document", status_code=500)
    
def move_documents_from(user_id:str, document_id:str, tag:str, collection_name:str):
    sftp_client = create_sftp_client()                
    print('mindahin docs')
    try:
        sftp_client.connect(
            hostname=os.getenv('QNAP_SFTP_IP'),
            port=int(os.getenv('QNAP_SFTP_PORT')),
            username=os.getenv('QNAP_SFTP_USERNAME'),
            password=os.getenv('QNAP_SFTP_PASSWORD')
        )
    except Exception as e:
        print(e, 'siniiii')
        raise HTTPRequestException(message="Failed to connect to the server", status_code=500)
    
    try:
        with sftp_client.open_sftp() as sftp_client:
            if collection_name == 'private':
                source_path = f"{os.getenv('QNAP_SFTP_PRIVATE_DIR')}/{user_id}"
                destination_path = f"{os.getenv('QNAP_SFTP_PUBLIC_DIR')}/{user_id}"
                
                check_directory(sftp_client, destination_path)
                
                sftp_client.rename(f"{source_path}/{document_id}.{tag}", f"{destination_path}/{document_id}.{tag}")
            else :
                source_path = f"{os.getenv('QNAP_SFTP_PUBLIC_DIR')}/{user_id}"
                destination_path = f"{os.getenv('QNAP_SFTP_PRIVATE_DIR')}/{user_id}"
                
                check_directory(sftp_client, destination_path)
                
                sftp_client.rename(f"{source_path}/{document_id}.{tag}", f"{destination_path}/{document_id}.{tag}")
    except Exception as e:
        print(e, 'sanaaaa')
        raise HTTPRequestException(message="Failed to retrieve the document", status_code=500)            

def check_directory(sftp, path:str) :
    try:
        sftp.chdir(path)
    except IOError:
        # Directory does not exist, create it
        mkdir_p(sftp, path)
        sftp.chdir(path)
        
def mkdir_p(sftp, remote_directory):
    try:
        sftp.stat(remote_directory)
    except IOError:
        sftp.mkdir(remote_directory)

