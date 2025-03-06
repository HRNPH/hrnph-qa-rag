import os
from typing import Dict, List, Optional
import chromadb
from chromadb import Settings
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

CHROMA_CLIENT = chromadb.HttpClient(
    host=os.environ["CHROMADB_HOST"],
    ssl=True,
    port=443,
    headers={
        "Accept-Language": "en",
        "CF-Access-Client-Id": os.environ["CHROMADB_CF_ACCESS_CLIENT_ID"],
        "CF-Access-Client-Secret": os.environ["CHROMADB_CF_ACCESS_CLIENT_SECRET"],
    },
    settings=Settings(
        chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
        chroma_client_auth_credentials=os.environ["CHROMADB_AUTH_TOKEN"],
    ),
)


class DocumentModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the document.")
    document: str = Field(..., description="The textual content of the document.")
    title: Optional[str] = Field(
        ..., description="Title of the document, if available."
    )
    tags: List[str] = Field(
        default_factory=list, description="List of tags associated with the document."
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None, description="Additional metadata as key/value pairs."
    )


class VectorDb:
    client = CHROMA_CLIENT

    @staticmethod
    def list_collections():
        return VectorDb.client.list_collections()

    @staticmethod
    def create_collection(collection_name):
        return VectorDb.client.create_collection(collection_name)

    @staticmethod
    def delete_collection(collection_name):
        return VectorDb.client.delete_collection(collection_name)

    # @staticmethod
    # def search_with_embedding(collection_name, embedding: List[float], top_k: int = 3):
    #     collection = VectorDb.client.get_collection(collection_name)
    #     return collection.query(embedding, n_results=top_k)

    @staticmethod
    def search_by_type(
        collection_name: str,
        types: List[str],
        top_k: int = 3,
    ) -> List[DocumentModel]:
        """
        Query ChromaDB collection and return results.
        :param collection_name: Name of the collection to query
        :param types: List of type of documents to search for
        :param top_k: Limit Number of results to return
        :return: List of dicts containing document, metadata, and match_count
        """
        collection = VectorDb.client.get_collection(collection_name)

        # Step 1: Query to find all documents with ANY tag from `tags`
        results = collection.get(
            where={"type": {"$in": types}},
            limit=top_k,
            include=["documents", "metadatas", "uris"],
        )

        # print(results)

        # If there are no documents, just return an empty list
        if not results["documents"]:
            return []

        # Extract the lists from the first (and only) query group
        id_list = results["ids"] if results["ids"] else []
        doc_list = results["documents"]
        meta_list = results["metadatas"] if results["metadatas"] else []

        items = []

        # Step 2: Build a list of dicts with match_count
        for doc_id, doc, meta in zip(id_list, doc_list, meta_list):
            items.append(
                {
                    "id": doc_id,
                    "title": meta.get("title"),
                    "document": doc,
                    "metadata": meta,
                    "tags": meta.get("tags").split(",") if meta.get("tags") else [],
                }
            )

        # Parse the items to Pydantic DocumentModel
        items = [DocumentModel(**item) for item in items]

        return items


if __name__ == "__main__":
    TARGET_COLLECTION_NAME = os.environ["TARGET_COLLECTION_NAME"]
    print(
        VectorDb.search_by_type(
            TARGET_COLLECTION_NAME, ["personal_trait", "ai"], top_k=1000
        )
    )
