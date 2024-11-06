import os
from atlassian import Confluence
from langchain_community.document_loaders import ConfluenceLoader
from settings import (
    OPEN_AI_API_KEY,
    CONFLUENCE_DOMAIN,
    CONFLUENCE_USERNAME,
    CONFLUENCE_API_KEY,
    PERSIST_DIRECTORY,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    LLM_OPENAI_MODEL,
    EMBEDDING_TEST_DATA,
)
from appdirs import AppDirs

__all__ = [
    'confluence_domain',
    'confluence_username',
    'confluence_api_key',
    'confluence_url',
    'persist_directory',
    'embedding_test_data',
    'global_dirs',
    'open_ai_model',
    'open_ai_api_key',
    'CONFLUENCE_LOADER',
    'CONFLUENCE'
]
confluence_url = f"{CONFLUENCE_DOMAIN}wiki/"
global_dirs = AppDirs('Torstone Expert', "Torstone", "0.0.1")
open_ai_api_key = OPEN_AI_API_KEY
confluence_domain = CONFLUENCE_DOMAIN
confluence_username = CONFLUENCE_USERNAME
confluence_api_key = CONFLUENCE_API_KEY
persist_directory = PERSIST_DIRECTORY
embedding_test_data = EMBEDDING_TEST_DATA
open_ai_model = LLM_OPENAI_MODEL
google_client_id = GOOGLE_CLIENT_ID
google_client_secret = GOOGLE_CLIENT_SECRET

CONFLUENCE_LOADER = ConfluenceLoader(
    url=confluence_url,
    username=CONFLUENCE_USERNAME,
    api_key=CONFLUENCE_API_KEY,
    number_of_retries=5,
    max_retry_seconds=120,
)

CONFLUENCE = Confluence(
    url=CONFLUENCE_DOMAIN,
    username=CONFLUENCE_USERNAME,
    password=CONFLUENCE_API_KEY
)
