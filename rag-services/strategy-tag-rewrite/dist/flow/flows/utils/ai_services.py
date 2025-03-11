import os
from typing import Dict, List
from chromadb import QueryResult
import openai
from flows.utils.services.config import SETTING
from flows.utils.services.vectordb import VectorDb
from promptflow.tracing import start_trace

start_trace(collection="hrnph-rag-tag-rw")

OPENAI_CLIENT = openai.Client(
    api_key=SETTING.openai_api_key,
    base_url=SETTING.openai_base_url,
    websocket_base_url=SETTING.openai_websocket_base_url,
    default_headers={
        "Accept-Language": "en",
        "CF-Access-Client-Id": SETTING.chromadb_cf_access_client_id,
        "CF-Access-Client-Secret": SETTING.chromadb_cf_access_client_secret,
    },
)


class AIServices:
    OPENAI_CLIENT: openai.Client = OPENAI_CLIENT

    @staticmethod
    def search_by_tags(collection_name: str, tags: List[str], top_k: int = 3):
        """Query ChromaDB collection and return results."""
        results = VectorDb.search_by_type(collection_name, tags, top_k)
        return results


if __name__ == "__main__":
    collection_name = SETTING.target_collection_name
    print(AIServices.search_by_tag(collection_name, ["technologies"]))
