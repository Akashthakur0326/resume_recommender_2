# app.py

import streamlit as st
from PAGES.student_corner import show_student_corner
from PAGES.recruiter_corner import show_recruiter_corner
from PAGES.resume_designer import show_resume_designer
import nltk

@st.cache_resource
def download_nltk():
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")
    nltk.download("omw-1.4")
    nltk.download("averaged_perceptron_tagger")

download_nltk()

# --- Page Configuration ---
st.set_page_config(page_title="AI Job Matcher", layout="wide")

# --- Main Title ---
st.title("🚀 AI-Powered Job & Resume Platform")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
pane_selection = st.sidebar.radio(
    "Choose your corner:",
    ["Student Corner", "Recruiter Corner", "Resume Designer"]
)

# --- Logic to Display Selected Pane ---
if pane_selection == "Student Corner":
    show_student_corner()

elif pane_selection == "Recruiter Corner":
    show_recruiter_corner()

elif pane_selection == "Resume Designer":
    show_resume_designer()