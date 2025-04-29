import bm25s
from termcolor import colored
from ..types import Email


def email_retrieval(corpus: list[Email], query: str, k: int = 5) -> list[Email]:
    processed_emails = [email.content for email in corpus]

    retriever = bm25s.BM25(corpus=processed_emails)
    retriever.index(bm25s.tokenize(processed_emails))
    results, _ = retriever.retrieve(bm25s.tokenize(query), k=k, sorted=True)

    retrieved_emails = []
    for result in results[0, :]:  # Extract document indices
        i = retriever.corpus.index(result)
        retrieved_emails.append(corpus[i])

    return retrieved_emails
