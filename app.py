import streamlit as st
import json, os, PyPDF2
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Resume Analyser - Reality Only")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'jobs.json'), 'r', encoding='utf-8') as f:
    ALL_JOBS = json.load(f)

TEMPLATE_LIST = [j['title'] for j in ALL_JOBS]

def extract_text(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for p in reader.pages:
            t = p.extract_text()
            if t:
                text += t + " "
    except:
        pass
    return text.lower()

if 'page_num' not in st.session_state:
    st.session_state.page_num = 0

st.title("🚀 Resume Analyser - 100% Reality of Resume Only")
uploaded = st.file_uploader("Upload Resume PDF", type=["pdf"])
selected_template = st.selectbox("Select Role Template (Only to check Have/Missing for that role)", TEMPLATE_LIST)

if not uploaded:
    st.info("Upload your resume - Both pages will show 100% reality based on YOUR resume skills only")
    st.stop()

resume_lower = extract_text(uploaded)

# Get Selected Template Details
job_obj = next((j for j in ALL_JOBS if j['title'] == selected_template), ALL_JOBS[0])
required_skills = job_obj.get('skills', [])
have = [s for s in required_skills if s.lower() in resume_lower]
missing = [s for s in required_skills if s.lower() not in resume_lower]
reality_pct = int((len(have)/len(required_skills))*100) if required_skills else 0

st.success(f"Resume: {uploaded.name} | Checked Template: {selected_template} | Reality: {len(have)}/{len(required_skills)} = {reality_pct}%")

tab1, tab2 = st.tabs(["📄 Page 1 - ATS Reality", "💼 Page 2 - Best Jobs Reality"])

# ================= PAGE 1 - REALITY ONLY =================
with tab1:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.subheader(f"For Role: {selected_template}")
        st.write(f"**Required Skills ({len(required_skills)}):** {', '.join(required_skills)}")
        st.write("---")
        st.markdown(f"#### ✅ You HAVE ({len(have)})")
        for s in have:
            st.markdown(f'<div style="background:#d4edda;border:1px solid #c3e6cb;padding:8px;border-radius:8px;margin:4px 0;">✅ {s}</div>', unsafe_allow_html=True)

        st.markdown(f"#### ❌ You MISSING ({len(missing)})")
        for s in missing:
            st.markdown(f'<div style="background:#f8d7da;border:1px solid #f5c6cb;padding:8px;border-radius:8px;margin:4px 0;">❌ {s}</div>', unsafe_allow_html=True)

        if missing:
            st.warning(f"Learn these to get 100% for {selected_template}: {', '.join(missing)}")
        else:
            st.balloons()
            st.success("You have ALL skills!")

    with c2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=reality_pct,
            title={'text': f"Reality - {selected_template}<br>{len(have)}/{len(required_skills)} skills"},
            gauge={'axis': {'range': [0,100]}, 'bar': {'color': "#28a745"}}
        ))
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Reality Formula", f"{len(have)} / {len(required_skills)} * 100 = {reality_pct}%")
        st.caption("100% Reality - No Boost, No Prediction - Only your resume skills")

# ================= PAGE 2 - REALITY ONLY =================
with tab2:
    st.markdown(f'<div style="background:#dc3545;padding:12px;border-radius:8px;text-align:center;color:white;font-weight:bold;font-size:16px;">Find My Best Jobs - 100% Reality Based on YOUR Resume Only - All {len(ALL_JOBS)} Jobs</div>', unsafe_allow_html=True)
    st.write("")
    st.info("This ranking NEVER changes when you change template - Because it's based only on YOUR resume reality!")

    scores = []
    for job in ALL_JOBS:
        orig = job.get('skills', [])
        low = [s.lower() for s in orig]
        matched = [o for o, l in zip(orig, low) if l in resume_lower]
        m = len(matched)
        t = len(orig) if orig else 1
        real_score = int((m/t)*100) # PURE REALITY - NO BOOST
        is_sel = job['title'] == selected_template
        scores.append((job, real_score, m, t, matched, is_sel))

    scores.sort(key=lambda x: x[1], reverse=True)

    # Top 3 Cards - Reality Only
    top3 = scores[:3]
    cols = st.columns(3)
    for i in range(3):
        if i < len(top3):
            job, sc, m, t, ml, is_sel = top3[i]
            with cols[i]:
                st.markdown(f"**{job['title']} {'⭐' if is_sel else ''}**")
                st.markdown(f"<h1 style='margin:0;'>{sc}% Match</h1>", unsafe_allow_html=True)
                st.write(f"{job['company']} | {job['salary']}")
                st.write(f"**Reality: {m}/{t} skills**")
                st.caption(f"Have: {', '.join(ml) if ml else 'None'}")

    st.write("---")

    # Full Table
    JOBS_PER_PAGE = 10
    total_pages = (len(scores)+JOBS_PER_PAGE-1)//JOBS_PER_PAGE
    start = st.session_state.page_num * JOBS_PER_PAGE
    curr = scores[start:start+JOBS_PER_PAGE]

    table = []
    for idx, (j, s, m, t, ml, is_sel) in enumerate(curr):
        miss = [o for o in j.get('skills', []) if o not in ml]
        table.append({
            "S.No": start+idx+1,
            "title": j['title'],
            "company": j['company'],
            "location": j['location'],
            "salary": j['salary'],
            "match": f"{s}%", # Pure reality
            "reality": f"{m}/{t} matched",
            "have": ", ".join(ml) if ml else "None",
            "missing": ", ".join(miss) if miss else "None",
            "Selected?": "⭐" if is_sel else ""
        })

    st.dataframe(pd.DataFrame(table), use_container_width=True, height=550, hide_index=True)

    b1, b2, b3 = st.columns([1,2,1])
    with b1:
        if st.button("⬅️ Previous", disabled=(st.session_state.page_num==0)):
            st.session_state.page_num-=1
            st.rerun()
    with b2:
        st.markdown(f"<center>Page {st.session_state.page_num+1} of {total_pages} | Reality Only - % never changes with template</center>", unsafe_allow_html=True)
    with b3:
        if st.button("Next ➡️", disabled=(st.session_state.page_num>=total_pages-1)):
            st.session_state.page_num+=1
            st.rerun()