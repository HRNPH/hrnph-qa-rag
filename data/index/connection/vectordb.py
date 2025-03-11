import os
import chromadb
from chromadb import Settings
from dotenv import load_dotenv
import requests

load_dotenv()

CHROMA_CLIENT = chromadb.HttpClient(
    host=SETTING,
    ssl=True,
    port=443,
    headers={
        "Accept-Language": "en",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Safari/537.36",
        "CF-Access-Client-Id": os.environ["CHROMADB_CF_ACCESS_CLIENT_ID"],
        "CF-Access-Client-Secret": os.environ["CHROMADB_CF_ACCESS_CLIENT_SECRET"],
    },
    settings=Settings(
        chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
        chroma_client_auth_credentials=os.environ["CHROMADB_AUTH_TOKEN"],
    ),
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

    @staticmethod
    def insert(collection_name, ids, embeddings, documents, metadatas):
        index = VectorDb.client.get_collection(collection_name)
        return index.add(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )


if __name__ == "__main__":
    print(VectorDb.list_collections())
