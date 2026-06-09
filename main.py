import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="NPTEL Course Helper", page_icon="🎓", layout="wide")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"
SWAYAM_LOGIN_URL = "https://swayam-sso.swayam2.ac.in/signin?response_type=code&client_id=swayam-node1-production&redirect_uri=%2Fe-learning%2Fpreview%2Fnoc26_ge105&state=NAnFZVTTDK46j2CKTCOiYNPw9DET4H"

st.markdown("""
<style>
.block-container {padding-top:1rem;}
.course-card{padding:1rem;border:1px solid #ddd;border-radius:12px;margin-bottom:10px;}
.hero{padding:20px;border-radius:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;text-align:center;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    local = Path(__file__).parent / "NPTEL.csv"
    try:
        df = pd.read_csv(local) if local.exists() else pd.read_csv(GOOGLE_SHEET_URL)
    except Exception:
        df = pd.read_csv(GOOGLE_SHEET_URL)

    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]

    for c in ["Start date","End date","Exam date","Enrollment End date","Exam Registration End date"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    return df

df = load_data()

st.markdown("""
<div class="hero">
<h1>🎓 NPTEL Course Helper</h1>
<p>Find IIT & IISc Courses • Enroll Faster • Build Your Resume</p>
</div>
""", unsafe_allow_html=True)

st.link_button("🔐 Login / Register on SWAYAM", SWAYAM_LOGIN_URL, use_container_width=True)

with st.expander("📋 Enrollment Instructions", expanded=True):
    st.markdown("""
1. Login/Register on SWAYAM.
2. Search a course below.
3. Click **Enroll Now**.
4. Use Local Chapter Code during registration.

**VBSPU Students** → Microtek College of Management and Technology, Jaunpur (**8666**)  
**MGKVP & AKTU Students** → Microtek College of Management and Technology, Varanasi (**8664**)
""")

c1,c2=st.columns(2)
c1.success("VBSPU → MCMT Jaunpur (8666)")
c2.success("MGKVP / AKTU → MCMT Varanasi (8664)")

st.sidebar.header("🔍 Filters")
st.sidebar.caption("📱 Mobile: open sidebar from top-left menu")

search = st.sidebar.text_input("Search")
course_pick = st.sidebar.selectbox(
    "Quick Course Search",
    [""] + sorted(df["Course Name"].dropna().astype(str).unique())[:1000]
)

quick = st.sidebar.radio("Quick Stream", ["All","CS","MGMT","Math"])

duration = st.sidebar.multiselect("Duration", sorted(df["Duration"].dropna().astype(str).unique()))
institute = st.sidebar.multiselect("Institute", sorted(df["Institute"].dropna().astype(str).unique()))

start_after = st.sidebar.date_input("Starts After", value=None)
exam_before = st.sidebar.date_input("Exam Before", value=None)

filtered = df.copy()

if course_pick:
    search = course_pick

if search:
    mask = pd.Series(False,index=filtered.index)
    for col in filtered.columns:
        mask |= filtered[col].astype(str).str.contains(search,case=False,na=False)
    filtered = filtered[mask]

if duration:
    filtered = filtered[filtered["Duration"].astype(str).isin(duration)]

if institute:
    filtered = filtered[filtered["Institute"].astype(str).isin(institute)]

if start_after and "Start date" in filtered.columns:
    filtered = filtered[filtered["Start date"] >= pd.to_datetime(start_after)]

if exam_before and "Exam date" in filtered.columns:
    filtered = filtered[filtered["Exam date"] <= pd.to_datetime(exam_before)]

if quick == "CS":
    filtered = filtered[filtered["Key"].astype(str).str.contains("CS", case=False, na=False)]
elif quick == "MGMT":
    filtered = filtered[filtered["Key"].astype(str).str.contains("MGMT", case=False, na=False)]
elif quick == "Math":
    filtered = filtered[filtered["Key"].astype(str).str.contains("MATH", case=False, na=False)]

m1,m2,m3,m4 = st.columns(4)
m1.metric("Courses", len(filtered))
m2.metric("Institutes", filtered["Institute"].nunique())
m3.metric("Disciplines", filtered["Discipline"].nunique())
m4.metric("Categories", filtered["Key"].nunique())

st.divider()
st.subheader("⭐ Featured Courses")
for _, row in filtered.head(5).iterrows():
    st.info(f"{row['Course Name']} • {row['Institute']}")

st.divider()

for _, row in filtered.iterrows():
    st.markdown(f"### {row['Course Name']}")

    enroll_end = row.get("Enrollment End date")
    if pd.notna(enroll_end):
        days = (enroll_end - pd.Timestamp.today()).days
        if 0 <= days <= 7:
            st.error(f"⏳ Enrollment closes in {days} days")

    st.write(f"**Institute:** {row.get('Institute','')}")
    st.write(f"**Duration:** {row.get('Duration','')}")
    st.write(f"**Start Date:** {row.get('Start date','')}")
    st.write(f"**Exam Date:** {row.get('Exam date','')}")

    url = row.get("Click here to Join the course")
    if pd.notna(url):
        st.link_button("🚀 Enroll Now", str(url), use_container_width=True)

    with st.expander("Full Details"):
        st.dataframe(pd.DataFrame({"Field":row.index,"Value":row.values}), use_container_width=True, hide_index=True)

st.download_button(
    "⬇ Download Filtered Courses",
    filtered.to_csv(index=False),
    "nptel_courses.csv",
    "text/csv"
)
