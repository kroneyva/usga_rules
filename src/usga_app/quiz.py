import random


def generate_quiz(records: list[dict], n: int = 5) -> list[dict]:
    if len(records) < 2:
        return []

    sample = random.sample(records, k=min(n, len(records)))
    quiz = []
    for correct in sample:
        distractors = [r for r in records if r["id"] != correct["id"]]
        distractor_titles = [d["title"] for d in random.sample(distractors, k=min(3, len(distractors)))]

        options = distractor_titles + [correct["title"]]
        random.shuffle(options)

        quiz.append(
            {
                "question": f"Which rule best matches: {correct['text'][:150]}...",
                "options": options,
                "answer": correct["title"],
            }
        )
    return quiz
