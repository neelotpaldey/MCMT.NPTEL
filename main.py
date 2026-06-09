import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="NPTEL Course Helper", page_icon="🎓", layout="wide")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"

st.markdown("""
<style>
div[data-testid="stMetric"]{border:1px solid #ddd;padding:10px;border-radius:10px}
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

with st.expander("Why NPTEL & IIT Certificates Matter", expanded=True):
    st.markdown("""
- Learn from IIT/IISc faculty
- Improve Resume & LinkedIn profile
- Valuable for Placements and Internships
- Industry-recognized certificates
- Useful for Higher Studies
""")

c1,c2=st.columns(2)
c1.info("VBSPU Students → Jaunpur (8666)")
c2.info("MGKVP Students → Varanasi (8664)")

st.sidebar.header("Filters")

search = st.sidebar.text_input("Search Topic / Course")

quick = st.sidebar.radio("Quick Stream",["All","CS","MGMT","Math"])

duration = st.sidebar.multiselect("Duration", sorted(df["Duration"].dropna().astype(str).unique()))
institute = st.sidebar.multiselect("Institute", sorted(df["Institute"].dropna().astype(str).unique()))

recommend = st.sidebar.selectbox("Recommended For",["All","BCA","MCA","Management","Mathematics"])

filtered = df.copy()

if search:
    mask = pd.Series(False,index=filtered.index)
    for col in filtered.columns:
        mask |= filtered[col].astype(str).str.contains(search,case=False,na=False)
    filtered = filtered[mask]

if duration:
    filtered = filtered[filtered["Duration"].astype(str).isin(duration)]

if institute:
    filtered = filtered[filtered["Institute"].astype(str).isin(institute)]

if quick == "CS":
    filtered = filtered[filtered["Key"].astype(str).str.contains("CS",case=False,na=False)]
elif quick == "MGMT":
    filtered = filtered[filtered["Key"].astype(str).str.contains("MGMT",case=False,na=False)]
elif quick == "Math":
    filtered = filtered[filtered["Key"].astype(str).str.contains("MATH",case=False,na=False)]

reco = {
"BCA":["python","java","web","dbms","ai","cloud"],
"MCA":["machine learning","ai","data science","cloud"],
"Management":["management","finance","marketing"],
"Mathematics":["mathematics","statistics","calculus"]
}

if recommend != "All":
    mask = pd.Series(False,index=filtered.index)
    for word in reco[recommend]:
        mask |= filtered["Course Name"].astype(str).str.contains(word,case=False,na=False)
    filtered = filtered[mask]

m1,m2,m3,m4 = st.columns(4)
m1.metric("Courses",len(filtered))
m2.metric("Institutes",filtered["Institute"].nunique())
m3.metric("Disciplines",filtered["Discipline"].nunique())
m4.metric("Categories",filtered["Key"].nunique())

st.divider()

today = pd.Timestamp.today()
closing = filtered[filtered["Enrollment End date"].notna() & ((filtered["Enrollment End date"]-today).dt.days <= 7) & ((filtered["Enrollment End date"]-today).dt.days >= 0)]

if not closing.empty:
    st.warning(f"⚠️ {len(closing)} course(s) closing enrollment within 7 days.")

for _,row in filtered.iterrows():
    with st.container():
        st.subheader(row["Course Name"])

        a,b = st.columns([3,1])

        with a:
            st.write(f"**Institute:** {row['Institute']}")
            st.write(f"**Discipline:** {row['Discipline']}")
            st.write(f"**Duration:** {row['Duration']}")
            st.write(f"**Start Date:** {row['Start date']}")
            st.write(f"**Exam Date:** {row['Exam date']}")

        with b:
            url = row.get("Click here to Join the course")
            if pd.notna(url):
                st.link_button("Enroll Now", str(url), use_container_width=True)

        with st.expander("Full Details"):
            st.dataframe(pd.DataFrame({"Field":row.index,"Value":row.values}), use_container_width=True, hide_index=True)

        st.divider()

st.download_button(
    "Download Filtered Courses",
    filtered.to_csv(index=False),
    "nptel_courses.csv",
    "text/csv"
)
