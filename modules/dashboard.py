import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database.database import (
    get_dashboard_stats, get_all_candidates,
    get_daily_analytics, get_role_distribution, get_status_distribution,
)

C = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
         font=dict(family="Plus Jakarta Sans", color="rgba(203,213,225,0.7)", size=11),
         margin=dict(l=8,r=8,t=36,b=8),
         title_font=dict(family="Outfit",size=13,color="#94A3B8"),
         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")))

def run():
    s = get_dashboard_stats()
    total       = s["total"]       or 0
    shortlisted = s["shortlisted"] or 0
    rejected    = s["rejected"]    or 0
    hired       = s["hired"]       or 0
    pending     = s["pending"]     or 0
    avg_score   = s["avg_score"]   or 0.0
    roles_count = s["roles"]       or 0

    # KPI strip
    cols = st.columns(7)
    icons  = ["📄","✅","❌","🏆","⏳","🎯","💼"]
    labels = ["Total","Shortlisted","Rejected","Hired","Pending","Avg Score","Roles"]
    values = [total, shortlisted, rejected, hired, pending, f"{avg_score}%", roles_count]
    for col, ic, lb, val in zip(cols, icons, labels, values):
        col.metric(f"{ic} {lb}", val)

    st.markdown("<br>", unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns(3)

    # Status donut
    sd = get_status_distribution()
    if sd:
        df = pd.DataFrame(sd)
        fig = px.pie(df, values="total", names="status", hole=0.6,
                     color_discrete_sequence=["#3B82F6","#10B981","#EF4444","#F59E0B","#8B5CF6"],
                     title="Candidate Status")
        fig.update_traces(textfont_color="white", textfont_size=11)
        fig.update_layout(**C)
        r1c1.plotly_chart(fig, use_container_width=True)

    # Role bar
    rd = get_role_distribution()
    if rd:
        df = pd.DataFrame(rd).sort_values("total")
        fig = go.Figure(go.Bar(
            x=df["total"], y=df["role"], orientation="h",
            marker=dict(color=df["total"],
                        colorscale=[[0,"#1E3A5F"],[0.5,"#3B82F6"],[1,"#10B981"]],
                        line=dict(width=0)),
        ))
        fig.update_layout(title="Candidates by Role", xaxis_title="", yaxis_title="", **C)
        r1c2.plotly_chart(fig, use_container_width=True)

    # Applications trend
    daily = get_daily_analytics(30)
    if daily:
        df = pd.DataFrame(daily)
        df["event_date"] = pd.to_datetime(df["event_date"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["event_date"], y=df["applications"],
            fill="tozeroy", mode="lines+markers",
            line=dict(color="#3B82F6", width=2.5),
            fillcolor="rgba(59,130,246,0.08)",
            marker=dict(size=5, color="#60A5FA"),
            name="Applications",
        ))
        fig.update_layout(title="Applications — 30 Days",
                          xaxis_title="", yaxis_title="",
                          showlegend=False, **C)
        r1c3.plotly_chart(fig, use_container_width=True)

    # Recent candidates table
    st.markdown("---")
    st.markdown("#### 🗂 Recent Candidates")
    data = get_all_candidates()
    if data:
        df = pd.DataFrame(data)
        df["Score"] = (df["score"]*100).round(1).astype(str)+"%"
        show = ["name","email","role","experience","Score","status","uploaded_at"]
        ok   = [c for c in show if c in df.columns]
        st.dataframe(
            df[ok].rename(columns={"name":"Name","email":"Email","role":"Role",
                                   "experience":"Exp(yrs)","status":"Status","uploaded_at":"Uploaded"}),
            use_container_width=True, hide_index=True)
    else:
        st.info("No candidates yet. Upload resumes to begin.")
