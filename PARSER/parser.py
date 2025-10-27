# parser.py
import fitz
import spacy
import pandas as pd
#import streamlit as st
from spacy.matcher import Matcher

import constant
from parser_utils import (
    open_pdf, extract_text, extract_links, get_number_of_pages,
    classify_sections, spacy_entity, extract_email,
    extract_name, extract_education, extract_skills, extract_experience
)


# ------------------------
# Resume Parser Class
# ------------------------
class ResumeParser:
    def __init__(self, uploaded_file):
        """Initialize with uploaded file (from Streamlit)."""
        self.uploaded_file = uploaded_file
        self.doc = open_pdf(uploaded_file)  # open once
        self.text = None
        self.links = None
        self.num_pages = None
        self.sections = None
        self.entities = None
        self.email = None
        self.name = None
        self.education = None
        self.skills = None

        # Load spacy model once
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)

    def parse(self):
        """Run full extraction pipeline."""

        # Extract plain text + links
        self.text = extract_text(self.doc)
        self.links = extract_links(self.doc)
        self.num_pages = get_number_of_pages(self.doc)

        # Section classification (keep only non-empty from RESUME_SECTION)
        raw_sections = classify_sections(self.text)
        self.sections = {
            key: val
            for key, val in raw_sections.items()
            if key in constant.RESUME_SECTION and val
        }

        # NER processing
        nlp_text = self.nlp(self.text)
        self.entities = spacy_entity(nlp_text)

        # Emails, name, education
        self.email = extract_email(self.text)
        self.name = extract_name(nlp_text, self.matcher)
        self.education = extract_education(self.text.split("\n"))

        # Skills
        self.skills = extract_skills(nlp_text, nlp_text.noun_chunks)

        # Close doc after parsing
        self.doc.close()

        return self.to_dict()

    def to_dict(self):
        """Return parsed data as dict."""
        return {
            "text": self.text,
            "links": self.links,
            "num_pages": self.num_pages,
            "sections": self.sections,
            "entities": self.entities,
            "email": self.email,
            "name": self.name,
            "education": self.education,
            "skills": self.skills,
        }


"""
def display_resume(parsed_data, container_type="expander"):
    
    if container_type == "expander":
        with st.expander("📄 Resume Text"):
            st.text_area("Extracted Text", parsed_data["text"], height=300)

        with st.expander("🔗 Links"):
            st.write(parsed_data["links"])

        with st.expander("📧 Contact Info"):
            st.write("Email:", parsed_data["email"])
            st.write("Name:", parsed_data["name"])

        with st.expander("🎓 Education"):
            st.json(parsed_data["education"])

        with st.expander("🛠 Skills"):
            st.write(parsed_data["skills"])

        with st.expander("🔍 NER Entities"):
            st.json(parsed_data["entities"])

        with st.expander("📑 Sections"):
            st.json(parsed_data["sections"])

    elif container_type == "container":
        st.subheader("📄 Resume Overview")
        st.write(f"Pages: {parsed_data['num_pages']}")
        st.write("Email:", parsed_data["email"])
        st.write("Name:", parsed_data["name"])
        st.write("Skills:", ", ".join(parsed_data["skills"]))

    elif container_type == "session_state":
        st.session_state["parsed_resume"] = parsed_data
        st.success("Resume data saved to session_state ")
"""