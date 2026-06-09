import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="NPTEL Course Helper", page_icon="🎓", layout="wide")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"

@st.cache_data(ttl=3600)
def load_data():
    csv_file = Path(__file__).parent / "NPTEL.csv"

    try:
        if csv_file.exists():
            df = pd.read_csv(csv_file)
        else:
            df = pd.read_csv(GOOGLE_SHEET_URL)
    except Exception:
        df = pd.read_csv(GOOGLE_SHEET_URL)

    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]

    date_cols = [
        "Start date",
        "End date",
        "Exam date",
        "Enrollment End date",
        "Exam Registration End date"
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

df = load_data()

st.title("🎓 NPTEL Course Helper")

st.markdown("""
### Why NPTEL & IIT Certificates Matter?

✅ Learn from IIT & IISc faculty

✅ Improve Resume and LinkedIn Profile

✅ Useful for Placements, Internships and Higher Studies

✅ Industry Recognized Certifications

✅ Build Future Ready Skills
""")

c1, c2 = st.columns(2)

with c1:
    st.success("VBSPU Students → Jaunpur Local Chapter (8666)")

with c2:
    st.info("MGKVP Students → Varanasi Local Chapter (8664)")

st.divider()

st.sidebar.header("🔍 Search Courses")

search_text = st.sidebar.text_input("Search Topic / Course")

selected_key = st.sidebar.multiselect(
    "Category",
    sorted(df["Key"].dropna().astype(str).unique())
)

selected_duration = st.sidebar.multiselect(
    "Duration",
    sorted(df["Duration"].dropna().astype(str).unique())
)

selected_institute = st.sidebar.multiselect(
    "Institute",
    sorted(df["Institute"].dropna().astype(str).unique())
)

recommendation = st.sidebar.selectbox(
    "Recommended For",
    ["All", "BCA Students", "MCA Students", "Management Students", "Mathematics Students"]
)

filtered = df.copy()

if search_text:
    mask = pd.Series(False, index=filtered.index)
    for col in filtered.columns:
        mask |= filtered[col].astype(str).str.contains(search_text, case=False, na=False)
    filtered = filtered[mask]

if selected_key:
    filtered = filtered[filtered["Key"].astype(str).isin(selected_key)]

if selected_duration:
    filtered = filtered[filtered["Duration"].astype(str).isin(selected_duration)]

if selected_institute:
    filtered = filtered[filtered["Institute"].astype(str).isin(selected_institute)]

st.subheader(f"📚 Available Courses ({len(filtered)})")

for _, row in filtered.iterrows():
    st.markdown(f"### 🎓 {row['Course Name']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Institute:", row["Institute"])
        st.write("Discipline:", row["Discipline"])

    with col2:
        st.write("Duration:", row["Duration"])
        st.write("Start:", row["Start date"])

    with col3:
        st.write("Exam:", row["Exam date"])
        st.write("Enrollment Ends:", row["Enrollment End date"])

    url = row.get("Click here to Join the course")
    if pd.notna(url):
        st.link_button("🔗 Enroll Now", str(url))

    with st.expander("View Complete Details"):
        st.dataframe(
            pd.DataFrame({"Field": row.index, "Value": row.values}),
            use_container_width=True,
            hide_index=True
        )

    st.divider()
