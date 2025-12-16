import streamlit as st
from wordive.controller import (
    WordListController,
    WordDetailController,
    WordImportController,
    WritingPracticeQuizController,
)


st.set_page_config(page_title="Wordive", layout="wide")

if "word_list_controller" not in st.session_state:
    st.session_state.word_list_controller = WordListController()

if "word_import_controller" not in st.session_state:
    st.session_state.word_import_controller = WordImportController()

if "quiz_controller" not in st.session_state:
    st.session_state.quiz_controller = WritingPracticeQuizController()

if "selected_word_id" not in st.session_state:
    st.session_state.selected_word_id = None

if "show_add_modal" not in st.session_state:
    st.session_state.show_add_modal = False

if "current_quiz_practice" not in st.session_state:
    st.session_state.current_quiz_practice = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_user_answer" not in st.session_state:
    st.session_state.quiz_user_answer = ""

controller: WordListController = st.session_state.word_list_controller
import_controller: WordImportController = st.session_state.word_import_controller
quiz_controller: WritingPracticeQuizController = st.session_state.quiz_controller

if st.session_state.selected_word_id is None:
    st.title("📚 Wordive")

    # Quiz section
    st.markdown("---")
    st.subheader("📝 Daily Quiz")

    # Initialize or get current quiz practice
    if st.session_state.current_quiz_practice is None:
        practice = quiz_controller.get_recent_practice()
        if practice is None:
            practice = quiz_controller.get_random_practice()
        st.session_state.current_quiz_practice = practice
        st.session_state.quiz_submitted = False

    current_practice = st.session_state.current_quiz_practice

    if current_practice:
        st.write("**Translate to English:**")
        st.info(f"🇰🇷 {current_practice.korean_sentence}")

        if not st.session_state.quiz_submitted:
            user_answer = st.text_area(
                "Write your translation:",
                key="quiz_answer",
                height=100,
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Submit", key="quiz_submit", use_container_width=True):
                    if user_answer.strip():
                        quiz_controller.save_quiz_attempt(
                            current_practice.id, user_answer
                        )
                        st.session_state.quiz_user_answer = user_answer
                        st.session_state.quiz_submitted = True
                        st.rerun()
                    else:
                        st.warning("Please write your translation first.")
            with col2:
                if st.button(
                    "🔄 Another Practice", key="quiz_another", use_container_width=True
                ):
                    practice = quiz_controller.get_random_practice()
                    if practice:
                        st.session_state.current_quiz_practice = practice
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_user_answer = ""
                        st.rerun()
        else:
            st.write("**Your answer:**")
            st.write(st.session_state.quiz_user_answer)
            st.write("**Correct answer:**")
            st.success(f"🇬🇧 {current_practice.english_answer}")

            if st.button("🔄 Another Practice", key="quiz_another_after"):
                practice = quiz_controller.get_random_practice()
                if practice:
                    st.session_state.current_quiz_practice = practice
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_user_answer = ""
                    st.rerun()
    else:
        st.info(
            "No writing practices available. Please add words with writing practices first."
        )

    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search words", placeholder="Enter a word to search..."
        )
    with col2:
        if st.button("➕ Add New Word", use_container_width=True):
            st.session_state.show_add_modal = True

    # Add word modal
    if st.session_state.show_add_modal:
        with st.container():
            st.markdown("---")
            st.subheader("Add New Word from JSON")
            st.markdown(
                """
                **JSON Format:**
                ```json
                {
                  "word": "example",
                  "usages": [
                    {
                      "usage_type": "noun",
                      "description": "A thing characteristic of its kind",
                      "examples": [
                        {
                          "english_sentence": "This is an example.",
                          "korean_sentence": "이것은 예시입니다."
                        }
                      ],
                      "writing_practices": [
                        {
                          "korean_sentence": "이것은 예시입니다.",
                          "english_answer": "This is an example."
                        }
                      ]
                    }
                  ]
                }
                ```
                """
            )

            json_input = st.text_area(
                "Paste JSON here:",
                height=300,
                key="json_input",
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✅ Import", use_container_width=True):
                    if json_input.strip():
                        try:
                            word = import_controller.import_word_from_json(json_input)
                            st.success(f"Successfully imported word: {word.word}")
                            st.session_state.show_add_modal = False
                            if "json_input" in st.session_state:
                                del st.session_state.json_input
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Error: {e}")
                        except Exception as e:
                            st.error(f"Unexpected error: {e}")
                    else:
                        st.warning("Please paste JSON data first.")
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_add_modal = False
                    if "json_input" in st.session_state:
                        del st.session_state.json_input
                    st.rerun()

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
