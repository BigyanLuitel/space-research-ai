import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "chroma_db"


def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_vectorstore(collection_name):
    path = os.path.join(CHROMA_DIR, collection_name)
    os.makedirs(path, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=path,
    )


def split_documents(documents):
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    ).split_documents(documents)


def ingest_pdf(uploaded_file, collection_name):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    for chunk in uploaded_file.chunks():
        tmp.write(chunk)
    tmp.close()

    try:
        loader = PyPDFLoader(tmp.name)
        documents = loader.load()
        chunks = split_documents(documents)
        vs = get_vectorstore(collection_name)
        vs.add_documents(chunks)
        return len(chunks), len(documents)
    finally:
        os.unlink(tmp.name)