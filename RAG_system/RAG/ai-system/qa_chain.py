from xml.dom.minidom import Document

from chromadb import logger
from langchain_core import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage,convert_to_messages
from langchain_core import documents
from dotenv import load_dotenv
import os

load_dotenv(override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
DB_COLLECTION_NAME = os.getenv("DB_COLLECTION_NAME", "collection_name")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
RETRIVAL_K = 4

SYSTEM_PROMPT = """
You are a helpful assistant for answering questions about space research. 
You have access to a vector database that contains documents related to space research. When a user asks a question, you should retrieve relevant documents from the vector database and use them to provide a comprehensive answer. If you cannot find relevant information in the vector database, you should answer based on your general knowledge of space research.

When retrieving documents from the vector database, you should use the following format:
"""
vector_store = Chroma(persist_directory="chroma_db", collection_name=DB_COLLECTION_NAME, embedding_function=embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": RETRIVAL_K})
llm = ChatGroq(model=MODEL_NAME, api_key=GROQ_API_KEY)


def combined_question_context_prompt(question: str, history: list[dict]=[]) -> str:
    """Build retrieval query from the question + only the last user message for context."""
    # Only use the most recent user turn (if any) to add retrieval context,
    # to avoid diluting the semantic signal with the full conversation.
    recent_user_msgs = [m["content"] for m in history if m.get("role") == "user"]
    if recent_user_msgs:
        return recent_user_msgs[-1] + " " + question
    return question

def fetch_context(question: str) -> list[Document]:
    """Retrieve top-k documents by similarity. Logs content previews."""
    docs = retriever.invoke(question)
    for i, doc in enumerate(docs):
        logger.info("  chunk[%d]: %s", i, doc.page_content[:100])
    return docs

def answer_question(question: str, history: list[dict]=[]) -> tuple[str, list[Document]]:
    logger.info("RAG query: %s", question)
    try:
        combined = combined_question_context_prompt(question, history)
        docs = fetch_context(combined)
        context = "\n\n".join(doc.page_content for doc in docs)
        system_prompt = SYSTEM_PROMPT.format(context=context)
        messages = [SystemMessage(content=system_prompt)]
        messages.extend(convert_to_messages(history))
        messages.append(HumanMessage(content=question))
        response = llm.invoke(messages)
        return response.content, docs
    except Exception as e:
        logger.error("Error in answer_question: %s", str(e), exc_info=True)
        raise
