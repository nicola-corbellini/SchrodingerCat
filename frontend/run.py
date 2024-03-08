import time
import streamlit as st
import cheshire_cat_api as ccat
from utils.zotero_downloader import ZoteroDownloader


def on_message(message):
    pass


config = ccat.Config(port=80, user_id="streamlit")
cat = ccat.CatClient(config, on_message=on_message)


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
if st.button('Connect Cheshire Cat'):
    if not cat.is_ws_connected:
        cat.connect_ws()
    # TODO upsert llm

# Button to initiate document sync from Zotero
if st.button('Sync Documents'):
    zotero_downloader = ZoteroDownloader(zotero_user_id, zotero_api_key, base_dir)
    zotero_downloader.download_pdfs(group_limit=group_limit if download_option == "Groups" else None)
    # TODO ingest files in the rabbit hole
    st.success('Your documents have been successfully synced.')

# Input field for the user's query
question_text = st.text_area("Ask a question about your collection of documents.", help="Type here.")

# Button to process the query
if st.button('Get Answer'):
    pass
    # TODO send ws message and get the answer

# Button to reset the application state
if st.button('Reset Application'):
    reset_application_state()
    st.experimental_rerun()
