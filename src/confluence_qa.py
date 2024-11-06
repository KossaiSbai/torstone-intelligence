from constants import *
import time
from typing import TYPE_CHECKING

import openai
from langchain.callbacks import FileCallbackHandler
from loguru import logger

chat_history = []


if TYPE_CHECKING:
    from langchain.chains.base import Chain

chat_history = []

openai.api_key = open_ai_api_key
logfile = "output.log"

logger.add(logfile, colorize=True, enqueue=True)
handler = FileCallbackHandler(logfile)


class ConfluenceQA:
    def __init__(self,
                 qa_chain
                 ):
        self.qa_chain = qa_chain
        self.embeddings_map = {}

    def extract_chat_history(self, output, sources):
        for message in output["chat_history"][-2:]:
            role = message.type.upper()
            if role == "AI":
                chat_history.append({"role": role, "content": message.content, "sources": sources})
            else:
                chat_history.append({"role": role, "content": message.content})

        return chat_history

    def get_chat_history(self):
        return chat_history

    def answer_confluence(self, question: str):
        """
        Answer the question
        """
        curr = time.time()
        result = self.qa_chain({"question": question})
        retrieved_documents = result['source_documents']
        sources = [doc.metadata for doc in retrieved_documents]
        links = "\n ".join([source['source'] for source in sources])
        chat_history_so_far = self.extract_chat_history(result, sources)
        answer = result['answer']
        logger.info(f"Question asked: {question}")
        logger.info(f"Documents in which information was found: \n {links}")
        logger.info(f"Chat history: \n {chat_history_so_far}")
        logger.info(f"Answer to the question:\n {answer}")
        end = time.time()
        print(f"Took {round(end - curr)} seconds")
        return {"answer": answer, "chat_history": chat_history_so_far, "sources": sources}

# def display_documents(self, question):
#     search = self.vector_db_manager.similarity_search_with_score(question, k=5)
#     try:
#         st.write("This information was found in:")
#         for doc in search:
#             score = doc[1]
#             try:
#                 page_num = doc[0].metadata['page']
#             except:
#                 page_num = "txt snippets"
#             source = doc[0].metadata['source']
#             # With a streamlit expander
#             with st.expander(
#                     "Source: " + str(source) + " - Page: " + str(page_num) + "; Similarity Score: " + str(score)):
#                 st.write(doc[0].page_content)
#     except Exception as e:
#         logger.error(e)
#         logger.error("unable to get source document detail")
#
#
# def update_docs(self):
#     collection = self.vector_db_manager._client.get_collection("ConfluenceDocs")
#     collection_content = collection.get()
#     metadatas = collection_content['metadatas']
#     embedding_ids = collection_content['ids']
#     self.embeddings_map = {metadatas[i]['id']: embedding_ids[i] for i in range(len(metadatas))}
#     page_ids = self.extract_all_recently_modified_docs()
#     documents = self.load_confluence_documents_from_page_ids(page_ids)
#     texts = get_text_from_docs(documents)
#     embedding_ids_to_update = [self.embeddings_map[page_id] for page_id in page_ids]
#     self.vector_db_manager.add_texts(texts=texts, ids=embedding_ids_to_update)
