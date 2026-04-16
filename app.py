import streamlit as st
import pandas as pd
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

# ---------------- FILE STORAGE ----------------
DATA_FILE = "history.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Name","Score","Date"]).to_csv(DATA_FILE, index=False)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Analyzer","📊 Dashboard","🏆 Leaderboard"])
st.sidebar.success("👩‍💻 Developed by Janeesha Y")

# ---------------- TEXT EXTRACTION (SAFE) ----------------
def extract_text(file):
    try:
        text = file.read().decode("latin-1")
        return text.lower()
    except:
        return ""

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

    uploaded_files = st.file_uploader("Upload Resume(s)", type=["pdf"], accept_multiple_files=True)
    job_desc = st.text_area("📄 Job Description (Optional)")

    if uploaded_files:

        start = time.time()
        df_hist = pd.read_csv(DATA_FILE)
        today = str(datetime.now().date())

        results = []

        for file in uploaded_files:

            resume_text = extract_text(file)

            name = resume_text.split("\n")[0] if resume_text else "Candidate"

            email = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", resume_text)
            email = email[0] if email else "Not Found"

            phone = re.findall(r"\b\d{10}\b", resume_text)
            phone = phone[0] if phone else "Not Found"

            st.subheader(f"👤 {name}")
            st.write(f"📧 {email}")
            st.write(f"📞 {phone}")

            # MATCHING
            if job_desc:
                docs = [resume_text, job_desc]
                tfidf = TfidfVectorizer().fit_transform(docs)
                sim = cosine_similarity(tfidf[0:1], tfidf[1:])
                best_score = sim[0][0]*100
                best_role = "Custom Match"
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

            st.write(f"🎯 Role: {best_role}")
            st.write(f"⭐ Score: {rating} / 5")
            st.progress(int(best_score))

            st.markdown("---")

            # SIMPLE SCORE BREAKDOWN
            st.subheader("📊 Score Breakdown")
            st.write(f"Skill Score: {round(best_score*0.6,2)}")
            st.write(f"Content Score: {round(len(resume_text.split())*0.2,2)}")
            st.write("Experience Score: 20")

            # CONFIDENCE
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

        # BEST CANDIDATE
        if len(results)>1:
            df_multi = pd.DataFrame(results, columns=["Name","Score"])
            top = df_multi.sort_values(by="Score",ascending=False).iloc[0]
            st.success(f"🏆 Best Candidate: {top['Name']}")

        st.caption(f"⏱ Analysis Time: {time.time()-start:.2f} sec")

# ================= DASHBOARD =================
elif page == "📊 Dashboard":

    st.title("📊 Dashboard")
    df = pd.read_csv(DATA_FILE)

    if not df.empty:
        st.metric("Total Candidates", len(df))
        st.metric("Average Score", f"{df['Score'].mean():.2f}")
        st.metric("Top Score", f"{df['Score'].max():.2f}")

        st.dataframe(df)

        st.download_button("📥 Download Report", df.to_csv(index=False), "report.csv")

# ================= LEADERBOARD =================
elif page == "🏆 Leaderboard":

    st.title("🏆 Leaderboard")
    df = pd.read_csv(DATA_FILE)

    if not df.empty:
        min_score = st.slider("Filter Score",0.0,5.0,0.0)
        df = df[df["Score"]>=min_score]
        df = df.sort_values(by="Score",ascending=False)
        st.dataframe(df)
