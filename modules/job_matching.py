"""pages/job_matching.py — Role-Based Matching"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database.database import (
    get_all_job_roles, insert_job_role, delete_job_role,
    get_all_candidates,
)
from utils.bert_scorer import compute_score, backend_label

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="rgba(255,255,255,0.6)", size=11),
    margin=dict(l=10,r=10,t=40,b=10),
    title_font=dict(family="Syne", size=14, color="rgba(255,255,255,0.85)"),
)

def run():
    

    tab1, tab2, tab3 = st.tabs(["🔍 Match Candidates","➕ Add Job Role","📋 Manage Roles"])

    with tab1:
        roles = get_all_job_roles()
        if not roles:
            st.warning("No job roles defined. Add some in the 'Add Job Role' tab.")
            return
        role_map = {r["title"]: r for r in roles}
        selected = st.selectbox("Select Role", list(role_map.keys()))
        ro = role_map[selected]
        c1,c2 = st.columns(2)
        c1.markdown(f"**Description:** {ro.get('description','N/A')}")
        c2.markdown(f"**Skills:** {ro.get('required_skills','N/A')}")
        c2.markdown(f"**Min Exp:** {ro.get('min_experience',0)} yrs")
        threshold = st.slider("Shortlist Threshold (%)", 0, 100, 60)
        if st.button("🚀 Match All Candidates", type="primary"):
            candidates = get_all_candidates()
            if not candidates:
                st.info("No candidates."); return
            jd = (ro.get("description") or "")+" "+(ro.get("required_skills") or "")
            results = []
            prog = st.progress(0)
            for i,c in enumerate(candidates):
                text = c.get("resume_text") or ""
                ls = compute_score(text, jd) if text else c.get("score",0)
                results.append({
                    "Name":c["name"],"Email":c["email"],
                    "Exp":c.get("experience",0),
                    "Skills":(c.get("skills") or "")[:50],
                    "Score (%)":round(ls*100,1),
                    "Status":c.get("status",""),
                })
                prog.progress((i+1)/len(candidates))
            prog.empty()
            df = pd.DataFrame(results).sort_values("Score (%)",ascending=False)
            df["Verdict"] = df["Score (%)"].apply(lambda s: "✅ Shortlist" if s>=threshold else "❌ Skip")
            top = df.head(20)
            fig = px.bar(top, x="Name", y="Score (%)",
                         color="Score (%)",
                         color_continuous_scale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
                         title=f"Top Candidates — {selected}")
            fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            shortlisted = df[df["Score (%)"]>=threshold]
            st.success(f"**{len(shortlisted)}** above {threshold}% threshold.")

    with tab2:
        st.markdown("##### Add New Job Role")
        title  = st.text_input("Job Title *")
        desc   = st.text_area("Job Description *", height=140)
        skills = st.text_area("Required Skills (comma-separated)")
        min_exp = st.number_input("Min Experience (yrs)", 0.0, 30.0, 0.0, 0.5)
        if st.button("💾 Save Role", type="primary"):
            if not title or not desc:
                st.error("Title and Description required.")
            else:
                insert_job_role(title, desc, skills, min_exp)
                st.success(f"Role **{title}** added!")
                st.rerun()

    with tab3:
        roles = get_all_job_roles()
        if not roles:
            st.info("No roles yet.")
        else:
            df_r = pd.DataFrame(roles)
            st.dataframe(df_r[["id","title","required_skills","min_experience","created_at"]],
                         use_container_width=True, hide_index=True)
            del_id = st.number_input("Role ID to Delete", min_value=1, step=1)
            if st.button("🗑️ Delete Role", type="secondary"):
                delete_job_role(int(del_id))
                st.success(f"Role {del_id} deleted.")
                st.rerun()
