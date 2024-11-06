from random import choice
import chromadb
from constants import persist_directory

def get_rand_frag() -> str:
    """Get a random text fragment from the database."""
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_collection("Torstone")
    return choice(collection.get()["documents"])


__all__ = ["get_rand_frag"]
