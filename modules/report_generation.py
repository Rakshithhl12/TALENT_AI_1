"""pages/report_generation.py — Report Generation"""
import io, streamlit as st
import pandas as pd
from datetime import date
from database.database import (
    get_all_candidates, get_all_interviews,
    get_dashboard_stats, get_role_distribution,
)

def _candidates_df():
    c = get_all_candidates()
    if not c: return pd.DataFrame()
    df = pd.DataFrame(c)
    df["score_pct"] = (df["score"]*100).round(1)
    return df.drop(columns=["resume_text","score"], errors="ignore")

def _interviews_df():
    iv = get_all_interviews()
    return pd.DataFrame(iv) if iv else pd.DataFrame()

def run():
    

    report_type = st.selectbox("Report Type", [
        "All Candidates Summary","Shortlisted Candidates",
        "Rejected Candidates","Interview Schedule",
        "Role-wise Summary","Full HR Report (Excel)",
    ])

    today_str = date.today().strftime("%d %B %Y")
    df_c = _candidates_df()
    df_i = _interviews_df()

    st.divider()

    def show_and_download(df, filename, label="All"):
        if df.empty:
            st.info(f"No {label} data available."); return
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(f"⬇️ Download CSV",
                           df.to_csv(index=False),
                           f"{filename}_{date.today()}.csv", "text/csv")

    if report_type == "All Candidates Summary":
        st.markdown(f"##### All Candidates — {today_str}")
        show_and_download(df_c, "all_candidates")

    elif report_type == "Shortlisted Candidates":
        df = df_c[df_c["status"]=="Shortlisted"] if not df_c.empty else pd.DataFrame()
        st.markdown(f"##### Shortlisted ({len(df)}) — {today_str}")
        show_and_download(df, "shortlisted", "shortlisted")

    elif report_type == "Rejected Candidates":
        df = df_c[df_c["status"]=="Rejected"] if not df_c.empty else pd.DataFrame()
        st.markdown(f"##### Rejected ({len(df)}) — {today_str}")
        show_and_download(df, "rejected", "rejected")

    elif report_type == "Interview Schedule":
        st.markdown(f"##### Interview Schedule — {today_str}")
        show_and_download(df_i, "interviews", "interview")

    elif report_type == "Role-wise Summary":
        st.markdown(f"##### Role-wise Summary — {today_str}")
        if not df_c.empty:
            rs = df_c.groupby("role").agg(
                Total=("id","count"),
                Shortlisted=("status", lambda s: (s=="Shortlisted").sum()),
                Hired=("status", lambda s: (s=="Hired").sum()),
                Avg_Score=("score_pct","mean"),
            ).reset_index()
            rs["Avg_Score"] = rs["Avg_Score"].round(1)
            show_and_download(rs, "role_summary")

    elif report_type == "Full HR Report (Excel)":
        st.info("Generates a multi-sheet Excel: Candidates · Shortlisted · Interviews · Role Summary")
        if st.button("📊 Generate Excel Report", type="primary"):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                if not df_c.empty:
                    df_c.to_excel(writer, sheet_name="All Candidates", index=False)
                    df_c[df_c["status"]=="Shortlisted"].to_excel(writer, sheet_name="Shortlisted", index=False)
                if not df_i.empty:
                    df_i.to_excel(writer, sheet_name="Interviews", index=False)
                if not df_c.empty:
                    rs = df_c.groupby("role").agg(
                        Total=("id","count"),
                        Shortlisted=("status", lambda s: (s=="Shortlisted").sum()),
                        Hired=("status", lambda s: (s=="Hired").sum()),
                        Avg_Score=("score_pct","mean"),
                    ).reset_index()
                    rs.to_excel(writer, sheet_name="Role Summary", index=False)
            buf.seek(0)
            st.download_button("⬇️ Download Excel",
                               buf, f"TalentAI_Report_{date.today()}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.success("Ready for download!")
