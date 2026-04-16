import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Analyzer","📊 Dashboard","🏆 Leaderboard"])
st.sidebar.success("👩‍💻 Developed by Janeesha Y")

# ---------------- STORAGE ----------------
DATA_FILE = "history.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Name","Score","Date"]).to_csv(DATA_FILE, index=False)

# ---------------- TEXT EXTRACTION (CLEAN) ----------------
def extract_text(file):
    try:
        content = file.read()
        text = content.decode("latin-1", errors="ignore")

        # remove pdf garbage like %PDF
        text = re.sub(r"%PDF.*", "", text)

        return text.lower()
    except:
        return ""

# ---------------- JOB DATA ----------------
jobs = {
    "Data Analyst": ["python","sql","excel","powerbi"],
    "Web Developer": ["html","css","javascript","react"],
    "Machine Learning Engineer": ["python","tensorflow","nlp"],
    "Software Developer": ["java","c++","python","algorithms"],
    "Cybersecurity Analyst": ["network","security"],
    "Cloud Engineer": ["aws","docker","cloud"],
    "Business Analyst": ["excel","communication","analysis"]
}

# ================= ANALYZER =================
if page == "🏠 Analyzer":

    st.title("🚀 AI Resume Analyzer")

    files = st.file_uploader("Upload Resume(s)", type=["pdf"], accept_multiple_files=True)

    if files:
        df_hist = pd.read_csv(DATA_FILE)
        today = str(datetime.now().date())
        results = []

        for file in files:

            text = extract_text(file)

            # Extract details
            name = text.split("\n")[0].strip() if text else "Candidate"

            email = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
            email = email[0] if email else "Not Found"

            phone = re.findall(r"\b\d{10}\b", text)
            phone = phone[0] if phone else "Not Found"

            st.subheader(f"👤 {name}")
            st.write(f"📧 {email}")
            st.write(f"📞 {phone}")

            # Skill Matching
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
            st.write(f"Keyword Count: {len(text.split())}")
            st.write("Experience Level: Estimated")

            # Confidence
            if rating >= 3:
                st.success("Good confidence")
            elif rating >= 2:
                st.info("Moderate confidence")
            else:
                st.warning("Needs improvement")

            st.markdown("---")

            # Save history
            df_hist = pd.concat([
                df_hist,
                pd.DataFrame([[name, rating, today]], columns=["Name","Score","Date"])
            ])

        df_hist.to_csv(DATA_FILE, index=False)

        # Best candidate
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

# ================= LEADERBOARD =================
elif page == "🏆 Leaderboard":

    st.title("🏆 Leaderboard")
    df = pd.read_csv(DATA_FILE)

    if not df.empty:
        df = df.sort_values(by="Score", ascending=False)
        st.dataframe(df)
