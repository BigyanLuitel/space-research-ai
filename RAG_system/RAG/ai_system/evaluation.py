import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def score_retrieval_relevance(question: str, docs: list) -> float:
    """
    What fraction of retrieved chunks contain
    keywords from the question.
    """
    if not docs:
        return 0.0

    # Remove common stop words so only meaningful keywords remain
    stop_words = {
        'what', 'is', 'the', 'a', 'an', 'of', 'in', 'are',
        'how', 'many', 'which', 'was', 'were', 'do', 'does',
        'did', 'to', 'for', 'and', 'or', 'on', 'at', 'by'
    }
    keywords = {
        w for w in question.lower().split()
        if w not in stop_words and len(w) > 2
    }

    if not keywords:
        return 1.0

    relevant = sum(
        1 for doc in docs
        if any(kw in doc.page_content.lower() for kw in keywords)
    )
    return round(relevant / len(docs), 2)


def score_faithfulness(answer: str, docs: list) -> float:
    """
    What fraction of sentences in the answer
    can be traced back to the retrieved context.
    """
    if not docs or not answer:
        return 0.0

    context = " ".join(doc.page_content.lower() for doc in docs)

    # Split answer into sentences (skip very short ones)
    sentences = [
        s.strip() for s in answer.split('.')
        if len(s.strip()) > 20
    ]

    if not sentences:
        return 1.0

    grounded = sum(
        1 for s in sentences
        if any(
            word in context
            for word in s.lower().split()
            if len(word) > 4
        )
    )
    return round(grounded / len(sentences), 2)


def score_completeness(answer: str) -> float:
    """
    Penalise answers that say the info is missing
    or are too short to be useful.
    """
    if not answer:
        return 0.0

    refusal_phrases = [
        'not available', 'not found', 'cannot find',
        'no information', 'not in the', 'not provided',
        'does not contain', 'not mentioned',
    ]

    if any(phrase in answer.lower() for phrase in refusal_phrases):
        return 0.3

    word_count = len(answer.split())
    if word_count < 10:
        return 0.4
    if word_count < 25:
        return 0.7

    return 1.0


def evaluate(question: str, answer: str, docs: list) -> dict:
    """
    Run all three metrics and return a combined score dict.
    Called automatically after every LLM response.
    """
    retrieval   = score_retrieval_relevance(question, docs)
    faithfulness = score_faithfulness(answer, docs)
    completeness = score_completeness(answer)
    overall      = round((retrieval + faithfulness + completeness) / 3, 2)

    metrics = {
        'timestamp':           datetime.utcnow().isoformat(),
        'question':            question[:120],
        'retrieval_relevance': retrieval,
        'faithfulness':        faithfulness,
        'completeness':        completeness,
        'overall':             overall,
    }

    logger.info(
        "EVAL — retrieval: %.2f | faithful: %.2f | complete: %.2f | overall: %.2f",
        retrieval, faithfulness, completeness, overall
    )
    return metrics