import os
import logging
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from .ingest import get_vectorstore

load_dotenv(override=True)

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
RETRIEVAL_K = 4

llm = ChatGroq(model=MODEL_NAME, api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are a helpful assistant for answering questions about space research.
Use the retrieved context below to answer the question accurately.
If the answer is not in the context, say clearly:
"This information is not available in the uploaded document."
Never make up facts or hallucinate information.

Retrieved context:
{context}
"""


def build_retrieval_query(question: str, history: list[dict]) -> str:
    """Combine last user message with current question for better retrieval."""
    recent = [m["content"] for m in history if m.get("role") == "user"]
    if recent:
        return recent[-1] + " " + question
    return question


def fetch_context(question: str, collection_name: str) -> list[Document]:
    """Retrieve top-k relevant chunks from vectorstore."""
    vs = get_vectorstore(collection_name)
    retriever = vs.as_retriever(search_kwargs={"k": RETRIEVAL_K})
    docs = retriever.invoke(question)
    for i, doc in enumerate(docs):
        logger.info("chunk[%d]: %s", i, doc.page_content[:100])
    return docs


def answer_question(
    question: str,
    collection_name: str,
    history: list[dict] = []
) -> tuple[str, list[Document]]:

    logger.info("RAG query: %s", question)

    try:
        query = build_retrieval_query(question, history)
        docs = fetch_context(query, collection_name)
        context = "\n\n".join(doc.page_content for doc in docs)

        messages = [SystemMessage(content=SYSTEM_PROMPT.format(context=context))]

        # convert history manually — no convert_to_messages needed
        for h in history:
            if h.get("role") == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h.get("role") == "assistant":
                messages.append(AIMessage(content=h["content"]))

        messages.append(HumanMessage(content=question))

        response = llm.invoke(messages)
        return response.content, docs

    except Exception as e:
        logger.error("Error in answer_question: %s", str(e), exc_info=True)
        raise