"""pages/bulk_processing.py — Bulk Processing"""
import streamlit as st
import pandas as pd
from database.database import (
    get_all_candidates, update_candidate_status,
    delete_candidate, get_all_job_roles, update_candidate_score,
)
from utils.bert_scorer import compute_score, backend_label

def bulk_update_scores(jd_text, role_filter, prog):
    candidates = get_all_candidates()
    if role_filter != "All":
        candidates = [c for c in candidates if c["role"] == role_filter]
    total = len(candidates)
    for i, c in enumerate(candidates):
        resume_text = c.get("resume_text") or ""
        if resume_text:
            score = compute_score(resume_text, jd_text)
            update_candidate_score(int(c["id"]), score)
        prog.progress((i+1)/max(total,1))
    return total

def run():
    

    tab1, tab2, tab3 = st.tabs(["🔄 Bulk Re-Score","📝 Bulk Status Update","🗑️ Bulk Delete"])

    with tab1:
        roles = get_all_job_roles()
        role_titles = ["All"] + [r["title"] for r in roles]
        role_filter = st.selectbox("Filter by Role", role_titles)
        jd_prefill = ""
        if role_filter != "All":
            ro = next((r for r in roles if r["title"]==role_filter), None)
            if ro: jd_prefill = ro.get("description","") or ""
        jd_text = st.text_area("Job Description", value=jd_prefill, height=180)
        st.warning("⚠️ This overwrites existing scores for filtered candidates.")
        if st.button("🚀 Run Bulk Re-Score", type="primary"):
            if not jd_text.strip():
                st.error("Provide a job description.")
            else:
                prog = st.progress(0)
                n = bulk_update_scores(jd_text, role_filter, prog)
                prog.empty()
                st.success(f"✅ Re-scored {n} candidate(s)!")
                st.rerun()

    with tab2:
        candidates = get_all_candidates()
        if not candidates:
            st.info("No candidates.")
        else:
            df = pd.DataFrame(candidates)
            df["score_pct"] = (df["score"]*100).round(1)
            c1,c2 = st.columns(2)
            score_thr = c1.slider("Min Score (%)", 0, 100, 60)
            roles_unique = df["role"].dropna().unique().tolist()
            role_f = c2.selectbox("Role Filter", ["All"]+roles_unique, key="br")
            mask = df["score_pct"] >= score_thr
            if role_f != "All": mask &= df["role"] == role_f
            filtered = df[mask]
            st.info(f"**{len(filtered)}** candidate(s) match.")
            st.dataframe(filtered[["id","name","role","score_pct","status"]],
                         use_container_width=True, hide_index=True)
            new_status = st.selectbox("Set Status To",
                ["Shortlisted","Rejected","Hired","Pending","On Hold"])
            if st.button("✅ Apply to All Filtered", type="primary"):
                for cid in filtered["id"].tolist():
                    update_candidate_status(int(cid), new_status)
                st.success(f"Updated {len(filtered)} → **{new_status}**")
                st.rerun()

    with tab3:
        st.error("⚠️ Deletion is permanent.")
        candidates = get_all_candidates()
        if not candidates:
            st.info("No candidates.")
        else:
            df = pd.DataFrame(candidates)
            c1,c2 = st.columns(2)
            del_role = c1.selectbox("By Role",["— Choose —"]+df["role"].dropna().unique().tolist())
            del_status = c2.selectbox("By Status",
                ["— Choose —","Pending","Rejected","Shortlisted","Hired","On Hold"])
            to_del = df.copy()
            if del_role != "— Choose —": to_del = to_del[to_del["role"]==del_role]
            if del_status != "— Choose —": to_del = to_del[to_del["status"]==del_status]
            st.warning(f"**{len(to_del)}** record(s) will be deleted.")
            confirm = st.checkbox("I understand this is irreversible")
            if confirm and st.button("🗑️ Delete Now", type="primary"):
                for cid in to_del["id"].tolist():
                    delete_candidate(int(cid))
                st.success(f"Deleted {len(to_del)} record(s).")
                st.rerun()
