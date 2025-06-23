from pymilvus import Collection
from uuid import uuid4

from ..constant.document import DOCUMENT_DIR
from ..util.document import *
from ..response import HTTPRequestException

import os


def insert_doc(document_id:str, user_id:str, tag:str, collection_name:str, change=False):
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
    document_data = read_file(document_path, tag)
    print('DOKUMEN DATA COYY ============',document_data)
    splitted_document_data = split_documents(document_data)
    print(f"Total chunks/nodes yang dihasilkan: {len(splitted_document_data)}")

    # contain objects
    data_objects = []
    for doc in splitted_document_data:
        data = {
            "id": str(uuid4()),
            "vector": document_to_embeddings(doc.text),
            "content": doc.text,
            "user_id": user_id,
            "document_id": document_id,
            # "metadata": doc.metadata
        }
        data_objects.append(data)
    
    try:
        for data in data_objects:
            print(f"Document ID: {data['document_id']}, User ID: {data['user_id']}, Content: {data['content']}...")  # Print first 50 characters of content for brevity
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
