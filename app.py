import streamlit as st
import pandas as pd
from pypdf import PdfReader
import matplotlib.pyplot as plt
import re
import os
import time
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ---------------- SPLASH SCREEN ----------------
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("""
    <div style="text-align:center; padding-top:150px;">
        <h1 style="font-size:40px;">🚀 AI Resume Analyzer</h1>
        <p style="font-size:18px;">Smart Recruitment Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading application..."):
        time.sleep(2)

    st.session_state.loaded = True
    st.rerun()

# ---------------- STYLE ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
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

st.sidebar.markdown("---")
st.sidebar.success("👩‍💻 Developed by Janeesha Y")

# ---------------- FUNCTION ----------------
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for p in reader.pages:
        if p.extract_text():
            text += p.extract_text()
    return text.lower()

# ---------------- JOB DATA ----------------
jobs = pd.DataFrame({
    "Role": [
        "Data Analyst","Web Developer","Machine Learning Engineer",
        "Software Developer","Cybersecurity Analyst",
        "Cloud Engineer","Business Analyst"
    ],
    "Skills": [
        "python sql excel powerbi statistics",
        "html css javascript react",
        "python tensorflow pytorch nlp",
        "java python c++ algorithms",
        "network security ethical hacking",
        "aws docker kubernetes cloud",
        "business analysis communication excel"
    ]
})

# ================= ANALYZER =================
if page == "🏠 Analyzer":

    st.title("🚀 AI Resume Analyzer")
    st.caption("AI-powered recruitment intelligence system")

    uploaded_files = st.file_uploader("Upload Resume(s)", type=["pdf"], accept_multiple_files=True)
    job_desc = st.text_area("📄 Paste Job Description (Optional)")

    if uploaded_files:

        start = time.time()
        df_hist = pd.read_csv(DATA_FILE)
        today = str(datetime.now().date())

        results = []

        for file in uploaded_files:

            resume_text = extract_text(file)

            # -------- INFO --------
            name = resume_text.split("\n")[0]

            email = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", resume_text)
            email = email[0] if email else "Not Found"

            phone = re.findall(r"\b\d{10}\b", resume_text)
            phone = phone[0] if phone else "Not Found"

            st.markdown("### 👤 Candidate Details")
            st.write(f"**Name:** {name}")
            st.write(f"**Email:** {email}")
            st.write(f"**Phone:** {phone}")

            # -------- MATCHING --------
            if job_desc:
                docs = [resume_text, job_desc]
                tfidf = TfidfVectorizer().fit_transform(docs)
                sim = cosine_similarity(tfidf[0:1], tfidf[1:])
                best_score = sim[0][0]*100
                best_role = "Custom Job Match"
            else:
                docs = [resume_text] + list(jobs["Skills"])
                tfidf = TfidfVectorizer().fit_transform(docs)
                sim = cosine_similarity(tfidf[0:1], tfidf[1:])
                top = sim[0].argsort()[-3:][::-1]

                best_match = top[0]
                best_score = sim[0][best_match]*100
                best_role = jobs.iloc[best_match]["Role"]

            rating = round(best_score/20,2)
            results.append((name,best_score))

            st.markdown("### 🎯 Analysis Result")
            st.write(f"**Recommended Role:** {best_role}")
            st.write(f"**Score:** {rating} / 5")
            st.progress(int(best_score))

            st.markdown("---")

            # -------- SKILLS --------
            if not job_desc:
                job_skills = jobs.iloc[best_match]["Skills"].split()
                words = resume_text.split()

                matched = [s for s in job_skills if s in words]
                missing = [s for s in job_skills if s not in words]

                coverage = (len(matched)/len(job_skills))*100
                ats = ((best_score*0.6 + coverage*0.4)/100)*5

                st.markdown("### 🧠 Skill Analysis")
                st.write("✔ Matched:", matched)
                st.write("❌ Missing:", missing)
                st.write(f"Coverage: {coverage:.2f}%")
                st.write(f"ATS Score: {ats:.2f}/5")

            # -------- GRAPH --------
            st.markdown("### 📊 Score Breakdown")

            breakdown = pd.DataFrame({
                "Category": ["Skill","Content","Experience"],
                "Score": [best_score*0.6, len(resume_text.split())*0.2, 20]
            })

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                fig, ax = plt.subplots(figsize=(4,2.5))
                ax.bar(breakdown["Category"], breakdown["Score"])
                ax.set_xlabel("Criteria")
                ax.set_ylabel("Score")
                plt.tight_layout()
                st.pyplot(fig)

            # -------- CONFIDENCE --------
            st.markdown("### 🎯 Confidence Level")

            if rating >= 3:
                st.success("Good confidence")
            elif rating >= 2:
                st.info("Moderate confidence")
            else:
                st.warning("Needs improvement")

            st.markdown("---")

            # SAVE
            df_hist = pd.concat([
                df_hist,
                pd.DataFrame([[name,rating,today]], columns=["Name","Score","Date"])
            ])

        df_hist.to_csv(DATA_FILE,index=False)

        # -------- MULTI --------
        if len(results)>1:
            df_multi = pd.DataFrame(results, columns=["Name","Score"])

            st.markdown("### 🏆 Best Candidate")
            top = df_multi.sort_values(by="Score",ascending=False).iloc[0]
            st.success(f"{top['Name']}")

        end = time.time()
        st.caption(f"⏱ Analysis time: {end-start:.2f} sec")

# ================= DASHBOARD =================
elif page == "📊 Dashboard":

    st.title("📊 Dashboard")

    df = pd.read_csv(DATA_FILE)

    if not df.empty:

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Candidates",len(df))
        col2.metric("Average Score",f"{df['Score'].mean():.2f}")
        col3.metric("Top Score",f"{df['Score'].max():.2f}")

        st.markdown("### 📊 Candidate Scores")

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            fig, ax = plt.subplots(figsize=(4.5,2.5))
            ax.bar(df["Name"], df["Score"])
            ax.set_xlabel("Candidate Name")
            ax.set_ylabel("Score (Out of 5)")
            plt.xticks(rotation=30)
            plt.tight_layout()
            st.pyplot(fig)

        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download Report",csv,"report.csv","text/csv")

# ================= LEADERBOARD =================
elif page == "🏆 Leaderboard":

    st.title("🏆 Leaderboard")

    df = pd.read_csv(DATA_FILE)

    if not df.empty:
        min_score = st.slider("Filter Score",0.0,5.0,0.0)
        df = df[df["Score"]>=min_score]
        df = df.sort_values(by="Score",ascending=False)

        st.dataframe(df)
