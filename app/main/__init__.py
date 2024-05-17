from flask import Flask
from pymilvus import connections
from pymilvus.model import DefaultEmbeddingFunction

from .config import config_by_name


embedding_model = DefaultEmbeddingFunction()


def create_app(config_name:str):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # connect to milvus
    connections.connect(uri=config_by_name[config_name].MILVUS_URI)

    # register blueprints
    # routes need to be imported inside to avoid conflict
    from .route import document_route
    app.register_blueprint(document_route.blueprint)

    print(f"The app is running in {config_name} environment")

    return app