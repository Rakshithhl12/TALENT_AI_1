"""pages/resume_upload.py — Upload & Score Resumes"""
import streamlit as st
import pandas as pd
from utils.resume_parser import parse_resume
from utils.bert_scorer import compute_score, backend_label
from database.database import insert_candidate, get_all_job_roles

def run():
    

    st.markdown("##### 1. Job Description")
    jd_source = st.radio("JD Source", ["From Database","Paste Manually"], horizontal=True)

    jd_text, selected_role = "", ""
    if jd_source == "From Database":
        roles = get_all_job_roles()
        if roles:
            role_map = {r["title"]: r for r in roles}
            selected_role = st.selectbox("Job Role", list(role_map.keys()))
            jd_text = role_map[selected_role].get("description","") or ""
            st.text_area("JD Preview", jd_text, height=120, disabled=True)
        else:
            st.warning("No roles in DB. Add via Job Match page.")
            jd_text = st.text_area("Paste JD", height=120)
            selected_role = st.text_input("Role Title")
    else:
        col_a, col_b = st.columns(2)
        jd_text = col_a.text_area("Job Description", height=150)
        selected_role = col_b.text_input("Role Title")

    st.markdown(" 2. Upload Resumes", unsafe_allow_html=True)
    files = st.file_uploader("PDF / DOCX (multiple allowed)",
                             type=["pdf","docx"], accept_multiple_files=True)

    if not files:
        st.info("📁 Upload one or more resume files to begin.")
        return

    st.success(f"**{len(files)} file(s)** ready. Click below to process.")

    if st.button("🚀 Process & Store in MySQL", type="primary"):
        results = []
        prog = st.progress(0)
        status_box = st.empty()
        for i, file in enumerate(files):
            status_box.info(f"Processing **{file.name}** …")
            parsed = parse_resume(file)
            score  = compute_score(parsed["text"], jd_text) if jd_text else 0.0
            role   = selected_role or "General"
            cid    = insert_candidate(
                name=parsed["name"],
                email=parsed["email"] or f"{i}_{file.name}@unknown.com",
                phone=parsed["phone"], role=role,
                skills=parsed["skills"], experience=parsed["experience"],
                score=score, resume_text=parsed["text"][:65000],
            )
            results.append({
                "File": file.name, "Name": parsed["name"],
                "Email": parsed["email"],
                "Exp": f"{parsed['experience']} yrs",
                "Skills": (parsed["skills"][:60]+"…") if len(parsed["skills"])>60 else parsed["skills"],
                "Score": f"{round(score*100,1)}%",
                "DB ID": cid,
            })
            prog.progress((i+1)/len(files))
        status_box.empty(); prog.empty()
        st.success(f"✅ {len(results)} resume(s) stored in MySQL!")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)
        best = max(results, key=lambda x: float(x["Score"].strip("%")))
        st.info(f"🏆 **Top Candidate:** {best['Name']} — {best['Score']} match")
