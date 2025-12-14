import streamlit as st
from wordive.controller import WordListController, WordDetailController


st.set_page_config(page_title="Wordive", layout="wide")

if "word_list_controller" not in st.session_state:
    st.session_state.word_list_controller = WordListController()

if "selected_word_id" not in st.session_state:
    st.session_state.selected_word_id = None

controller: WordListController = st.session_state.word_list_controller

if st.session_state.selected_word_id is None:
    st.title("📚 Wordive")

    search_query = st.text_input(
        "Search words", placeholder="Enter a word to search..."
    )

    words = controller.get_words(search_query if search_query else None)

    if not words:
        st.info("No words found. Please add words to the database.")
    else:
        st.subheader(f"Words ({len(words)})")

        for word in words:
            if st.button(word.word, key=f"word_{word.id}", use_container_width=True):
                st.session_state.selected_word_id = word.id
                st.rerun()
else:
    if "word_detail_controller" not in st.session_state:
        st.session_state.word_detail_controller = WordDetailController()

    detail_controller: WordDetailController = st.session_state.word_detail_controller
    word_id = st.session_state.selected_word_id

    word = detail_controller.get_word_details(word_id)

    if not word:
        st.error("Word not found.")
        st.session_state.selected_word_id = None
        st.rerun()

    st.title(f"📖 {word.word}")

    if st.button("← Back to Word List"):
        st.session_state.selected_word_id = None
        st.rerun()

    if not word.usages:
        st.info("No usages found for this word.")
    else:
        for usage in word.usages:
            st.divider()
            st.subheader(f"{usage.usage_type}")
            if usage.description:
                st.write(usage.description)

            if usage.examples:
                st.write("**Examples:**")
                for example in usage.examples:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write(f"🇬🇧 {example.english_sentence}")
                    with col2:
                        st.write(f"🇰🇷 {example.korean_sentence}")

            if usage.writing_practices:
                st.write("**Practice:**")
                for practice in usage.writing_practices:
                    with st.expander(f"{practice.korean_sentence}"):
                        user_answer = st.text_area(
                            "Write your translation:",
                            key=f"practice_{practice.id}",
                            height=100,
                        )

                        if st.button("Submit", key=f"submit_{practice.id}"):
                            if user_answer.strip():
                                detail_controller.save_attempt(practice.id, user_answer)
                                st.success("Your attempt has been saved!")
                                st.write("**Answer:**")
                                st.info(practice.english_answer)
                            else:
                                st.warning("Please write your translation first.")
