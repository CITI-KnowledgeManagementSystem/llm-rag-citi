from flask import request
from ..service.document_service import *
from ..response import HTTPRequestException, HTTPRequestSuccess



def insert_document_to_vdb():
    body = request.get_json()
    document_id = body.get('document_id')
    user_id = body.get('user_id')
    tag = body.get('tag')
    collection_name = body.get('collection_name')
    original_filename = body.get('original_filename')
    change = body.get('change', False)
    parser = body.get('parser')
    
    try:
        insert_doc(str(document_id), user_id, tag, collection_name, original_filename, change, parser)
        return HTTPRequestSuccess(message="Document has been added", status_code=201).to_response()
    
    except HTTPRequestException as e:
        print(e.message)
        print(document_id, user_id, tag, collection_name, change)
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
    
def check_document_exist_in_vdb():
    args = request.args
    document_id = args.get('document_id')
    collection_name = args.get('collection_name')
    user_id = args.get('user_id')
    
    try:
        check_doc(document_id, collection_name, user_id)
        return HTTPRequestSuccess(message="Document exists", status_code=200).to_response()
    
    except HTTPRequestException as e:
        print(e.message)
        return e.to_response()
    
async def create_mind_map():  
    
    body = request.get_json()
    document_id = body.get('document_id')
    user_id = body.get('user_id')
    tag = body.get('tag')
    collection_name = body.get('collection_name')
    
    # =========== test ==============
    
    # document_id = "1"
    # user_id = "user_2yfckZL2Y68NPUyEMOMy456sBWD"
    # tag = "docx"
    # collection_name = "private"

    try:
        res = await mind_map(document_id, user_id, tag, collection_name)
        output_file = "mindmap_output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(res)
    
        print(f"Mind map generated successfully: {output_file}")
        return HTTPRequestSuccess(message="Mind map created", status_code=200, payload=res).to_response()
    
    except HTTPRequestException as e:
        print(e.message)
        return e.to_response()
    
    

        

    