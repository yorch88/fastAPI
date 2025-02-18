from elasticsearch import Elasticsearch
from app.config import settings

def get_es_client():
    return Elasticsearch(settings.ELASTICSEARCH_HOST)
