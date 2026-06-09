```python
import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="NPTEL Course Helper",
    page_icon="🎓",
    layout="wide"
)

# ==========================================
# GOOGLE SHEET CSV
# ==========================================
CSV_URL = "https://docs.google.com/spreadsheets/d/1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"

# ==========================================
# LOAD DATA
# ==========================================
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Convert date columns if present
    date_columns = [
        "Start Date",
        "End Date",
        "Exam Date",
        "Enrollment End Date",
        "Exam Registration End Date"
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

df = load_data()

# ==========================================
# HEADER
# ==========================================
st.title("🎓 NPTEL Course Helper")
st.caption("Find the right NPTEL course quickly")

# ==========================================
# IMPORTANCE SECTION
# ==========================================
with st.container():

    st.markdown("""
    ## Why NPTEL & IIT Certificates Matter?

    ✅ Enhance Resume Value

    ✅ Recognized by Recruiters and Industry

    ✅ Learn Directly from IIT/IISc Faculty

    ✅ Useful for Placements, Internships and Higher Studies

    ✅ Add Certificates to LinkedIn

    ✅ Gain Industry-Oriented Skills Beyond University Curriculum

    ✅ Strong Advantage for Competitive Exams and Career Growth
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

# ==========================================
# SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🔍 Search Courses")

# Course Name Column Detection
course_col = None

possible_course_cols = [
    "Course Name",
    "Course",
    "Name",
    "Title"
]

for c in possible_course_cols:
    if c in df.columns:
        course_col = c
        break

# Discipline Column
discipline_col = None

for c in df.columns:
    if "discipline" in c.lower():
        discipline_col = c
        break

# Duration Column
duration_col = None

for c in df.columns:
    if "duration" in c.lower():
        duration_col = c
        break

# ==========================================
# SEARCH TOPIC
# ==========================================
keyword = st.sidebar.text_input(
    "Search Topic",
    placeholder="python, ai, finance, machine learning..."
)

# ==========================================
# DISCIPLINE FILTER
# ==========================================
if discipline_col:

    disciplines = sorted(
        df[discipline_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_discipline = st.sidebar.multiselect(
        "Discipline",
        disciplines
    )
else:
    selected_discipline = []

# ==========================================
# DURATION FILTER
# ==========================================
if duration_col:

    durations = sorted(
        df[duration_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_duration = st.sidebar.multiselect(
        "Duration",
        durations
    )
else:
    selected_duration = []

# ==========================================
# START DATE
# ==========================================
start_filter = st.sidebar.date_input(
    "Starts After",
    value=None
)

# ==========================================
# EXAM DATE
# ==========================================
exam_filter = st.sidebar.date_input(
    "Exam Before",
    value=None
)

# ==========================================
# RECOMMENDATION SECTION
# ==========================================
st.sidebar.divider()

st.sidebar.subheader("⭐ Quick Recommendations")

recommended_stream = st.sidebar.selectbox(
    "Recommended For",
    [
        "All",
        "BCA Students",
        "MCA Students",
        "Management Students",
        "Math Students"
    ]
)

# ==========================================
# FILTERING
# ==========================================
filtered_df = df.copy()

# Topic Search
if keyword:

    mask = pd.Series(False, index=filtered_df.index)

    for col in filtered_df.columns:
        try:
            mask = mask | filtered_df[col].astype(str).str.contains(
                keyword,
                case=False,
                na=False
            )
        except:
            pass

    filtered_df = filtered_df[mask]

# Discipline
if selected_discipline and discipline_col:
    filtered_df = filtered_df[
        filtered_df[discipline_col].isin(selected_discipline)
    ]

# Duration
if selected_duration and duration_col:
    filtered_df = filtered_df[
        filtered_df[duration_col].astype(str).isin(selected_duration)
    ]

# Start Date
if "Start Date" in filtered_df.columns:
    if start_filter:
        filtered_df = filtered_df[
            filtered_df["Start Date"] >= pd.to_datetime(start_filter)
        ]

# Exam Date
if "Exam Date" in filtered_df.columns:
    if exam_filter:
        filtered_df = filtered_df[
            filtered_df["Exam Date"] <= pd.to_datetime(exam_filter)
        ]

# ==========================================
# RECOMMENDATION ENGINE
# ==========================================
if recommended_stream != "All":

    recommendation_keywords = {
        "BCA Students": [
            "python",
            "java",
            "web",
            "database",
            "dbms",
            "cloud",
            "cyber",
            "data structure",
            "programming",
            "ai",
            "machine learning"
        ],

        "MCA Students": [
            "machine learning",
            "ai",
            "cloud",
            "data science",
            "deep learning",
            "cyber security",
            "software engineering",
            "analytics"
        ],

        "Management Students": [
            "management",
            "finance",
            "marketing",
            "hr",
            "entrepreneurship",
            "business"
        ],

        "Math Students": [
            "mathematics",
            "statistics",
            "probability",
            "calculus",
            "linear algebra"
        ]
    }

    keywords = recommendation_keywords[recommended_stream]

    mask = pd.Series(False, index=filtered_df.index)

    for col in filtered_df.columns:
        try:
            for k in keywords:
                mask = mask | filtered_df[col].astype(str).str.contains(
                    k,
                    case=False,
                    na=False
                )
        except:
            pass

    filtered_df = filtered_df[mask]

# ==========================================
# DASHBOARD
# ==========================================
st.subheader("📊 Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Courses Found",
    len(filtered_df)
)

if "Start Date" in filtered_df.columns:
    upcoming = (
        filtered_df["Start Date"] >= pd.Timestamp.today()
    ).sum()

    col2.metric(
        "Upcoming Starts",
        upcoming
    )

if "Exam Date" in filtered_df.columns:
    exams = (
        filtered_df["Exam Date"] >= pd.Timestamp.today()
    ).sum()

    col3.metric(
        "Upcoming Exams",
        exams
    )

col4.metric(
    "Columns Available",
    len(df.columns)
)

st.divider()

# ==========================================
# RESULTS
# ==========================================
st.subheader("📚 Course Results")

if len(filtered_df) == 0:
    st.warning("No matching courses found.")
    st.stop()

# ==========================================
# COURSE CARDS
# ==========================================
for idx, row in filtered_df.iterrows():

    title = row.get(course_col, "Course")

    with st.container():

        st.markdown(f"## 🎓 {title}")

        c1, c2, c3 = st.columns(3)

        with c1:

            if discipline_col:
                st.write(
                    f"**Discipline:** {row.get(discipline_col,'')}"
                )

            if duration_col:
                st.write(
                    f"**Duration:** {row.get(duration_col,'')}"
                )

        with c2:

            if "Start Date" in df.columns:
                st.write(
                    f"**Start Date:** {row.get('Start Date')}"
                )

            if "End Date" in df.columns:
                st.write(
                    f"**End Date:** {row.get('End Date')}"
                )

        with c3:

            if "Exam Date" in df.columns:
                st.write(
                    f"**Exam Date:** {row.get('Exam Date')}"
                )

            if "Enrollment End Date" in df.columns:
                st.write(
                    f"**Enroll Till:** {row.get('Enrollment End Date')}"
                )

        # Enrollment Link
        url_column = None

        for c in df.columns:
            if "url" in c.lower() or "link" in c.lower():
                url_column = c
                break

        if url_column and pd.notna(row[url_column]):

            st.link_button(
                "🔗 Enroll Now",
                str(row[url_column])
            )

        with st.expander("📄 View Complete Course Details"):

            details = pd.DataFrame(
                {
                    "Field": row.index,
                    "Value": row.values
                }
            )

            st.dataframe(
                details,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

# ==========================================
# DOWNLOAD FILTERED DATA
# ==========================================
csv = filtered_df.to_csv(index=False)

st.download_button(
    "⬇ Download Filtered Courses",
    csv,
    file_name="filtered_nptel_courses.csv",
    mime="text/csv"
)
```
