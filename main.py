import streamlit as st
import pandas as pd

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="NPTEL Course Helper",
    page_icon="🎓",
    layout="wide"
)

# ==========================
# DATA SOURCE
# ==========================
CSV_URL = "https://docs.google.com/spreadsheets/d/1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"


@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Convert dates
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

# ==========================
# HEADER
# ==========================
st.title("🎓 NPTEL Course Helper")

st.markdown("""
### Why NPTEL & IIT Certificates Matter?

✅ Enhance Resume Value

✅ Learn from IIT & IISc Professors

✅ Useful for Placements & Internships

✅ Industry Recognized Certifications

✅ Boost LinkedIn & Resume Profile

✅ Gain Future Ready Skills
""")

col1, col2 = st.columns(2)

with col1:
    st.success("VBSPU Students → Select Jaunpur Local Chapter (8666)")

with col2:
    st.info("MGKVP Students → Select Varanasi Local Chapter (8664)")

st.divider()

# ==========================
# SIDEBAR
# ==========================
st.sidebar.header("🔍 Search Courses")

search_text = st.sidebar.text_input(
    "Search Topic / Course",
    placeholder="Python, AI, Java, Finance..."
)

selected_key = st.sidebar.multiselect(
    "Category",
    sorted(df["Key"].dropna().unique())
)

selected_duration = st.sidebar.multiselect(
    "Duration",
    sorted(df["Duration"].dropna().unique())
)

selected_institute = st.sidebar.multiselect(
    "Institute",
    sorted(df["Institute"].dropna().unique())
)

start_after = st.sidebar.date_input(
    "Starts After",
    value=None
)

exam_before = st.sidebar.date_input(
    "Exam Before",
    value=None
)

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

# ==========================
# FILTER DATA
# ==========================
filtered = df.copy()

# Text Search
if search_text:

    mask = pd.Series(False, index=filtered.index)

    for col in filtered.columns:
        mask = mask | filtered[col].astype(str).str.contains(
            search_text,
            case=False,
            na=False
        )

    filtered = filtered[mask]

# Category
if selected_key:
    filtered = filtered[
        filtered["Key"].isin(selected_key)
    ]

# Duration
if selected_duration:
    filtered = filtered[
        filtered["Duration"].isin(selected_duration)
    ]

# Institute
if selected_institute:
    filtered = filtered[
        filtered["Institute"].isin(selected_institute)
    ]

# Start Date
if start_after and "Start date" in filtered.columns:
    filtered = filtered[
        filtered["Start date"] >= pd.to_datetime(start_after)
    ]

# Exam Date
if exam_before and "Exam date" in filtered.columns:
    filtered = filtered[
        filtered["Exam date"] <= pd.to_datetime(exam_before)
    ]

# ==========================
# RECOMMENDATION ENGINE
# ==========================
recommendations = {
    "BCA Students": [
        "python",
        "java",
        "programming",
        "web",
        "database",
        "dbms",
        "cloud",
        "cyber",
        "machine learning",
        "ai"
    ],
    "MCA Students": [
        "ai",
        "machine learning",
        "deep learning",
        "data science",
        "cloud",
        "cyber security"
    ],
    "Management Students": [
        "management",
        "finance",
        "marketing",
        "business",
        "entrepreneurship",
        "hr"
    ],
    "Mathematics Students": [
        "mathematics",
        "statistics",
        "probability",
        "algebra",
        "calculus"
    ]
}

if recommendation != "All":

    words = recommendations.get(recommendation, [])

    mask = pd.Series(False, index=filtered.index)

    for word in words:
        mask = mask | filtered["Course Name"].astype(str).str.contains(
            word,
            case=False,
            na=False
        )

    filtered = filtered[mask]

# ==========================
# DASHBOARD
# ==========================
st.subheader("📊 Dashboard")

d1, d2, d3, d4 = st.columns(4)

d1.metric("Courses Found", len(filtered))
d2.metric("Institutes", filtered["Institute"].nunique())
d3.metric("Disciplines", filtered["Discipline"].nunique())
d4.metric("Categories", filtered["Key"].nunique())

st.divider()

# ==========================
# QUICK FILTERS
# ==========================
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

# ==========================
# RESULTS
# ==========================
st.subheader(f"📚 Courses Found: {len(filtered)}")

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
        st.write("**Start Date:**", row["Start date"])
        st.write("**End Date:**", row["End date"])

    with c3:
        st.write("**Exam Date:**", row["Exam date"])
        st.write("**Enrollment Ends:**", row["Enrollment End date"])
        st.write(
            "**Exam Registration Ends:**",
            row["Exam Registration End date"]
        )

    course_url = row.get("Click here to Join the course")

    if pd.notna(course_url):
        st.link_button(
            "🔗 Enroll Now",
            str(course_url)
        )

    with st.expander("📄 View Full Course Details"):

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

# ==========================
# DOWNLOAD
# ==========================
csv_data = filtered.to_csv(index=False)

st.download_button(
    label="⬇ Download Filtered Courses",
    data=csv_data,
    file_name="nptel_courses.csv",
    mime="text/csv"
)
