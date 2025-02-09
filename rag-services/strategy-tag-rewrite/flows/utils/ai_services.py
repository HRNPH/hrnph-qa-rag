import os
from typing import Dict, List
from chromadb import QueryResult
import openai
from flows.utils.services.vectordb import VectorDb
from promptflow.tracing import start_trace

start_trace(collection="hrnph-rag-tag-rw")

OPENAI_CLIENT = openai.Client(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_API_BASE_URL", None),
    websocket_base_url=os.environ.get("OPENAI_WEBSOCKET_BASE_URL", None),
    default_headers={
        "Accept-Language": "en",
        "CF-Access-Client-Id": os.environ["CHROMADB_CF_ACCESS_CLIENT_ID"],
        "CF-Access-Client-Secret": os.environ["CHROMADB_CF_ACCESS_CLIENT_SECRET"],
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
    collection_name = os.environ["TARGET_COLLECTION_NAME"]
    print(AIServices.search_by_tag(collection_name, ["technologies"]))
