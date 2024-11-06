
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import TextSplitter
from langchain.vectorstores import VectorStore
from loguru import logger
from confluence_utils import load_confluence_documents_from_all_spaces, load_confluence_spaces
from constants import open_ai_api_key, persist_directory



class VectorDbManager:
    """
    Manages the vector database for the embeddings
    """

    def __init__(self, docs, vectordb: VectorStore, text_splitter: TextSplitter, embedding_extractor: Embeddings):
        self.vectordb = vectordb
        self.text_splitter = text_splitter
        self.docs = docs
        self.embedding_extractor = embedding_extractor

    def vector_db_confluence_docs(self, force_reload: bool = False) -> None:
        """
        creates vector db for the embeddings and persists them or loads a vector db from the persist directory
        """

        if force_reload:
            logger.info("Loading Confluence documents")
            documents = load_confluence_documents_from_all_spaces(['INF'])
            logger.info("Splitting texts")

            split_documents = self.text_splitter.split_documents(documents)

            texts = [doc.page_content for doc in split_documents]
            batch_size = 50
            metadatas = [doc.metadata for doc in split_documents]
            self.process_batches(texts, batch_size, metadatas)

            logger.info(f"Vector embedding database successfully created and stored in {persist_directory}")

    def process_batches(self, texts, batch_size, metadatas):
        """Batch process the texts and metadatas"""
        for i in range(0, len(texts), batch_size):
            logger.info(f"Processing batch from {i} to {i + batch_size}")
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            self.add_documents_batch_to_vector_db(batch_texts, batch_metadatas)

    def add_documents_batch_to_vector_db(self, batch_texts, batch_metadatas):
        logger.info("Storing batch in vector database")
        self.vectordb.add_texts(batch_texts, batch_metadatas)
        logger.info("Batch stored successfully")