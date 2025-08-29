from pymilvus import Collection
from uuid import uuid4

from ..constant.document import DOCUMENT_DIR
from ..util.document import *
from ..response import HTTPRequestException

import os

from ..constant.llm import *
from llama_index.core import PromptTemplate
from ...main import generation_llm
import json
import datetime


def insert_doc(document_id:str, user_id:str, tag:str, collection_name:str, original_filename:str, change=False, parser="pymu"):
    if not document_id or not user_id or not tag or not collection_name:
        raise HTTPRequestException(message="Please fill all the required fields")

    document_path = os.path.join(DOCUMENT_DIR, document_id + '.' + tag)

    if not check_collection_validation(collection_name):
        raise HTTPRequestException(message="The provided collection doesn't exist")
    
    if not check_document_validation(tag):
        raise HTTPRequestException(message="The provided document is not valid")
    
    print(document_id, user_id, tag, collection_name, document_path, change)
    
    retrieve_documents_from_sftp(
        user_id=user_id,
        document_id=document_id,
        tag=tag,
        collection_name=collection_name,
    )
    
    
    if (change):
        move_documents_from(
            user_id=user_id,
            document_id=document_id,
            tag=tag,
            collection_name=collection_name,
        )
    
    collection_name = collection_name if change==False else "public" if collection_name=="private" else "private"
    
    collection = Collection(collection_name)
    
    # retrieve the document from sftp             
    # read the file
    document_data = read_file_mineru(document_path, tag, parser=parser) if parser=="mineru" else read_file(document_path, tag, parser=parser)
    # print('DOKUMEN DATA COYY ============',document_data)
    splitted_document_data = split_documents(document_data)
    print(f"Total chunks/nodes yang dihasilkan: {len(splitted_document_data)}")

    # contain objects
    data_objects = []
    
    for doc in splitted_document_data:
        # print('Document', doc)  # Print first 200 characters of the document text
        # print(f"Metadata: {doc.metadata}")
        try:
            # Get both dense and sparse embeddings in one call
            print("Document text for embedding:", doc.text)  # Print first 100 characters for debugging
            embeddings_result = document_to_embeddings(doc.text)
            
            # Ensure sparse vector format is compatible with Milvus
            # Convert string keys to integers if needed
            sparse_vector = embeddings_result["sparse"]
            if isinstance(sparse_vector, dict):
                # Convert string keys to integers if they exist
                formatted_sparse_vector = {
                    int(k) if isinstance(k, str) else k: float(v) 
                    for k, v in sparse_vector.items()
                }
            else:
                formatted_sparse_vector = sparse_vector
            
            data = {
                "id": str(uuid4()),
                "vector": embeddings_result["dense"],
                "sparse_vector": formatted_sparse_vector,
                "content": doc.text,
                "user_id": user_id,
                "document_id": document_id,
                "document_name": original_filename,
                # "page_number": int(doc.metadata.get("source", 0)) if doc.metadata else 0,
                "page_number": int(doc.metadata.get("page_number", 0)) if doc.metadata else 0
            
                # "metadata": doc.metadata
            }
            print(f"Prepared data object for insertion: ID={data['id']}, Document ID={data['document_id']}, User ID={data['user_id']}, Page Number={data['page_number']}")
            data_objects.append(data)
        except Exception as e:
            print(f"Failed to generate embeddings: {str(e)}")
            raise HTTPRequestException(message=f"Failed to generate embeddings: {str(e)}", status_code=500)
    
    try:
        # for data in data_objects:
            # print(f" ID: {data['id']}, Document ID: {data['document_id']}, User ID: {data['user_id']}, Content: {data['content']}")
        collection.insert(data=data_objects)

    except Exception as e:
        raise HTTPRequestException(message=str(e), status_code=500)
    
    os.remove(document_path)
    
    

def delete_doc(document_id:str, collection_name:str):
    if not document_id or not collection_name:
        raise HTTPRequestException("Please fill all the required fields")
    
    if not check_collection_validation(collection_name):
        raise HTTPRequestException("The provided collection doesn't exist")
    
    collection = Collection(collection_name)

    # delete from the collection
    try:
        collection.delete(f"document_id == '{document_id}'")
    
    except Exception as e:
        raise HTTPRequestException(message=str(e), status_code=500)
    
def check_doc(document_id:str, collection_name:str, user_id:str):
    if not document_id:
        raise HTTPRequestException("Please fill the document_id field")
    
    if not user_id:
        raise HTTPRequestException("Please fill the user_id field")
    
    if not collection_name:
        raise HTTPRequestException("Please fill the collection_name field")
    
    if not check_collection_validation(collection_name):
        raise HTTPRequestException("The provided collection doesn't exist")
    
    collection = Collection(collection_name)

    # check from the collection
    try:
        res = collection.query(
            expr=f"document_id == '{document_id}' && user_id == '{user_id}'",
            limit=1
        )
        if not res:
            raise HTTPRequestException("The document doesn't exist", status_code=404)
    
    except Exception as e:
        raise HTTPRequestException("The document doesn't exist", status_code=404)
    

async def mind_map(document_id:str, user_id:str, tag:str, collection_name:str):
    
    file_path = os.path.join(DOCUMENT_DIR, document_id + '.' + tag)
    
    retrieve_documents_from_sftp(
        user_id=user_id,
        document_id=document_id,
        tag=tag,
        collection_name=collection_name,
    )
    
    read_files = read_file(file_path, tag)
    
    print("Content to be processed:", read_files[:1000])  # Print first 1000 characters for debugging
    
    extracted_texts = [doc.text_resource.text for doc in read_files if doc.text_resource and doc.text_resource.text]


    # Gabungkan semua teks jika diperlukan
    
    print("Full text extracted:", extracted_texts[0][:1000])  # Print first 1000 characters for debugging
    
    content = read_files[0]
    
    prompt = PromptTemplate(MINDMAP_PROMPT_TEMPLATE)
    
    try:
        response = await generation_llm.acomplete(prompt.format(content=content))
        markdown_content = response.text
        print("Generated Markdown Content:", markdown_content)
        
        return markdown_content
        
    except Exception as e:
        raise HTTPRequestException(message=f"Failed to generate mind map: {str(e)}", status_code=500)
    


