import streamlit as st
from wordive.ai_helper import get_word_usages, get_example_sentences, get_feedback

# --- App Title ---
st.title("Wordive")

# --- Word Input ---
word = st.text_input("Enter an English word:", "have")

if st.button("Get Usages"):
    # Store the usages in the session state to persist them
    st.session_state.usages = get_word_usages(word)
    st.session_state.word = word
    # Clear previous sentences and translations when a new word is submitted
    for key in list(st.session_state.keys()):
        if key.startswith("sentences_") or key.startswith("user_translations_"):
            del st.session_state[key]


# --- Display Usages and Translation Practice ---
if "usages" in st.session_state:
    usages = st.session_state.usages
    if "Error" in usages:
        st.error(usages["Error"])
    else:
        for i, (usage_type, description) in enumerate(usages.items()):
            with st.expander(f"{usage_type}: {description}"):
                # Use a unique key for the button based on the usage_type
                if st.button("Request Korean Sentences", key=f"btn_{i}"):
                    # Store sentences in session state
                    st.session_state[f"sentences_{i}"] = get_example_sentences(
                        usage_type
                    )
                    # Initialize a list to hold the translations for this usage
                    st.session_state[f"user_translations_{i}"] = [""] * len(
                        st.session_state[f"sentences_{i}"]
                    )

                # Check if sentences for this usage are in the session state
                if f"sentences_{i}" in st.session_state:
                    sentences = st.session_state[f"sentences_{i}"]
                    user_translations = st.session_state[f"user_translations_{i}"]

                    for j, sentence in enumerate(sentences):
                        st.write(f"**Translate this sentence:** {sentence}")
                        # The user's translation is stored in the list
                        user_translations[j] = st.text_input(
                            "Your English translation:",
                            value=user_translations[j],
                            key=f"trans_{i}_{j}",
                        )

                    if st.button("Submit All Translations", key=f"submit_all_{i}"):
                        all_filled = all(user_translations)
                        if all_filled:
                            st.write("---")
                            st.subheader("Feedback")
                            for j, (korean_sent, user_trans) in enumerate(
                                zip(sentences, user_translations)
                            ):
                                feedback = get_feedback(user_trans, korean_sent)
                                st.write(f"**Original:** {korean_sent}")
                                st.write(f"**Your Translation:** {user_trans}")
                                st.success(f"**Feedback:** {feedback}")
                                st.write("---")
                        else:
                            st.warning(
                                "Please fill in all translation fields before submitting."
                            )
