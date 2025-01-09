import os
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from connection.vectordb import VectorDb

# Load environment variables
load_dotenv()


class KnowledgeBaseIngestor:
    def __init__(
        self, model_name="all-MiniLM-L6-v2", json_path="./data/knowledge-base.json"
    ):
        self.model = SentenceTransformer(model_name)
        self.json_path = json_path

    def load_data(self):
        """Load the structured knowledge base JSON file."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"{self.json_path} not found.")

        with open(self.json_path, "r") as f:
            data = json.load(f)
        return data

    def create_embeddings(self, title, content):
        """Create an embedding from the title and content."""
        combined_text = f"{title}. {content}"
        embedding = self.model.encode(combined_text)
        return embedding

    def ingest_to_chromadb(self, collection_name="v1-personal-all-MiniLM-L6-v2"):
        """Ingest the knowledge base into ChromaDB."""
        # Create collection in ChromaDB
        try:
            VectorDb.create_collection(collection_name)
        except Exception as e:
            print(f"Collection '{collection_name}' already exists, Deleting it?")
            delete_collection = input("Delete collection? [y/n]: ")
            if delete_collection.lower() == "y":
                VectorDb.delete_collection(collection_name)
                VectorDb.create_collection(collection_name)
            else:
                print("Exiting...")
                return

        # Load data
        data = self.load_data()

        # Prepare data for insertion
        ids = [str(entry["id"]) for entry in data]
        documents = [f"{entry['title']}. {entry['content']}" for entry in data]
        print(f"Creating embeddings for {len(data)} documents...")
        embeddings = [
            self.create_embeddings(entry["title"], entry["content"]) for entry in data
        ]
        metadata = [entry["metadata"] for entry in data]
        # Fix "tags" key in metadata to be str instead of list by joining the list
        for entry in metadata:
            entry["tags"] = ",".join(entry["tags"])

        # Insert data into ChromaDB
        VectorDb.insert(collection_name, ids, embeddings, documents, metadata)
        print(f"Data successfully ingested into collection '{collection_name}'.")

        # Try and list the collections
        print(VectorDb.list_collections())

    def search_loop(self, collection_name="v1-personal-all-MiniLM-L6-v2"):
        """Search loop for querying the knowledge base."""
        while True:
            query = input("Enter query: ")
            if query.lower() == "exit":
                break
            collection = VectorDb.client.get_collection(collection_name)
            q_embed = self.create_embeddings(query, query)
            search_results = collection.query(q_embed, n_results=3)

            print(json.dumps(search_results, indent=4))


if __name__ == "__main__":
    ingestor = KnowledgeBaseIngestor()
    # ingestor.ingest_to_chromadb()
    ingestor.search_loop()
