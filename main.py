import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="NPTEL Course Helper",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# DATA SOURCE
# =====================================================
GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"
)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data(ttl=3600)
def load_data():

    csv_file = Path(__file__).parent / "NPTEL.csv"

    try:
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            source = "📁 Repository CSV (NPTEL.csv)"
        else:
            df = pd.read_csv(GOOGLE_SHEET_URL)
            source = "🌐 Google Sheet"

    except Exception:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        source = "🌐 Google Sheet (Fallback)"

    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]

    date_columns = [
        "Start date",
        "End date",
        "Exam date",
        "Enrollment End date",
        "Exam Registration End date"
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df, source


df, source = load_data()

# =====================================================
# HEADER
# =====================================================
st.title("🎓 NPTEL Course Helper")

st.sidebar.success(source)

st.markdown("""
### Why NPTEL & IIT Certificates Matter?

✅ Learn directly from IIT & IISc faculty

✅ Improve resume and LinkedIn profile

✅ Useful for internships and placements

✅ Industry-recognized certifications

✅ Build advanced technical and management skills

✅ Valuable for higher studies and career growth
""")

col1, col2 = st.columns(2)

with col1:
    st.success(
        """
        VBSPU Students

        Local Chapter: Jaunpur

        Code: 8666
        """
    )

with col2:
    st.info(
        """
        MGKVP Students

        Local Chapter: Varanasi

        Code: 8664
        """
    )

st.divider()

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("🔍 Search Courses")

search_text = st.sidebar.text_input(
    "Search Topic / Course",
    placeholder="Python, AI, Java, Finance..."
)

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

start_after = st.sidebar.date_input(
    "Starts After",
    value=None
)

exam_before = st.sidebar.date_input(
    "Exam Before",
    value=None
)

st.sidebar.divider()

recommendation = st.sidebar.selectbox(
    "⭐ Recommended For",
    [
        "All",
        "BCA Students",
        "MCA Students",
        "Management Students",
        "Mathematics Students"
    ]
)

# =====================================================
# FILTERING
# =====================================================
filtered = df.copy()

if search_text:

    mask = pd.Series(False, index=filtered.index)

    for col in filtered.columns:
        mask |= filtered[col].astype(str).str.contains(
            search_text,
            case=False,
            na=False
        )

    filtered = filtered[mask]

if selected_key:
    filtered = filtered[
        filtered["Key"].astype(str).isin(selected_key)
    ]

if selected_duration:
    filtered = filtered[
        filtered["Duration"].astype(str).isin(selected_duration)
    ]

if selected_institute:
    filtered = filtered[
        filtered["Institute"].astype(str).isin(selected_institute)
    ]

if start_after and "Start date" in filtered.columns:
    filtered = filtered[
        filtered["Start date"] >= pd.to_datetime(start_after)
    ]

if exam_before and "Exam date" in filtered.columns:
    filtered = filtered[
        filtered["Exam date"] <= pd.to_datetime(exam_before)
    ]

# =====================================================
# RECOMMENDATION ENGINE
# =====================================================
recommendations = {
    "BCA Students": [
        "python", "java", "programming", "web",
        "database", "dbms", "cloud",
        "cyber", "ai", "machine learning"
    ],
    "MCA Students": [
        "ai", "machine learning", "deep learning",
        "data science", "cloud", "cyber security"
    ],
    "Management Students": [
        "management", "finance", "marketing",
        "business", "entrepreneurship", "hr"
    ],
    "Mathematics Students": [
        "mathematics", "statistics",
        "probability", "algebra", "calculus"
    ]
}

if recommendation != "All":

    keywords = recommendations.get(recommendation, [])

    mask = pd.Series(False, index=filtered.index)

    for word in keywords:
        mask |= filtered["Course Name"].astype(str).str.contains(
            word,
            case=False,
            na=False
        )

    filtered = filtered[mask]

# =====================================================
# DASHBOARD
# =====================================================
st.subheader("📊 Dashboard")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Courses Found", len(filtered))
m2.metric("Institutes", filtered["Institute"].nunique())
m3.metric("Disciplines", filtered["Discipline"].nunique())
m4.metric("Categories", filtered["Key"].nunique())

st.divider()

# =====================================================
# QUICK FILTERS
# =====================================================
st.subheader("🚀 Quick Filters")

q1, q2, q3 = st.columns(3)

if q1.button("💻 Computer Science"):
    filtered = filtered[
        filtered["Key"].astype(str).str.contains(
            "CS",
            case=False,
            na=False
        )
    ]

if q2.button("📈 Management"):
    filtered = filtered[
        filtered["Key"].astype(str).str.contains(
            "MGMT",
            case=False,
            na=False
        )
    ]

if q3.button("➗ Mathematics"):
    filtered = filtered[
        filtered["Key"].astype(str).str.contains(
            "MATH",
            case=False,
            na=False
        )
    ]

st.divider()

# =====================================================
# RESULTS
# =====================================================
st.subheader(f"📚 Available Courses ({len(filtered)})")

if filtered.empty:
    st.warning("No matching courses found.")
    st.stop()

for _, row in filtered.iterrows():

    st.markdown(f"## 🎓 {row['Course Name']}")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("**Institute:**", row["Institute"])
        st.write("**Discipline:**", row["Discipline"])
        st.write("**Category:**", row["Key"])

    with c2:
        st.write("**Duration:**", row["Duration"])

        if pd.notna(row["Start date"]):
            st.write("**Start Date:**", row["Start date"].strftime("%d-%b-%Y"))

        if pd.notna(row["End date"]):
            st.write("**End Date:**", row["End date"].strftime("%d-%b-%Y"))

    with c3:

        if pd.notna(row["Exam date"]):
            st.write("**Exam Date:**", row["Exam date"].strftime("%d-%b-%Y"))

        if pd.notna(row["Enrollment End date"]):
            st.write(
                "**Enrollment Ends:**",
                row["Enrollment End date"].strftime("%d-%b-%Y")
            )

    course_url = row.get("Click here to Join the course")

    if pd.notna(course_url):
        st.link_button(
            "🔗 Enroll Now",
            str(course_url)
        )

    with st.expander("📄 View Complete Details"):

        details = pd.DataFrame({
            "Field": row.index,
            "Value": row.values
        })

        st.dataframe(
            details,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

# =====================================================
# DOWNLOAD
# =====================================================
csv_export = filtered.to_csv(index=False)

st.download_button(
    "⬇ Download Filtered Courses",
    csv_export,
    file_name="nptel_courses.csv",
    mime="text/csv"
)
