"""
modules/chatbot.py — TalentAI HR Chatbot
All quick-start buttons and natural queries answered from live MySQL data.
No API key required.
"""
import streamlit as st
from collections import Counter
from database.database import (
    get_dashboard_stats, get_all_candidates,
    get_role_distribution, get_all_interviews,
    get_all_job_roles,
)

def _has(q, *phrases):
    return any(p in q for p in phrases)

def _score_bar(sc):
    return "🟢" if sc >= 70 else "🟡" if sc >= 40 else "🔴"

def _fmt(c, rank=None):
    sc  = round(c.get("score", 0) * 100, 1)
    pfx = f"**#{rank}** " if rank else ""
    return (f"{pfx}{_score_bar(sc)} **{c['name']}**\n"
            f"   • Role: {c.get('role','N/A')} | Score: {sc}% "
            f"| Exp: {c.get('experience',0)} yrs | Status: {c.get('status','N/A')}")

def answer(query):
    q = query.lower().strip()

    stats      = get_dashboard_stats()
    cands      = get_all_candidates()
    roles_dist = get_role_distribution()
    interviews = get_all_interviews()
    job_roles  = get_all_job_roles()

    total  = stats["total"]       or 0
    sl     = stats["shortlisted"] or 0
    rej    = stats["rejected"]    or 0
    hired  = stats["hired"]       or 0
    pend   = stats["pending"]     or 0
    avg_sc = stats["avg_score"]   or 0.0

    sorted_cands = sorted(cands, key=lambda c: c.get("score",0), reverse=True)

    def top_n(n):
        t = sorted_cands[:n]
        if not t: return "No candidates yet."
        return "\n".join(_fmt(c, i+1) for i,c in enumerate(t))

    def by_status(status):
        m = sorted([c for c in cands if c.get("status","").lower()==status.lower()],
                   key=lambda c: c.get("score",0), reverse=True)
        return "\n".join(_fmt(c) for c in m) if m else f"No **{status}** candidates found."

    def upcoming_ivs():
        up = [i for i in interviews if i.get("status")=="Scheduled"]
        if not up: return "No upcoming interviews scheduled."
        return "\n".join(
            f"📌 **{iv['candidate_name']}** | {iv['role']} | "
            f"{iv.get('interview_date','')} {str(iv.get('interview_time',''))[:5]} | "
            f"{iv.get('mode','')} | Interviewer: {iv.get('interviewer','N/A')}"
            for iv in up[:8]
        )

    def find_candidate(hint):
        hint = hint.strip().lower()
        if len(hint) < 2: return "Please provide a name to search."
        m = [c for c in cands
             if hint in c.get("name","").lower()
             or hint in (c.get("email") or "").lower()]
        if not m: return f"❌ No candidate matching **'{hint}'**."
        out = []
        for c in m:
            sc = round(c.get("score",0)*100,1)
            out.append(
                f"{_score_bar(sc)} **{c['name']}**\n"
                f"  • Email: {c.get('email','N/A')}\n"
                f"  • Phone: {c.get('phone','N/A')}\n"
                f"  • Role: {c.get('role','N/A')}\n"
                f"  • Experience: {c.get('experience',0)} years\n"
                f"  • AI Score: **{sc}%**\n"
                f"  • Status: {c.get('status','N/A')}\n"
                f"  • Skills: {c.get('skills','N/A')}"
            )
        return "\n\n".join(out)

    def role_breakdown():
        if not roles_dist: return "No role data. Upload resumes first."
        tc = sum(r["total"] for r in roles_dist)
        lines = []
        for r in sorted(roles_dist, key=lambda x: x["total"], reverse=True):
            pct = round(r["total"]/tc*100,1) if tc else 0
            bar = "█"*int(pct/5) + "░"*(20-int(pct/5))
            lines.append(f"**{r['role']}**: {r['total']} candidates ({pct}%)\n`{bar}`")
        return "\n\n".join(lines)

    def job_role_list():
        if not job_roles: return "No job roles defined. Add via Job Matching page."
        return "\n".join(
            f"• **{r['title']}** — Min {r.get('min_experience',0)} yrs "
            f"| Skills: {(r.get('required_skills') or 'N/A')[:70]}"
            for r in job_roles
        )

    def top_skills():
        counter = Counter()
        for c in cands:
            for sk in (c.get("skills") or "").split(","):
                sk = sk.strip()
                if sk: counter[sk] += 1
        if not counter: return "No skills extracted yet. Upload resumes first."
        return "\n".join(f"• **{sk}**: {cnt} candidate(s)" for sk,cnt in counter.most_common(15))

    def role_stats(role_hint):
        m = [c for c in cands if role_hint.lower() in (c.get("role") or "").lower()]
        if not m: return f"No candidates found for **'{role_hint}'**."
        scores = [c.get("score",0)*100 for c in m]
        avg    = round(sum(scores)/len(scores),1)
        best   = max(m, key=lambda c: c.get("score",0))
        sl_cnt = sum(1 for c in m if c.get("status")=="Shortlisted")
        ranked = sorted(m, key=lambda c: c.get("score",0), reverse=True)
        return (
            f"**{role_hint.title()} — Role Summary**\n\n"
            f"• Total: **{len(m)}** | Shortlisted: **{sl_cnt}** | Avg Score: **{avg}%**\n"
            f"• Best: **{best['name']}** ({round(best.get('score',0)*100,1)}%)\n\n"
            "**Ranked:**\n" + "\n".join(_fmt(c,i+1) for i,c in enumerate(ranked))
        )

    def interview_questions(rh=""):
        bank = {
            "data scientist":[
                "Explain the bias-variance tradeoff.",
                "Walk me through a full ML project end-to-end.",
                "How do you handle class imbalance?",
                "What is regularization? L1 vs L2?",
                "Explain precision, recall and F1-score.",
                "How do you detect and handle data leakage?",
            ],
            "data analyst":[
                "SQL: find the second highest salary in a table.",
                "How do you validate the accuracy of your analysis?",
                "What KPIs matter for an e-commerce or SaaS business?",
                "Describe a time your data changed a business decision.",
                "LEFT vs INNER vs FULL OUTER join — explain each.",
                "How do you explain complex findings to non-technical teams?",
            ],
            "ml engineer":[
                "How do you deploy an ML model to production?",
                "What is model drift and how do you monitor it?",
                "Explain feature stores and when to use them.",
                "Batch inference vs online inference — differences?",
                "How do you build a CI/CD pipeline for ML?",
                "What containerisation strategy do you use for ML services?",
            ],
            "backend developer":[
                "Design a scalable REST API for a ride-sharing app.",
                "Explain database indexing — when can indexes hurt?",
                "What is a race condition and how do you prevent it?",
                "Synchronous vs asynchronous programming?",
                "How do you secure a REST API?",
                "Explain the CAP theorem with a real example.",
            ],
            "frontend developer":[
                "Explain React's virtual DOM and reconciliation.",
                "How do you optimize a React app for performance?",
                "Controlled vs uncontrolled components?",
                "How do you handle state management at scale?",
                "Explain CSS specificity and the box model.",
                "How do you implement accessibility (a11y)?",
            ],
            "software engineer":[
                "Explain SOLID principles with examples.",
                "Difference between a process and a thread?",
                "How do you debug a production incident?",
                "Describe your approach to code reviews.",
                "What design patterns have you applied and why?",
                "How do you ensure code quality and maintainability?",
            ],
        }
        for key, qs in bank.items():
            if key in rh or rh in key:
                return "\n".join(f"{i+1}. {q}" for i,q in enumerate(qs))
        return "\n".join([
            "1. Tell me about yourself and your most relevant experience.",
            "2. Describe the most challenging project you have worked on.",
            "3. How do you stay current with industry trends?",
            "4. Describe a conflict at work and how you resolved it.",
            "5. Where do you see yourself in 3–5 years?",
            "6. Why are you interested in this role?",
        ])

    def hiring_tips():
        return (
            "**✅ Hiring Best Practices**\n\n"
            "1. **Define criteria first** — set evaluation rubric before reviewing resumes.\n"
            "2. **Structured interviews** — same questions for every candidate.\n"
            "3. **Diverse panels** — 2–3 interviewers from different teams reduce bias.\n"
            "4. **Time-box your pipeline** — aim to close within 2 weeks of first contact.\n"
            "5. **Always give feedback** — even rejected candidates deserve a response.\n"
            "6. **AI scores are filters, not verdicts** — always do a human final review.\n"
            "7. **Reference checks** — mandatory before extending any offer.\n"
            "8. **Candidate experience matters** — poor experience = bad employer brand."
        )

    def scoring_advice():
        acc  = round(sl/total*100,1) if total else 0
        hire = round(hired/total*100,1) if total else 0
        return (
            f"**🎯 Scoring & Accuracy**\n\n"
            f"• Avg AI Match Score: **{avg_sc}%**\n"
            f"• Shortlisting Rate: **{acc}%** ({sl}/{total})\n"
            f"• Hiring Rate: **{hire}%** ({hired}/{total})\n\n"
            "**Thresholds:**\n"
            "• 🟢 ≥ 70% → Strong — shortlist\n"
            "• 🟡 40–69% → Moderate — manual review\n"
            "• 🔴 < 40% → Weak — likely reject"
        )

    def overview():
        acc      = round(sl/total*100,1) if total else 0
        hire_pct = round(hired/total*100,1) if total else 0
        iv_ct    = sum(1 for i in interviews if i.get("status")=="Scheduled")
        return (
            "**📊 Live Recruitment Overview**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| 📄 Total Candidates | **{total}** |\n"
            f"| ✅ Shortlisted | **{sl}** ({acc}%) |\n"
            f"| ❌ Rejected | **{rej}** |\n"
            f"| 🏆 Hired | **{hired}** ({hire_pct}%) |\n"
            f"| ⏳ Pending | **{pend}** |\n"
            f"| 🎯 Avg Score | **{avg_sc}%** |\n"
            f"| 📅 Interviews Scheduled | **{iv_ct}** |\n"
            f"| 💼 Job Roles | **{len(job_roles)}** |"
        )

    # ══════════════════════════════════════════════════════
    # INTENT ROUTING — specific first, generic last
    # ══════════════════════════════════════════════════════

    # ── "Which roles have most applicants?" ──────────────
    if _has(q, "which role","roles have","most applicant","applicants per role",
               "role breakdown","role distribution","candidates per role",
               "candidates by role","applicant count"):
        return f"**💼 Candidates by Role**\n\n{role_breakdown()}"

    # ── "What are hiring best practices?" ────────────────
    if _has(q, "best practice","hiring best","hiring practice","hiring tip",
               "hiring advice","improve hiring","how to hire","hiring process"):
        return hiring_tips()

    # ── "What skills are most common?" ───────────────────
    if _has(q, "what skill","most common skill","skill","tech stack",
               "technology","common tech","skills across","popular skill"):
        return f"**🛠 Top Skills Across All Candidates**\n\n{top_skills()}"

    # ── "Give me a full overview" ─────────────────────────
    if _has(q, "overview","full overview","give me","summary","dashboard",
               "stats","how many","total candidates","all candidates",
               "recruitment status","full report"):
        return overview()

    # ── "Show top 5 candidates" ───────────────────────────
    if _has(q, "top candidate","best candidate","highest score",
               "top 5","top 10","top 3","top 20","show top","best match","rank"):
        n = 20 if "20" in q else 10 if "10" in q else 3 if "3" in q else 5
        return f"**🏆 Top {n} Candidates by AI Score**\n\n{top_n(n)}"

    # ── "Show all shortlisted candidates" ────────────────
    if _has(q, "shortlist"):
        return f"**✅ Shortlisted Candidates ({sl})**\n\n{by_status('Shortlisted')}"

    # ── Other status filters ──────────────────────────────
    if _has(q, "reject"):
        return f"**❌ Rejected Candidates ({rej})**\n\n{by_status('Rejected')}"
    if _has(q, "hired","who got hired","who was hired"):
        return f"**🏆 Hired Candidates ({hired})**\n\n{by_status('Hired')}"
    if _has(q, "pending"):
        return f"**⏳ Pending Candidates ({pend})**\n\n{by_status('Pending')}"
    if _has(q, "on hold"):
        return f"**⏸ On Hold Candidates**\n\n{by_status('On Hold')}"

    # ── "Interview questions for Data Scientist" ──────────
    if _has(q, "interview question","what to ask","questions for","question for",
               "ask the candidate","screening question"):
        for rk in ["data scientist","data analyst","ml engineer","machine learning",
                   "backend developer","backend","frontend developer","frontend",
                   "software engineer"]:
            if rk in q:
                return f"**🎤 Interview Questions — {rk.title()}**\n\n{interview_questions(rk)}"
        return f"**🎤 General Interview Questions**\n\n{interview_questions()}"

    # ── "List upcoming interviews" ────────────────────────
    if _has(q, "upcoming interview","list interview","scheduled interview",
               "interview today","interview this week","upcoming schedule",
               "interview","schedule","calendar"):
        return f"**📅 Upcoming Interviews**\n\n{upcoming_ivs()}"

    # ── Find candidate by name ────────────────────────────
    if _has(q, "find candidate","find ","search for","search ","who is ",
               "tell me about","profile of","details of","info on","show me "):
        for kw in ["find candidate","search for","who is","profile of",
                   "details of","info on","tell me about","find","search","show me"]:
            if kw in q:
                hint = q.split(kw, 1)[-1].strip()
                hint = hint.replace("candidate","").replace("the","").strip()
                if len(hint) >= 2:
                    return find_candidate(hint)

    # ── Role-specific candidate stats ────────────────────
    for rk in ["data scientist","data analyst","ml engineer",
               "backend developer","frontend developer",
               "backend","frontend","software engineer"]:
        if rk in q and _has(q,"candidate","applicant","how many","who","list"):
            return role_stats(rk)

    # ── Job openings list ─────────────────────────────────
    if _has(q, "job opening","vacancy","vacancies","open position","job role",
               "available role","current opening","what roles","list roles",
               "list job","all roles","all job"):
        return f"**💼 Defined Job Roles**\n\n{job_role_list()}"

    # ── Scoring accuracy ──────────────────────────────────
    if _has(q, "score","accuracy","match score","average score",
               "scoring","threshold","ai accuracy","how accurate"):
        return scoring_advice()

    # ── JD writing ────────────────────────────────────────
    if _has(q, "write jd","write a jd","job description","good jd",
               "jd tip","create jd","how to write"):
        for rk in ["data scientist","data analyst","ml engineer","backend","frontend"]:
            if rk in q:
                return (
                    f"**📝 Writing a Great JD for {rk.title()}**\n\n"
                    "1. Open with a 2–3 sentence hook about why this role is exciting.\n"
                    "2. List 5–7 responsibilities using strong action verbs.\n"
                    "3. Separate must-have from nice-to-have skills.\n"
                    "4. Show the salary range — increases applications by ~30%.\n"
                    "5. State remote/hybrid policy explicitly.\n"
                    "6. Keep it under 600 words.\n"
                    "7. Avoid jargon: no 'rockstar', 'ninja', '10x engineer'.\n"
                    "8. Include growth paths and career progression."
                )
        return (
            "**📝 Writing a Great Job Description**\n\n"
            "1. Open with a compelling hook about the role.\n"
            "2. List 5–7 clear responsibilities.\n"
            "3. Separate must-have from nice-to-have requirements.\n"
            "4. Include salary range.\n"
            "5. State remote/hybrid policy.\n"
            "6. Keep under 600 words.\n"
            "7. Avoid jargon and buzzwords.\n"
            "8. Highlight growth opportunities."
        )

    # ── Help / greeting ───────────────────────────────────
    if _has(q, "help","hello","hi ","hey ","what can you","commands","guide me"):
        return (
            "**👋 Hello! I'm TalentAI HR Assistant.**\n\n"
            "Here's what I can answer:\n\n"
            "📊 **Overview**  →  *Give me a full overview*\n"
            "👤 **Candidates**  →  *Show top 5 candidates* | *Show all shortlisted*\n"
            "🔍 **Search**  →  *Find candidate [name]*\n"
            "💼 **Roles**  →  *Which roles have most applicants?*\n"
            "📅 **Interviews**  →  *List upcoming interviews*\n"
            "🎤 **Prep**  →  *Interview questions for Data Scientist*\n"
            "📝 **HR Advice**  →  *What are hiring best practices?*\n"
            "🛠 **Skills**  →  *What skills are most common?*\n"
            "🎯 **Scoring**  →  *What is our scoring accuracy?*"
        )

    # ── Fallback ──────────────────────────────────────────
    return (
        f"I have **{total}** candidates "
        f"({sl} shortlisted, {hired} hired, {pend} pending).\n\n"
        "I didn't quite catch that. Try one of these:\n"
        "• *Give me a full overview*\n"
        "• *Show top 5 candidates*\n"
        "• *Find candidate [name]*\n"
        "• *Interview questions for Data Scientist*\n"
        "• *Which roles have most applicants?*\n"
        "• Type **help** to see all commands."
    )


# ──────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────

QUICK_STARTERS = [
    "Give me a full overview",
    "Show top 5 candidates",
    "List upcoming interviews",
    "Which roles have most applicants?",
    "Interview questions for Data Scientist",
    "What are hiring best practices?",
    "What skills are most common?",
    "Show all shortlisted candidates",
]

def run():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.chat_history:
        st.markdown("**💡 Try asking:**")
        cols = st.columns(4)
        for i, starter in enumerate(QUICK_STARTERS):
            if cols[i % 4].button(starter, key=f"qs_{i}", use_container_width=True):
                reply = answer(starter)
                st.session_state.chat_history.append({"role":"user","content":starter})
                st.session_state.chat_history.append({"role":"assistant","content":reply})
                st.rerun()

    user_input = st.chat_input("Ask anything about candidates, interviews, or hiring…")
    if user_input:
        reply = answer(user_input)
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
