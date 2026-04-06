"""pages/interview_scheduler.py — Interview Scheduler"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, time, timedelta
from database.database import (
    schedule_interview, get_all_interviews,
    update_interview_status, delete_interview, get_all_candidates,
)

STATUSES = ["Scheduled","Completed","Cancelled","No-Show","Rescheduled"]
MODES    = ["Online (Video Call)","In-Person","Phone","Technical Test"]
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="rgba(255,255,255,0.6)", size=11),
    margin=dict(l=10,r=10,t=40,b=10),
    title_font=dict(family="Syne", size=14, color="rgba(255,255,255,0.85)"),
)

def run():
    

    tab1, tab2, tab3 = st.tabs(["📌 Schedule New","📋 Upcoming","📊 Analytics"])

    with tab1:
        candidates = get_all_candidates()
        shortlisted = [c for c in candidates if c.get("status") in ("Shortlisted","Pending","On Hold")]
        if shortlisted:
            cand_map = {f"{c['name']} — {c['role']} (ID {c['id']})": c for c in shortlisted}
            chosen   = st.selectbox("Select Candidate", list(cand_map.keys()))
            cand_obj = cand_map[chosen]
            cand_id, cand_name, cand_role = cand_obj["id"], cand_obj["name"], cand_obj["role"]
        else:
            st.warning("No shortlisted candidates. Using manual entry.")
            cand_id   = None
            cand_name = st.text_input("Candidate Name")
            cand_role = st.text_input("Role")

        c1,c2 = st.columns(2)
        iv_date = c1.date_input("Interview Date", value=date.today()+timedelta(days=3))
        iv_time = c2.time_input("Interview Time", value=time(10,0))
        interviewer = st.text_input("Interviewer / Panel")
        mode  = st.selectbox("Mode", MODES)
        notes = st.text_area("Notes / Agenda", height=90)

        if st.button("📅 Schedule Interview", type="primary"):
            if not cand_name or not interviewer:
                st.error("Candidate name and interviewer required.")
            else:
                schedule_interview(cand_id, cand_name, cand_role,
                                   iv_date, str(iv_time), interviewer, mode, notes)
                st.success(f"✅ Interview scheduled for **{cand_name}** on **{iv_date}**!")
                st.rerun()

    with tab2:
        interviews = get_all_interviews()
        if not interviews:
            st.info("No interviews scheduled yet.")
            return
        df = pd.DataFrame(interviews)
        df["interview_date"] = pd.to_datetime(df["interview_date"])

        c1,c2 = st.columns(2)
        status_filter = c1.multiselect("Filter Status", STATUSES, default=["Scheduled"])
        date_from     = c2.date_input("From Date", value=date.today())

        filtered = df.copy()
        if status_filter: filtered = filtered[filtered["status"].isin(status_filter)]
        filtered = filtered[filtered["interview_date"].dt.date >= date_from]

        st.info(f"**{len(filtered)}** interview(s)")
        for _, row in filtered.iterrows():
            with st.expander(
                f"📌 {row['candidate_name']} · {row['role']} · "
                f"{row['interview_date'].strftime('%d %b %Y')} "
                f"{str(row.get('interview_time',''))[:5]} · {row['status']}"
            ):
                c1,c2,c3 = st.columns(3)
                c1.write(f"**Interviewer:** {row.get('interviewer','')}")
                c1.write(f"**Mode:** {row.get('mode','')}")
                c2.write(f"**Notes:** {row.get('notes','N/A')}")
                new_s = c3.selectbox("Update Status", STATUSES,
                    index=STATUSES.index(row["status"]) if row["status"] in STATUSES else 0,
                    key=f"is_{row['id']}")
                col_b1,col_b2 = c3.columns(2)
                if col_b1.button("Save", key=f"isv_{row['id']}"):
                    update_interview_status(int(row["id"]), new_s)
                    st.success("Updated!"); st.rerun()
                if col_b2.button("🗑️", key=f"idl_{row['id']}"):
                    delete_interview(int(row["id"]))
                    st.warning("Deleted."); st.rerun()

    with tab3:
        interviews = get_all_interviews()
        if not interviews:
            st.info("No data yet."); return
        df = pd.DataFrame(interviews)
        c1,c2 = st.columns(2)
        fig_s = px.pie(df.groupby("status").size().reset_index(name="count"),
                       values="count", names="status", title="By Status",
                       color_discrete_sequence=["#6366f1","#10b981","#ef4444","#f59e0b","#8b5cf6"],
                       hole=0.5)
        fig_s.update_layout(**CHART_LAYOUT)
        c1.plotly_chart(fig_s, use_container_width=True)
        fig_m = px.bar(df.groupby("mode").size().reset_index(name="count"),
                       x="mode", y="count", title="By Mode",
                       color="count",
                       color_continuous_scale=[[0,"#6366f1"],[1,"#10b981"]])
        fig_m.update_layout(**CHART_LAYOUT, coloraxis_showscale=False)
        c2.plotly_chart(fig_m, use_container_width=True)
