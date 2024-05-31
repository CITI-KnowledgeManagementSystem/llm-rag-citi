from flask import Flask
from flask_cors import CORS
from pymilvus import connections
from sentence_transformers import SentenceTransformer
import torch

from .config import config_by_name
from .constant.document import EMBEDDING_MODEL
import torch

embedding_model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True, device='cuda' if torch.cuda.is_available() else 'cpu')


def create_app(config_name:str):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    CORS(app=app)

    # connect to milvus
    connections.connect(
        uri=config_by_name[config_name].MILVUS_URI,
        user=config_by_name[config_name].MILVUS_USER,
        password=config_by_name[config_name].MILVUS_PASSWORD,
        db_name=config_by_name[config_name].MILVUS_DB_NAME
    )

    # register blueprints
    # routes need to be imported inside to avoid conflict
    from .route import document_route, llm_route
    app.register_blueprint(document_route.blueprint)
    app.register_blueprint(llm_route.blueprint)

    print(f"The app is running in {config_name} environment")

    return app