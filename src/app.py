"""Main app definition"""
import os
import mimetypes
from typing import TYPE_CHECKING
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
from langchain_text_splitters import CharacterTextSplitter
from loguru import logger
import openai
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationalRetrievalChain
from flask_cors import CORS
from flask import request, jsonify, Flask, redirect, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from confluence_utils import load_confluence_documents_from_all_spaces, load_confluence_spaces
from utils.utils import log_message

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from VectorDbManager import VectorDbManager
from confluence_qa import ConfluenceQA
from session import ChatbotSession
from utils.sql import db
from utils.flask import htmx
from constants import persist_directory, open_ai_api_key, google_client_id, google_client_secret
from user import User

if TYPE_CHECKING:
    from langchain_community.vectorstores.chroma import Chroma  # pylint: disable=reimported

current_user: User

confluence_qa = None

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

openai.api_key = open_ai_api_key
app = Flask(__name__.split(".")[0])
# app.register_blueprint(embeddings_tester.bp)
# app.register_blueprint(llm_tuner.bp)
# app.register_blueprint(common.bp)
app.secret_key = "secret do not tell"
CORS(app, supports_credentials=True)  # if using cookies for authentication)
htmx.init_app(app)

# if 'SQLALCHEMY_DATABASE_URI' not in app.config:
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
# db.init_app(app)




def initialize_prompt_template(prompt, input_variables):
    """
    Initializes a prompt template
    """
    return PromptTemplate(
        template=prompt, input_variables=input_variables
    )


def initialize_retrieval_qa_chain(llm, vectordb):
    """
    Creates retrieval qa chain using vectordb as retriever and LLM to complete the prompt
    """

    custom_prompt_template = initialize_prompt_template(
        "You are a Confluence chatbot answering questions."
        "Use the following pieces of context and your internal knowledge to answer the question.\n"
        "If you don't know the answer, say that you don't know, don't try to make up an answer.\n\n"
        "{context}\n\n"
        "Question: {question}\n"
        "Helpful Answer:",
        ["context", "question"])
    # Inject custom prompt
    memory = ConversationSummaryBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        llm=llm,
        output_key="answer"
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": custom_prompt_template},
        return_source_documents=True,
        memory=memory,
    )


def extract_chroma_vector_db(embedding_function, force_reload: bool = False, collection_name: str = "Torstone"):
    if persist_directory and os.path.exists(persist_directory) and not force_reload:
        # Load from the persist db
        logger.info(f"Vector embedding database successfully loaded from {persist_directory}")
        return Chroma(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_function=embedding_function
        )

    else:
        client = chromadb.PersistentClient(path=persist_directory)
        return Chroma(client=client, persist_directory=persist_directory,
                      collection_name=collection_name, embedding_function=embedding_function)

vector_db = extract_chroma_vector_db(OpenAIEmbeddings(openai_api_key=open_ai_api_key), force_reload=False, collection_name="Test")
                                     
def populate_vector_db():

    def len_func(text):
        return len(text)

    docs = load_confluence_documents_from_all_spaces(load_confluence_spaces()) 
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size = 1200,
        chunk_overlap = 100,
        length_function = len_func,
        is_separator_regex= False)

    vector_db_manager = VectorDbManager(docs,  vector_db, text_splitter, OpenAIEmbeddings(openai_api_key=open_ai_api_key))
    vector_db_manager.vector_db_confluence_docs(force_reload=True)

def get_confluence_qa(force_reload=False):
    print("GETTING CONFLUENCE QA CHAIN")
    chain = initialize_retrieval_qa_chain(OpenAI(openai_api_key=open_ai_api_key), vector_db)
    if force_reload:
        populate_vector_db()
    return ConfluenceQA(
        chain
    )

@app.route('/query', methods=['POST'])
def query_agent():
    data = request.json
    response = confluence_qa.answer_confluence(data["query"])
    return jsonify({"response": response})


@app.route('/log', methods=['POST'])
def log():
    message = request.json["message"]
    log_message(message)
    return jsonify({})


@app.route("/chat-history", methods=['GET'])
def get_chat_history():
    return confluence_qa.get_chat_history()


@app.route("/current-user",  methods=['GET'])
def get_current_user():
    return jsonify(current_user)


@app.route("/current-session", methods=['GET'])
def current_session():
    if current_user is None:
        return 'None'
    session = current_user.latest_session
    return session


@app.route("/")
def index():
    if current_user.is_authenticated:
        cs = current_user.latest_session
        if cs is None:
            session = ChatbotSession(user=current_user)
            db.session.add(session)
            db.session.commit()
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.username, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


# with app.app_context():
#     db.create_all()
if __name__ == '__main__':
    confluence_qa = get_confluence_qa(True)
    app.run(host="0.0.0.0", port=8000)