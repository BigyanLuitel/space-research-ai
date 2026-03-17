import os
import glob
from pathlib import Path
from dotenv import load_dotenv
from langchain_community import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import PyPDFLoader # type: ignore

CHROMA_DIR = "chroma_db"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
def get_vector_store():
    return Chroma(collection_name="collection_name", embedding_function=get_embeddings(), persist_directory=CHROMA_DIR)

def ingest_data(data_dir):
    # Load documents from the specified directory
    loader = PyPDFLoader(data_dir)
    documents = loader.load()

    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    # Create or load the vector store
    vector_store = get_vector_store()

    # Add documents to the vector store
    vector_store.add_documents(chunks)

    # Persist the vector store to disk
    vector_store.persist()

