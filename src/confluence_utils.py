import os
import pathlib
import pickle
import datetime

from langchain.document_loaders.confluence import ContentFormat

from constants import *
from loguru import logger

__all__ = [
    'load_confluence_spaces',
    'load_confluence_documents',
    'load_confluence_documents_from_page_ids',
    'get_text_from_docs',
    'load_confluence_documents_from_all_spaces',
    'extract_all_recently_modified_docs'
]


def load_confluence_spaces():
    spaces = CONFLUENCE.get_all_spaces(start=0, limit=500, expand="homepage")['results']
    return [space['key'] for space in spaces]


def load_confluence_documents(space_key):
    return CONFLUENCE_LOADER.load(space_key=space_key, content_format=ContentFormat.VIEW)


def load_confluence_documents_from_page_ids(page_ids):
    return CONFLUENCE_LOADER.load(page_ids=page_ids)


def get_text_from_docs(docs):
    return [doc.page_content for doc in docs]


def load_confluence_documents_from_all_spaces(target_spaces):
    filename = pathlib.Path(global_dirs.user_cache_dir) / "confluence-docs.pk"
    filename.parent.mkdir(parents=True, exist_ok=True)
    if os.path.isfile(filename):
        with open(filename, 'rb') as fi:
            return pickle.load(fi)
    # space_keys = load_confluence_spaces()
    all_docs = []
    for space_key in target_spaces:
        logger.info(f"Loading documents from space with key {space_key}")
        confluence_docs = load_confluence_documents(space_key)
        logger.info(f"Loaded {len(confluence_docs)} documents from space with key {space_key}")
        confluence_docs = list(filter(lambda doc: 'overview' not in doc.metadata['source'], confluence_docs))
        all_docs.extend(confluence_docs)
    # open a pickle file
    with open(filename, 'wb') as fi:
        # dump your data into the file
        pickle.dump(all_docs, fi)
    logger.info(f"Loaded {len(all_docs)} documents from {confluence_domain}")
    return all_docs


def extract_all_recently_modified_docs(self):
    all_docs = self.load_confluence_documents_from_all_spaces()
    page_ids = [doc.metadata["id"] for doc in all_docs]
    last_updated_dates = {}
    for page_id in page_ids:
        history = CONFLUENCE.history(page_id)
        last_updated_dates[page_id] = (
            datetime.datetime.strptime(history["lastUpdated"]["when"][0:10], "%Y-%m-%d").strftime("%Y-%m-%d"))
    sorted_last_updated = dict(sorted(last_updated_dates.items(), key=lambda x: x[1], reverse=True))
    date = list(sorted_last_updated.items())[0][1]
    docs_to_update = list({k: v for k, v in sorted_last_updated.items() if v == date}.keys())
    return docs_to_update

def make_safe(string):
    return "".join(c for c in string if c.isalpha() or c.isdigit() or c==' ').strip()

def get_docs():
    docs = load_confluence_documents_from_all_spaces(['INF','RD'])

    for doc in docs:
        title = doc.metadata["title"]
        doc_id = doc.metadata["id"]
        filename = make_safe(f"{title} {doc_id}")+".md"
        content = "# " + title + "\n\n" + doc.page_content

        with open(f"docs/{filename}", "w", encoding='utf-16') as f:
            f.write(content)