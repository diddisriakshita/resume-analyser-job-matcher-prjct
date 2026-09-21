import streamlit as st
import pickle
import PyPDF2
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

st.set_page_config(page_title="Resume Analyser - 15x15 Final", layout="wide")

st.markdown("""
<style>
.card {background:white;border:1px solid #e0e0e0;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:12px;}
.badge-high{background:#057642;color:white;padding:6px 14px;border-radius:20px;font-weight:bold;float:right}
.badge-mid{background:#f59e0b;color:black;padding:6px 14px;border-radius:20px;font-weight:bold;float:right}
.badge-low{background:#dc2626;color:white;padding:6px 14px;border-radius:20px;font-weight:bold;float:right}
.chip-have{background:#d1fae5;color:#065f46;padding:5px 10px;border-radius:16px;margin:3px;display:inline-block;font-size:12px;font-weight:700}
.chip-miss{background:#fee2e2;color:#991b1b;padding:5px 10px;border-radius:16px;margin:3px;display:inline-block;font-size:12px;font-weight:700}
</style>
""", unsafe_allow_html=True)

st.title("📄 Resume Analyser - Job Matcher")
st.caption("15 Roles | 15 Companies Per Role = 225 Jobs | Final Clean Version")

@st.cache_resource
def load_ml():
    vectorizer = pickle.load(open('models/tfidf.pkl','rb'))
    job_embeddings = pickle.load(open('models/job_embeddings.pkl','rb'))
    jobs = pickle.load(open('models/jobs.pkl','rb'))
    return vectorizer, job_embeddings, jobs

vectorizer, job_embeddings, ALL_JOBS = load_ml()

def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for p in reader.pages:
        text += (p.extract_text() or "") + " "
    return text.lower()

uploaded = st.file_uploader("Upload Resume PDF", type=["pdf"])
if not uploaded:
    st.info("Upload resume - Will show 15 companies for selected role")
    st.stop()

resume_lower = extract_text(uploaded)
resume_vec = vectorizer.transform([resume_lower])
sims = cosine_similarity(resume_vec, job_embeddings)[0]

titles = sorted(list(set([j['title'] for j in ALL_JOBS])))
selected = st.selectbox(f"Select Role Template - {len(titles)} Roles", titles)

scores = []
for idx, job in enumerate(ALL_JOBS):
    req = job.get('skills', [])
    have = [s for s in req if s.lower() in resume_lower]
    miss = [s for s in req if s.lower() not in resume_lower]
    pct = int(len(have)/len(req)*100) if req else 0
    scores.append((job, pct, len(have), len(req), have, miss, sims[idx]))

scores.sort(key=lambda x: x[1], reverse=True)

count_selected = len([j for j in ALL_JOBS if j['title'] == selected])
st.markdown(f"<div style='background:#e6f0ff;padding:12px;border-radius:8px'>Resume: {uploaded.name} | Selected: <b>{selected}</b> | Found: <b>{count_selected} companies</b> | Total: {len(ALL_JOBS)} jobs</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([f"Page 1 - {selected} Learning Path", f"Page 2 - {selected} Table"])

with tab1:
    filtered = [s for s in scores if s[0]['title'] == selected]
    st.subheader(f"🎯 {selected} - {len(filtered)} Companies")
    for job, pct, m, t, have, miss, sim in filtered:
        badge = "badge-high" if pct>=60 else "badge-mid" if pct>=40 else "badge-low"
        st.markdown(f"<div class='card'><span class='{badge}'>{pct}% Match</span><h3>🏢 {job['company']} | {job['title']}</h3><p>📍 {job['location']} | 💰 {job['salary']} | Reality: {m}/{t} skills | 🕒 Full-time</p></div>", unsafe_allow_html=True)
        st.progress(pct/100)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ YOU HAVE:**")
            if have: st.markdown("".join([f"<span class='chip-have'>✅ {s}</span>" for s in have]), unsafe_allow_html=True)
        with c2:
            st.markdown(f"**❌ LEARN FOR {job['company']}:**")
            if miss: st.markdown("".join([f"<span class='chip-miss'>❌ {s}</span>" for s in miss]), unsafe_allow_html=True)
        st.divider()

with tab2:
    filtered = [s for s in scores if s[0]['title'] == selected]
    st.subheader(f"Open Roles - {selected} - All {len(filtered)} Companies")

    data = []
    for i, (job, pct, m, t, have, miss, sim) in enumerate(filtered, 1):
        data.append({
            "S.No": i,
            "Company": job['company'],
            "Role": job['title'],
            "Location": job['location'],
            "Salary": job['salary'],
            "Match": f"{pct}%",
            "Reality": f"{m}/{t}",
            "Have": ", ".join(have) if have else "-",
            "Missing": ", ".join(miss)
        })
    df = pd.DataFrame(data)

    # FIX FOR YOUR ISSUE - HIDE 0,1,2 INDEX - SHOW ONLY S.No
    st.dataframe(df, use_container_width=True, height=700, hide_index=True)
