import os
import chromadb
from chromadb import Settings
from dotenv import load_dotenv
import requests

load_dotenv()

CHROMA_CLIENT = chromadb.HttpClient(
    host=os.environ["CHROMADB_HOST"],
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

    def create_collection(self, collection_name):
        return VectorDb.client.create_collection(collection_name)


if __name__ == "__main__":
    # print(get_cookies())
    print(VectorDb.list_collections())
