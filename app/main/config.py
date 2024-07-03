import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    DEBUG = False


class DevelopmentConfig(Config):
    # using milvus database
    DEBUG = True
    MILVUS_URI = os.getenv('MILVUS_URI_DEV')
    MILVUS_USER = os.getenv('MILVUS_USERNAME')
    MILVUS_PASSWORD = os.getenv('MILVUS_PASSWORD')
    MILVUS_DB_NAME = os.getenv('MILVUS_DB_NAME')


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MILVUS_URI = os.getenv('MILVUS_URI_TEST')


class ProductionConfig(Config):
    DEBUG = False
    MILVUS_URI = os.getenv('MILVUS_URI_PROD')


config_by_name = dict(
    dev = DevelopmentConfig,
    test=TestingConfig,
    prod = ProductionConfig
)


key = Config.SECRET_KEY