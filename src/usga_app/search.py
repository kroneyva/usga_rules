from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_search_index(records: list[dict]):
    documents = []
    for item in records:
        keywords = " ".join(item.get("keywords", []))
        documents.append(f"{item.get('title', '')}\n{item.get('text', '')}\n{keywords}")

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents) if documents else None
    return vectorizer, matrix


def search_rules(query: str, records: list[dict], vectorizer, matrix, top_k: int = 5) -> list[dict]:
    if not query or matrix is None:
        return []

    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, matrix)[0]
    ranked_ids = scores.argsort()[::-1][:top_k]

    results = []
    for idx in ranked_ids:
        score = float(scores[idx])
        if score <= 0:
            continue
        item = records[idx]
        results.append(
            {
                "id": item.get("id", ""),
                "title": item.get("title", "Untitled"),
                "text": item.get("text", ""),
                "source": item.get("source", ""),
                "score": score,
            }
        )
    return results


def retrieval_only_answer(retrieved: list[dict]) -> str:
    if not retrieved:
        return (
            "I could not find matching rules in the loaded dataset. "
            "Try a more specific question or load a richer USGA rules dataset."
        )

    best = retrieved[0]
    answer = [
        f"Best match: {best['id']} - {best['title']}",
        best["text"],
    ]
    if best.get("source"):
        answer.append(f"Source: {best['source']}")
    answer.append("For official wording, verify against current USGA rules pages.")
    return "\n\n".join(answer)
