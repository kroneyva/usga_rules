import streamlit as st

from .config import load_settings
from .ollama_client import ask_ollama, build_chat_prompt, resolve_ollama_model
from .quiz import generate_quiz
from .rules import load_rules
from .search import build_search_index, retrieval_only_answer, search_rules


def main() -> None:
    settings = load_settings()

    st.set_page_config(page_title="USGA Rules Assistant", layout="wide")
    st.title("USGA Rules of Golf Assistant")
    st.caption("Small-model assistant with rule lookup, chat, and quiz.")

    records = load_rules(settings)
    if not records:
        st.error("No rules dataset found. Add data to data/rules_dataset.json or data/rules_seed.json")
        st.stop()

    vectorizer, matrix = build_search_index(records)

    tab_chat, tab_search, tab_quiz = st.tabs(["Chatbot", "Rule Lookup", "Quiz"])

    with tab_chat:
        st.subheader("Q&A Chatbot")
        st.write("Uses retrieval + Ollama for grounded answers.")
        use_ollama = st.toggle("Use Ollama generation", value=True)
        if use_ollama:
            st.caption(f"Configured Ollama endpoint: {settings.ollama_base_url}")
            st.caption(
                f"Request timeout: {settings.ollama_timeout}s | Max tokens: {settings.ollama_num_predict}"
            )

        question = st.text_input(
            "Ask a rules question",
            placeholder="Can I declare my ball unplayable in a bunker?",
        )

        if st.button("Get Answer", type="primary"):
            if not question.strip():
                st.warning("Enter a question first.")
            else:
                retrieved = search_rules(question, records, vectorizer, matrix, top_k=4)
                if use_ollama:
                    try:
                        selected_model, available_models, configured_model_missing = resolve_ollama_model(settings)
                        if configured_model_missing:
                            st.info(
                                f"Configured model '{settings.ollama_model}' not found. "
                                f"Using '{selected_model}' instead."
                            )
                        st.caption(f"Using model: {selected_model}")
                        st.caption(f"Available models: {', '.join(available_models)}")

                        prompt = build_chat_prompt(question, retrieved)
                        with st.spinner("Waiting for Ollama response..."):
                            answer = ask_ollama(settings, selected_model, prompt)
                    except Exception as exc:
                        st.warning(f"Ollama call failed ({exc}). Falling back to retrieval-only mode.")
                        answer = retrieval_only_answer(retrieved)
                else:
                    answer = retrieval_only_answer(retrieved)

                st.markdown("### Answer")
                st.write(answer)

                if retrieved:
                    st.markdown("### Retrieved References")
                    for item in retrieved:
                        st.write(f"{item['id']} - {item['title']} (score: {item['score']:.3f})")
                        if item["source"]:
                            st.write(f"Source: {item['source']}")

    with tab_search:
        st.subheader("Rule Lookup")
        query = st.text_input("Search by keyword", key="search_query", placeholder="penalty area relief")
        top_k = st.slider("Results", min_value=1, max_value=10, value=5)
        if query:
            results = search_rules(query, records, vectorizer, matrix, top_k=top_k)
            if not results:
                st.info("No matching rules found.")
            else:
                for item in results:
                    with st.expander(f"{item['id']} - {item['title']} (score: {item['score']:.3f})"):
                        st.write(item["text"])
                        if item["source"]:
                            st.write(f"Source: {item['source']}")

    with tab_quiz:
        st.subheader("Rules Quiz")
        if "quiz_items" not in st.session_state:
            st.session_state.quiz_items = generate_quiz(records, n=5)
            st.session_state.quiz_score = 0
            st.session_state.answered = set()

        if st.button("New Quiz"):
            st.session_state.quiz_items = generate_quiz(records, n=5)
            st.session_state.quiz_score = 0
            st.session_state.answered = set()

        for idx, item in enumerate(st.session_state.quiz_items):
            st.markdown(f"**Q{idx + 1}.** {item['question']}")
            selected = st.radio(
                "Choose one",
                options=item["options"],
                key=f"quiz_{idx}",
                index=None,
                label_visibility="collapsed",
            )
            if st.button("Submit", key=f"submit_{idx}"):
                if idx in st.session_state.answered:
                    st.info("You already submitted this question.")
                elif selected is None:
                    st.warning("Select an option before submitting.")
                else:
                    st.session_state.answered.add(idx)
                    if selected == item["answer"]:
                        st.session_state.quiz_score += 1
                        st.success("Correct")
                    else:
                        st.error(f"Incorrect. Correct answer: {item['answer']}")

        st.markdown(f"### Score: {st.session_state.quiz_score} / {len(st.session_state.quiz_items)}")
