import streamlit as st
from dotenv import load_dotenv

# Import models from all apps to ensure they are registered with SQLModel's metadata

from database import init_db

# Initialize the database and create tables
load_dotenv()
init_db()

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# 🎮 Welcome to the Playground!")
st.subheader("Build. Experiment. Learn.")

st.markdown(
    """
    This is personal **Streamlit playground** —  
    a space where you can quickly test out ideas, visualize data, or prototype new features.

    👉 Use the **sidebar** to explore different mini-apps or create your own.  
    👉 Everything you change updates in real-time.  
    """
)
