from flask import request
from ..service.document_service import insert_doc, delete_doc
from ..response import HTTPRequestException, HTTPRequestSuccess


def insert_document_to_vdb():
    body = request.get_json()
    document_id = body.get('document_id')
    user_id = body.get('user_id')
    tag = body.get('tag')
    collection_name = body.get('collection_name')  
    
    try:
        insert_doc(document_id, user_id, tag, collection_name)
        return HTTPRequestSuccess(message="Document has been added", status_code=201).to_response()
    
    except HTTPRequestException as e:
        print(e.message)
        return e.to_response()
    

def delete_document_from_vdb():
    args = request.args
    document_id = args.get('document_id')
    collection_name = args.get('collection_name')

    try:
        delete_doc(document_id, collection_name)
        return HTTPRequestSuccess(message="Document has been deleted", status_code=200).to_response()
    
    except HTTPRequestException as e:
        print(e.message)
        return e.to_response()
        

    