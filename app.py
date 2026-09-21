import streamlit as st
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Resume Analyser", layout="wide")
st.title("📄 Resume Analyser - Job Matcher")
st.write("15 Roles | 15 Companies Per Role = 225 Jobs | Final Clean Version")

# Load jobs
@st.cache_data
def load_jobs():
    with open('jobs.json', 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    return jobs

@st.cache_resource
def get_vectorizer(_jobs):
    descriptions = [j.get('description','') + " " + j.get('title','') for j in _jobs]
    vectorizer = TfidfVectorizer(stop_words='english')
    job_embeddings = vectorizer.fit_transform(descriptions)
    return vectorizer, job_embeddings

ALL_JOBS = load_jobs()
vectorizer, job_embeddings = get_vectorizer(ALL_JOBS)

# UI
resume_text = st.text_area("Paste your Resume Text here:", height=250)

if st.button("Find Matching Jobs"):
    if not resume_text.strip():
        st.warning("Please paste resume text.")
    else:
        resume_vec = vectorizer.transform([resume_text])
        scores = cosine_similarity(resume_vec, job_embeddings)[0]

        # Get top 10
        top_idx = scores.argsort()[::-1][:10]

        st.subheader("Top Matching Jobs:")
        for i in top_idx:
            job = ALL_JOBS[i]
            st.markdown(f"**{job.get('title','')}** at **{job.get('company','')}** - Score: {scores[i]:.2f}")
            st.write(job.get('description','')[:300] + "...")
            st.divider()
