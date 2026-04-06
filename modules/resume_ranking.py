"""pages/resume_ranking.py — AI Resume Ranking"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.bert_scorer import compute_score, backend_label
from database.database import (
    get_all_candidates, get_candidates_by_role,
    update_candidate_status, get_job_role_titles,
)

STATUS_OPTIONS = ["Pending","Shortlisted","Rejected","Hired","On Hold"]
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="rgba(255,255,255,0.6)", size=11),
    margin=dict(l=10,r=10,t=40,b=10),
    title_font=dict(family="Syne", size=14, color="rgba(255,255,255,0.85)"),
)

def run():
    

    tab1, tab2 = st.tabs(["📋 Ranked Candidates", "🔬 Live Scorer"])

    with tab1:
        c1, c2 = st.columns([2,1])
        filter_role = c1.selectbox("Filter Role", ["All Roles"]+get_job_role_titles())
        min_score   = c2.slider("Min Score (%)", 0, 100, 0)

        candidates = (get_candidates_by_role(filter_role)
                      if filter_role != "All Roles"
                      else get_all_candidates())
        if not candidates:
            st.info("No candidates. Upload resumes first.")
            return

        df = pd.DataFrame(candidates)
        df["score_pct"] = (df["score"]*100).round(1)
        df = df[df["score_pct"] >= min_score].reset_index(drop=True)
        df["rank"] = df["score_pct"].rank(ascending=False, method="min").astype(int)

        fig = px.histogram(df, x="score_pct", nbins=20,
                           title="Score Distribution",
                           color_discrete_sequence=["#6366f1"])
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"##### {len(df)} Candidates")
        for _, row in df.iterrows():
            with st.expander(f"#{int(row['rank'])}  {row['name']}  ·  {row['score_pct']}%  ·  {row.get('role','')}"):
                c1,c2,c3 = st.columns(3)
                c1.write(f"**Email:** {row.get('email','')}")
                c1.write(f"**Phone:** {row.get('phone','')}")
                c2.write(f"**Experience:** {row.get('experience',0)} yrs")
                c2.write(f"**Skills:** {(row.get('skills') or '')[:80]}")
                new_status = c3.selectbox("Status",STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(row.get("status","Pending"))
                    if row.get("status") in STATUS_OPTIONS else 0,
                    key=f"st_{row['id']}")
                if c3.button("Save", key=f"sv_{row['id']}"):
                    update_candidate_status(int(row["id"]), new_status)
                    st.success(f"Updated → {new_status}")
                    st.rerun()

    with tab2:
        st.markdown("##### Test Resume vs Job Description")
        col_a, col_b = st.columns(2)
        jd     = col_a.text_area("Job Description", height=220)
        resume = col_b.text_area("Resume Text",     height=220)
        if st.button("⚡ Compute Score", type="primary"):
            if jd and resume:
                score = compute_score(resume, jd)
                pct   = round(score*100, 2)
                color = "#10b981" if pct>=70 else "#f59e0b" if pct>=40 else "#ef4444"
                st.markdown(f"<h2 style='color:{color};font-family:Syne'>Match Score: {pct}%</h2>",
                            unsafe_allow_html=True)
                fig_g = px.bar(x=["Score","Remaining"], y=[pct,100-pct],
                               color=["Score","Remaining"],
                               color_discrete_map={"Score":color,"Remaining":"rgba(255,255,255,0.06)"})
                fig_g.update_layout(**CHART_LAYOUT, showlegend=False)
                st.plotly_chart(fig_g, use_container_width=True)
                verdict = ("🟢 Strong Match — Recommend Shortlisting" if pct>=70
                           else "🟡 Moderate Match — Manual Review Advised" if pct>=40
                           else "🔴 Weak Match — Consider Rejecting")
                st.info(verdict)
            else:
                st.warning("Fill both fields.")
