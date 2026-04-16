import streamlit as st
import pandas as pd
import re
import os
import time
from datetime import datetime

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ---------------- SPLASH ----------------
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("""
    <div style="text-align:center; padding-top:150px;">
        <h1>🚀 AI Resume Analyzer</h1>
        <p>Smart Recruitment Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.loaded = True
    st.rerun()

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stButton>button {
    background-color: #4CAF50;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FILE ----------------
DATA_FILE = "history.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Name","Score","Date"]).to_csv(DATA_FILE, index=False)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Analyzer","📊 Dashboard","🏆 Leaderboard"])
st.sidebar.success("👩‍💻 Developed by Janeesha Y")

# ---------------- TEXT EXTRACTION ----------------
def extract_text(file):
    try:
        return file.read().decode("latin-1").lower()
    except:
        return ""

# ---------------- JOB DATA ----------------
jobs = {
    "Data Analyst": ["python","sql","excel","powerbi"],
    "Web Developer": ["html","css","javascript","react"],
    "Machine Learning Engineer": ["python","tensorflow","nlp"],
    "Software Developer": ["java","c++","python","algorithms"],
    "Cybersecurity Analyst": ["network","security","hacking"],
    "Cloud Engineer": ["aws","docker","cloud"],
    "Business Analyst": ["excel","communication","analysis"]
}

# ================= ANALYZER =================
if page == "🏠 Analyzer":

    st.title("🚀 AI Resume Analyzer")

    uploaded_files = st.file_uploader("Upload Resume(s)", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:

        df_hist = pd.read_csv(DATA_FILE)
        today = str(datetime.now().date())
        results = []

        for file in uploaded_files:

            text = extract_text(file)

            name = text.split("\n")[0] if text else "Candidate"

            email = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
            email = email[0] if email else "Not Found"

            phone = re.findall(r"\b\d{10}\b", text)
            phone = phone[0] if phone else "Not Found"

            st.subheader(f"👤 {name}")
            st.write(f"📧 {email}")
            st.write(f"📞 {phone}")

            # SIMPLE MATCHING
            scores = {}
            for role, skills in jobs.items():
                match = sum(1 for skill in skills if skill in text)
                scores[role] = match / len(skills)

            best_role = max(scores, key=scores.get)
            best_score = scores[best_role] * 100

            rating = round(best_score / 20, 2)

            results.append((name, best_score))

            st.write(f"🎯 Role: {best_role}")
            st.write(f"⭐ Score: {rating} / 5")
            st.progress(int(best_score))

            # Breakdown
            st.subheader("📊 Score Breakdown")
            st.write(f"Skill Match: {round(best_score,2)}")
            st.write(f"Keyword Strength: {len(text.split())}")
            st.write("Experience Estimate: Medium")

            # Confidence
            if rating >= 3:
                st.success("Good confidence")
            elif rating >= 2:
                st.info("Moderate confidence")
            else:
                st.warning("Needs improvement")

            st.markdown("---")

            df_hist = pd.concat([
                df_hist,
                pd.DataFrame([[name, rating, today]], columns=["Name","Score","Date"])
            ])

        df_hist.to_csv(DATA_FILE, index=False)

        if len(results) > 1:
            best = sorted(results, key=lambda x: x[1], reverse=True)[0]
            st.success(f"🏆 Best Candidate: {best[0]}")

# ================= DASHBOARD =================
elif page == "📊 Dashboard":

    st.title("📊 Dashboard")
    df = pd.read_csv(DATA_FILE)

    if not df.empty:
        st.metric("Total Candidates", len(df))
        st.metric("Average Score", round(df["Score"].mean(),2))
        st.metric("Top Score", round(df["Score"].max(),2))

        st.dataframe(df)

        st.download_button("Download Report", df.to_csv(index=False), "report.csv")

# ================= LEADERBOARD =================
elif page == "🏆 Leaderboard":

    st.title("🏆 Leaderboard")
    df = pd.read_csv(DATA_FILE)

    if not df.empty:
        df = df.sort_values(by="Score", ascending=False)
        st.dataframe(df)
