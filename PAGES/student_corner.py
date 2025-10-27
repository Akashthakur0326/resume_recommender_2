# panes/student.py

import streamlit as st
# Import your backend functions from 'core' when ready
# from core.resume_parser import parse_resume
# from core.job_matcher import get_recommendations

def show_student_corner():
    st.header("🎓 Student Corner")
    
    # Create the two tabs
    tab_upload, tab_recommend = st.tabs(["Upload Resume", "Recommended Jobs"])

    # --- Tab 1: Upload Resume ---
    with tab_upload:
        st.subheader("Upload Your Resume")
        st.write("Upload your resume (PDF or DOCX) to parse your skills and experience.")
        
        uploaded_resume = st.file_uploader(
            "Choose a file", 
            type=["pdf", "docx"],
            label_visibility="collapsed"
        )
        
        if uploaded_resume is not None:
            # --- BACKEND HOOK ---
            # parsed_data = parse_resume(uploaded_resume) 
            # st.json(parsed_data)
            
            # Placeholder:
            st.success(f"Successfully uploaded: {uploaded_resume.name}")
            st.write("---")
            st.subheader("Parsed Resume Data (Backend Placeholder)")
            st.json({
                "name": "Your Name",
                "email": "your.email@example.com",
                "skills": ["Python", "Streamlit", "Data Analysis", "ML"],
                "experience": "Details about your experience..."
            })

    # --- Tab 2: Recommended Jobs ---
    with tab_recommend:
        st.subheader("Your Recommended Jobs")
        st.write("Based on your uploaded resume, your top job recommendations will appear here.")
        
        # --- BACKEND HOOK ---
        # recommendations = get_recommendations(parsed_data)
        # for job in recommendations:
        #    st.markdown(f"- **{job['title']}** at {job['company']}")
        
        # Placeholder:
        st.info("Upload a resume in the first tab to see recommendations.")
        st.write("---")
        st.write("*(Backend Placeholder): Job recommendations based on resume data will be listed here.*")
        st.markdown("- **Software Engineer** at Google\n- **Data Scientist** at Meta\n- **ML Engineer** at OpenAI")