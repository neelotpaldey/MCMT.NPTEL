import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="NPTEL Course Helper", page_icon="🎓", layout="wide")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"
SWAYAM_LOGIN_URL = "https://swayam-sso.swayam2.ac.in/signin?response_type=code&client_id=swayam-node1-production&redirect_uri=%2Fe-learning%2Fpreview%2Fnoc26_ge105&state=NAnFZVTTDK46j2CKTCOiYNPw9DET4H"

st.markdown("""
<style>
div[data-testid="stMetric"]{border:1px solid #ddd;padding:10px;border-radius:10px}
.step-box {
    background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
    border-left: 4px solid #667eea;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 8px 0;
}
.step-number {
    font-size: 1.3em;
    font-weight: 700;
    color: #667eea;
}
.highlight-box {
    background: #fff8e1;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    csv_file = Path(__file__).parent / "NPTEL.csv"
    try:
        df = pd.read_csv(csv_file) if csv_file.exists() else pd.read_csv(GOOGLE_SHEET_URL)
    except Exception:
        df = pd.read_csv(GOOGLE_SHEET_URL)

    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]

    for col in ["Start date","End date","Exam date","Enrollment End date","Exam Registration End date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

df = load_data()

st.title("🎓 NPTEL Course Helper")

# ── STEP-BY-STEP ENROLLMENT INSTRUCTIONS ──────────────────────────────────────
with st.expander("📋 How to Enroll — Step-by-Step Instructions", expanded=True):
    st.markdown("### 🚀 Quick Enrollment Guide")

    st.markdown("""
<div class="step-box">
<span class="step-number">Step 1 — Login / Register on Swayam</span><br><br>
You must have a Swayam account before you can enroll in any NPTEL course.<br>
👉 <a href="{login_url}" target="_blank"><strong>Click here to Login / Register on Swayam</strong></a><br>
<small>Create a free account using your email ID if you don't have one already.</small>
</div>

<div class="step-box">
<span class="step-number">Step 2 — Find Your Course Below</span><br><br>
Use the filters in the left sidebar to search by topic, discipline, institute, or your program (BCA / MCA / Management / Mathematics).
</div>

<div class="step-box">
<span class="step-number">Step 3 — Click "Enroll Now"</span><br><br>
Once logged in to Swayam, click the <strong>Enroll Now</strong> button on any course card below.
The button will take you directly to the course page where you can complete your enrollment in one click.
</div>

<div class="step-box">
<span class="step-number">Step 4 — Enter Your College Code During Course Registration</span><br><br>
When registering for the proctored exam, enter your college's NPTEL Local Chapter code:
<ul>
<li>🏫 <strong>VBSPU Students</strong> — Microtek College of Management and Technology, Jaunpur &nbsp;|&nbsp; Code: <strong>8666</strong></li>
<li>🏫 <strong>MGKVP / AKTU Students</strong> — Microtek College of Management and Technology, Varanasi &nbsp;|&nbsp; Code: <strong>8664</strong></li>
</ul>
Entering the correct code ensures your certificate is linked to your institution.
</div>
""".format(login_url=SWAYAM_LOGIN_URL), unsafe_allow_html=True)

    st.info("⚠️ **Important:** Always log in to Swayam first before clicking Enroll Now — otherwise the enrollment button may not work correctly.")

# ── WHY NPTEL ─────────────────────────────────────────────────────────────────
with st.expander("🌟 Why NPTEL & IIT Certificates Matter"):
    st.markdown("""
- 📚 Learn from IIT / IISc faculty
- 📄 Improve your Resume & LinkedIn profile
- 💼 Valuable for Placements and Internships
- 🏆 Industry-recognized certificates
- 🎓 Useful for Higher Studies & PhD applications
""")

# ── COLLEGE CODE QUICK REFERENCE ──────────────────────────────────────────────
st.markdown("### 🏫 Your College Code (for Exam Registration)")
c1, c2 = st.columns(2)
c1.success("**VBSPU Students**\nMicrotek College of Management and Technology\n**Jaunpur → Code: 8666**")
c2.success("**MGKVP / AKTU Students**\nMicrotek College of Management and Technology\n**Varanasi → Code: 8664**")

st.markdown(
    f"🔐 **Not registered on Swayam yet?** &nbsp; [Login / Register here]({SWAYAM_LOGIN_URL})",
    unsafe_allow_html=False
)

st.divider()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

search = st.sidebar.text_input("Search Topic / Course")

quick = st.sidebar.radio("Quick Stream", ["All", "CS", "MGMT", "Math"])

duration = st.sidebar.multiselect("Duration", sorted(df["Duration"].dropna().astype(str).unique()))
institute = st.sidebar.multiselect("Institute", sorted(df["Institute"].dropna().astype(str).unique()))

recommend = st.sidebar.selectbox("Recommended For", ["All", "BCA", "MCA", "Management", "Mathematics"])

filtered = df.copy()

if search:
    mask = pd.Series(False, index=filtered.index)
    for col in filtered.columns:
        mask |= filtered[col].astype(str).str.contains(search, case=False, na=False)
    filtered = filtered[mask]

if duration:
    filtered = filtered[filtered["Duration"].astype(str).isin(duration)]

if institute:
    filtered = filtered[filtered["Institute"].astype(str).isin(institute)]

if quick == "CS":
    filtered = filtered[filtered["Key"].astype(str).str.contains("CS", case=False, na=False)]
elif quick == "MGMT":
    filtered = filtered[filtered["Key"].astype(str).str.contains("MGMT", case=False, na=False)]
elif quick == "Math":
    filtered = filtered[filtered["Key"].astype(str).str.contains("MATH", case=False, na=False)]

reco = {
    "BCA": ["python", "java", "web", "dbms", "ai", "cloud"],
    "MCA": ["machine learning", "ai", "data science", "cloud"],
    "Management": ["management", "finance", "marketing"],
    "Mathematics": ["mathematics", "statistics", "calculus"]
}

if recommend != "All":
    mask = pd.Series(False, index=filtered.index)
    for word in reco[recommend]:
        mask |= filtered["Course Name"].astype(str).str.contains(word, case=False, na=False)
    filtered = filtered[mask]

# ── METRICS ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Courses", len(filtered))
m2.metric("Institutes", filtered["Institute"].nunique())
m3.metric("Disciplines", filtered["Discipline"].nunique())
m4.metric("Categories", filtered["Key"].nunique())

st.divider()

# ── ENROLLMENT DEADLINE WARNING ───────────────────────────────────────────────
today = pd.Timestamp.today()
closing = filtered[
    filtered["Enrollment End date"].notna() &
    ((filtered["Enrollment End date"] - today).dt.days <= 7) &
    ((filtered["Enrollment End date"] - today).dt.days >= 0)
]

if not closing.empty:
    st.warning(f"⚠️ {len(closing)} course(s) closing enrollment within 7 days! Enroll soon.")

# ── COURSE CARDS ──────────────────────────────────────────────────────────────
for _, row in filtered.iterrows():
    with st.container():
        st.subheader(row["Course Name"])

        a, b = st.columns([3, 1])

        with a:
            st.write(f"**Institute:** {row['Institute']}")
            st.write(f"**Discipline:** {row['Discipline']}")
            st.write(f"**Duration:** {row['Duration']}")
            st.write(f"**Start Date:** {row['Start date']}")
            st.write(f"**Exam Date:** {row['Exam date']}")

        with b:
            url = row.get("Click here to Join the course")
            if pd.notna(url):
                st.link_button("Enroll Now 🚀", str(url), use_container_width=True)
            st.caption("Login to Swayam first →")
            st.link_button("Login / Register", SWAYAM_LOGIN_URL, use_container_width=True)

        with st.expander("Full Details"):
            st.dataframe(
                pd.DataFrame({"Field": row.index, "Value": row.values}),
                use_container_width=True,
                hide_index=True
            )

        st.divider()

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.download_button(
    "⬇️ Download Filtered Courses (CSV)",
    filtered.to_csv(index=False),
    "nptel_courses.csv",
    "text/csv"
)
