from pymilvus import Collection
from uuid import uuid4

from ..constant.document import DOCUMENT_DIR
from ..util.document import *
from ..response import HTTPRequestException

import os


def insert_doc(document_id:str, user_id:str, tag:str, collection_name:str):
    if not document_id or not user_id or not tag or not collection_name:
        raise HTTPRequestException(message="Please fill all the required fields")

    document_path = os.path.join(DOCUMENT_DIR, collection_name, user_id, document_id + '.' + tag)

    if not check_collection_validation(collection_name):
        raise HTTPRequestException(message="The provided collection doesn't exist")
    
    if not check_document_validation(tag):
        raise HTTPRequestException(message="The provided document is not valid")
    
    if not check_document_exists(document_path):
        raise HTTPRequestException(message="The document doesn't exist")
    
    collection = Collection(collection_name)

    # read the file
    document_data = read_file(document_path, tag)
    splitted_document_data = split_documents(document_data)

    print('sini')
    
    # contain objects
    data_objects = []
    for doc in splitted_document_data:
        data = {
            "id": str(uuid4()),
            "vector": document_to_embeddings(doc.page_content),
            "content": doc.page_content,
            "user_id": user_id,
            "document_id": document_id
        }
        data_objects.append(data)
    
    print(data_objects)
    
    try:
        collection.insert(data=data_objects)

    except Exception as e:
        raise HTTPRequestException(message=str(e), status_code=500)
    

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
