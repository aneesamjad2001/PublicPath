import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="PublicPath",
    page_icon="🏛️",
    layout="wide"
)

st.markdown("""
    <style>
    .job-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 4px solid #1a5276;
    }
    .job-title { font-size: 20px; font-weight: 700; color: #1a5276; }
    .job-agency { font-size: 15px; color: #555; margin-top: 4px; }
    .job-meta { font-size: 14px; color: #777; margin-top: 8px; }
    .stat-box {
        background-color: #1a5276;
        color: white;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .stat-number { font-size: 32px; font-weight: 700; }
    .stat-label { font-size: 14px; opacity: 0.85; }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🏛️ PublicPath")
st.markdown("#### Find your path into public service")
st.markdown("---")

@st.cache_data
def get_jobs():
    response = supabase.table("jobs").select("*").execute()
    return response.data

all_jobs = get_jobs()

agencies = sorted(set(j["agency"] for j in all_jobs))
locations = sorted(set(j["location"] for j in all_jobs))

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(all_jobs)}</div>
            <div class="stat-label">Jobs available</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(agencies)}</div>
            <div class="stat-label">Federal agencies</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(locations)}</div>
            <div class="stat-label">Locations</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Search & filter")

col1, col2 = st.columns([2, 1])

with col1:
    keyword = st.text_input("", placeholder="🔍  Search by job title or agency...")

with col2:
    location_filter = st.selectbox("Location", ["All locations"] + locations)

jobs = all_jobs

if keyword:
    jobs = [j for j in jobs if
            keyword.lower() in j["title"].lower() or
            keyword.lower() in j["agency"].lower()]

if location_filter != "All locations":
    jobs = [j for j in jobs if j["location"] == location_filter]

st.markdown("---")
st.markdown(f"**{len(jobs)} jobs found**")
st.markdown("")

if len(jobs) == 0:
    st.info("No jobs found. Try a different keyword or filter.")
else:
    for job in jobs:
        salary_min = f"${float(job['salary_min']):,.0f}" if job['salary_min'] else "N/A"
        salary_max = f"${float(job['salary_max']):,.0f}" if job['salary_max'] else "N/A"
        close_date = job['close_date'][:10] if job['close_date'] else "N/A"

        st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{job['title']}</div>
                <div class="job-agency">{job['agency']}</div>
                <div class="job-meta">
                    📍 {job['location']} &nbsp;|&nbsp;
                    💰 {salary_min} – {salary_max} &nbsp;|&nbsp;
                    ⏰ Closes {close_date}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.link_button("View Job →", job["url"])
        st.markdown("")