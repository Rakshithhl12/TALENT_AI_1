import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import Counter
from database.database import (
    get_daily_analytics, get_role_distribution, get_score_distribution,
    get_status_distribution, get_all_candidates, get_dashboard_stats,
)

C = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
         font=dict(family="Plus Jakarta Sans", color="rgba(203,213,225,0.7)", size=11),
         margin=dict(l=8,r=8,t=36,b=8),
         title_font=dict(family="Outfit",size=13,color="#94A3B8"),
         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")))

def run():
    col_f, _ = st.columns([1,4])
    days = col_f.selectbox("Time Range", [7,14,30,60,90], index=2,
                           format_func=lambda d: f"Last {d} days")

    s = get_dashboard_stats()
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Candidates", s["total"] or 0)
    k2.metric("Avg Match Score",  f"{s['avg_score'] or 0}%")
    k3.metric("Hired",            s["hired"] or 0)
    k4.metric("Active Roles",     s["roles"] or 0)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1
    c1,c2 = st.columns(2)
    daily = get_daily_analytics(days)
    if daily:
        df = pd.DataFrame(daily)
        df["event_date"] = pd.to_datetime(df["event_date"])
        fig = go.Figure()
        specs = [("applications","#3B82F6","Applications"),
                 ("shortlisted","#10B981","Shortlisted"),
                 ("rejected","#EF4444","Rejected"),
                 ("hired","#F59E0B","Hired")]
        for col,color,name in specs:
            if col in df.columns:
                fig.add_trace(go.Scatter(x=df["event_date"],y=df[col],
                    mode="lines+markers",name=name,
                    line=dict(color=color,width=2),
                    marker=dict(size=4,color=color)))
        fig.update_layout(title=f"Trend — Last {days} Days",
                          hovermode="x unified",**C)
        c1.plotly_chart(fig, use_container_width=True)

    sd = get_status_distribution()
    if sd:
        df = pd.DataFrame(sd)
        fig = px.pie(df, values="total", names="status", hole=0.55,
                     color_discrete_sequence=["#3B82F6","#10B981","#EF4444","#F59E0B","#8B5CF6"],
                     title="Status Distribution")
        fig.update_traces(textfont_color="white")
        fig.update_layout(**C)
        c2.plotly_chart(fig, use_container_width=True)

    # Row 2
    c3,c4 = st.columns(2)
    rd = get_role_distribution()
    if rd:
        df = pd.DataFrame(rd).sort_values("total")
        fig = go.Figure(go.Bar(x=df["total"],y=df["role"],orientation="h",
            marker=dict(color=df["total"],
                        colorscale=[[0,"#1E3A5F"],[1,"#10B981"]],
                        line=dict(width=0))))
        fig.update_layout(title="Candidates per Role",**C,coloraxis_showscale=False)
        c3.plotly_chart(fig, use_container_width=True)

    sc = get_score_distribution()
    if sc:
        df = pd.DataFrame(sc)
        colors = {"Excellent (80-100%)":"#10B981","Good (60-79%)":"#3B82F6",
                  "Average (40-59%)":"#F59E0B","Low (<40%)":"#EF4444"}
        df["color"] = df["band"].map(colors)
        fig = go.Figure(go.Bar(x=df["band"],y=df["total"],
            marker=dict(color=df["color"],line=dict(width=0))))
        fig.update_layout(title="Score Band Distribution",**C)
        c4.plotly_chart(fig, use_container_width=True)

    # Scatter
    cands = get_all_candidates()
    if cands:
        df = pd.DataFrame(cands)
        df["score_pct"] = (df["score"]*100).round(1)
        st.markdown("---")
        st.markdown("#### Experience vs Match Score")
        fig = px.scatter(df, x="experience", y="score_pct",
            color="role", hover_name="name", size="score_pct",
            title="Experience vs Score",
            color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(**C)
        st.plotly_chart(fig, use_container_width=True)

        # Skills
        skill_counter: Counter = Counter()
        for c in cands:
            for sk in (c.get("skills") or "").split(","):
                sk = sk.strip()
                if sk: skill_counter[sk] += 1
        if skill_counter:
            df_sk = pd.DataFrame(skill_counter.most_common(20), columns=["Skill","Count"])
            fig = go.Figure(go.Bar(x=df_sk["Count"],y=df_sk["Skill"],orientation="h",
                marker=dict(color=df_sk["Count"],
                            colorscale=[[0,"#1E3A5F"],[1,"#3B82F6"]],
                            line=dict(width=0))))
            fig.update_layout(title="Top 20 Skills",yaxis=dict(autorange="reversed"),**C)
            st.plotly_chart(fig, use_container_width=True)
