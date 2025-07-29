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


def insert_doc(document_id:str, user_id:str, tag:str, collection_name:str, original_filename:str, change=False):
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
    # print('DOKUMEN DATA COYY ============',document_data)
    splitted_document_data = split_documents(document_data)
    print(f"Total chunks/nodes yang dihasilkan: {len(splitted_document_data)}")

    # contain objects
    data_objects = []
    for doc in splitted_document_data:
        # print(f"Metadata: {doc.metadata}")
        try:
            # Get both dense and sparse embeddings in one call
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
                "page_number": int(doc.metadata.get("source", 0)) if doc.metadata else 0,
                # "metadata": doc.metadata
            }
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
    

async def mind_map(file_path: str, tag: str):
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
        
        html_output = create_mindmap_html(
            markdown_content=markdown_content,
            source_file=file_path
        )
        
        return html_output
        
    except Exception as e:
        raise HTTPRequestException(message=f"Failed to generate mind map: {str(e)}", status_code=500)

def create_mindmap_html(markdown_content: str, source_file: str) -> str:
    """Generate complete HTML structure for the mind map"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_result = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mind Map from {source_file}</title>
        <script src="https://cdn.jsdelivr.net/npm/markmap-view"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
            }}
            .container {{
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                border-radius: 8px;
            }}
            header {{
                border-bottom: 1px solid #eaeaea;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .file-info {{
                color: #7f8c8d;
                font-size: 0.9em;
            }}
            #mindmap {{
                width: 100%;
                height: 600px;
                border: 1px solid #eaeaea;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .controls {{
                margin: 15px 0;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }}
            .btn {{
                padding: 8px 16px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                text-decoration: none;
                font-size: 14px;
            }}
            .btn:hover {{
                background-color: #2980b9;
            }}
            .metadata {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                margin-top: 20px;
                font-size: 0.9em;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Mind Map: {source_file}</h1>
                <div class="file-info">Source: {source_file}</div>
            </header>
            
            <div id="mindmap"></div>
            
            <div class="controls">
                <a href="#" onclick="downloadMarkdown()" class="btn">Download Markdown</a>
                <a href="#" onclick="downloadHTML()" class="btn">Download HTML</a>
            </div>
        </div>
        
        <script>
            // Initialize mindmap
            markmap.Html('div#mindmap', {{
                content: {json.dumps(markdown_content)},
                zoom: true,
                pan: true
            }});
            
            // Download functions
            function downloadMarkdown() {{
                const blob = new Blob([{json.dumps(markdown_content)}], {{ type: 'text/markdown' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mindmap_a.md';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}
            
            function downloadHTML() {{
                const html = document.documentElement.outerHTML;
                const blob = new Blob([html], {{ type: 'text/html' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mindmap_a.html';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}
        </script>
    </body>
    </html>
    """
    
    return html_result
