import os
import glob
import json
import queue
import logging
import time

import streamlit as st
import cheshire_cat_api as ccat
from zotero_downloader import ZoteroDownloader


def on_open():
    logging.error("WebSocket connected")


def on_message(message):
    answer = json.loads(message)["content"]
    q.put(answer)


def on_error(error):
    logging.error("-"*200, error)


def on_close():
    logging.error("."*200)


@st.cache_resource
def load_cat():
    config = ccat.Config(base_url="cheshire-cat-core", port=80, user_id="42")
    cat = ccat.CatClient(config, on_message=on_message, on_open=on_open, on_close=on_close, on_error=on_error)
    return cat


@st.cache_resource
def load_queue():
    return queue.Queue()


cat = load_cat()
q = load_queue()


def connect_cat(cat, openai_api_key):
    cat.llm.upsert_llm_setting(
        language_model_name="LLMOpenAIChatConfig",
        body={
            "openai_api_key": openai_api_key,
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "streaming": False
        }
    )
    cat.connect_ws()


def download_papers(zotero_user_id, zotero_api_key, base_dir, group_limit, download_option):
    zotero_downloader = ZoteroDownloader(zotero_user_id, zotero_api_key, base_dir)
    zotero_downloader.download_pdfs(group_limit=group_limit if download_option == "Groups" else None)
    for file in glob.glob(os.path.join(base_dir, "*.pdf")):
        cat.rabbit_hole.ingest_file(file)
    st.success('Your documents have been successfully synced.')


def send_message(cat, text):
    cat.send(text)
    while True:
        if q.not_empty:
            st.session_state["answer"] = q.get()
            break
        time.sleep(1)


# Function to reset the application's state
def reset_application_state():
    # Example: Clearing session variables
    keys_to_clear = ["last_data_source", "papers", "full_text", "paper_chunks"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    print("Application state has been reset.")


# Main UI title
st.title('Zotero Scholar')
st.subheader('Simplify your research with easy document handling and querying with your Zotero files.')

base_dir = "data/zotero_papers"

# User inputs for Zotero credentials and library options
zotero_user_id = st.text_input("Enter Zotero User ID")
zotero_api_key = st.text_input("Enter Zotero API Key", type="password")
download_option = st.selectbox("Choose your Zotero library:", ["Personal Library", "Groups"])
openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
group_limit = None

# Group download limit input field
if download_option == "Groups":
    group_limit = st.number_input("Limit Group Downloads", min_value=1, max_value=10, value=2)

# Button to connect to the Cat: upsert LLM and instantiate WebSocket
_ = st.button(
    'Connect Cheshire Cat',
    on_click=connect_cat,
    kwargs={
        "cat": cat,
        "openai_api_key": openai_api_key
    }
)
_ = st.button(
    'Sync Documents',
    on_click=download_papers,
    kwargs={
        "zotero_user_id": zotero_user_id,
        "zotero_api_key": zotero_api_key,
        "base_dir": base_dir,
        "group_limit": group_limit,
        "download_option": download_option
    }
)

# Input field for the user's query
question_text = st.text_area("Ask a question about your collection of documents.", help="Type here.", key="answer")

# Button to process the query
_ = st.button(
    'Get Answer',
    on_click=send_message,
    kwargs={
        "cat": cat,
        "text": question_text
    }
)


# Button to reset the application state
if st.button('Reset Application'):
    reset_application_state()
    st.experimental_rerun()
