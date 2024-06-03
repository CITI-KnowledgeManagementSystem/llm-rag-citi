from flask import Flask
from flask_cors import CORS
from pymilvus import connections
from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer
import torch

from .config import config_by_name
from .constant.document import EMBEDDING_MODEL
from .constant.llm import TEMPERATURE, MODEL, N_HYDE_INSTANCE, HYDE_LLM_URL

embedding_model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True, device='cuda' if torch.cuda.is_available() else 'cpu')

hyde_llm = ChatOpenAI(
    openai_api_base = HYDE_LLM_URL,
    model_name = MODEL,
    n=N_HYDE_INSTANCE,
    temperature=TEMPERATURE,
    openai_api_key="None"
)

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
