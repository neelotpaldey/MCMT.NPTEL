import streamlit as st
import pandas as pd

st.set_page_config(
page_title="NPTEL Course Helper",
page_icon="🎓",
layout="wide"
)

CSV_URL = "https://docs.google.com/spreadsheets/d/1QjQPP0R2yFsajCjnTT3-QmUqdqLHHWnJkesXPMAE8QY/export?format=csv"

@st.cache_data(ttl=3600)
def load_data():
df = pd.read_csv(CSV_URL)

```
# Remove blank columns
df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
df = df.drop(columns=[c for c in df.columns if str(c).strip() in ["", ".", ".1", ".2", ".3"]], errors="ignore")

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
```

df = load_data()

st.title("🎓 NPTEL Course Helper")

st.markdown("""

### Why NPTEL & IIT Certificates Matter

✅ Improve Resume Quality

✅ Recognized by Industry & Recruiters

✅ Learn from IIT / IISc Faculty

✅ Helpful for Placements & Internships

✅ Add to LinkedIn Profile

✅ Build Industry-Relevant Skills
""")

col1, col2 = st.columns(2)

with col1:
st.success("VBSPU Students → Jaunpur Local Chapter (8666)")

with col2:
st.info("MGKVP Students → Varanasi Local Chapter (8664)")

st.divider()

# SIDEBAR

st.sidebar.header("🔍 Search Courses")

topic = st.sidebar.text_input(
"Search Topic",
placeholder="Python, AI, Finance, Java..."
)

selected_keys = st.sidebar.multiselect(
"Category",
options=sorted(df["Key"].dropna().unique())
)

selected_duration = st.sidebar.multiselect(
"Duration",
options=sorted(df["Duration"].dropna().unique())
)

selected_institute = st.sidebar.multiselect(
"Institute",
options=sorted(df["Institute"].dropna().unique())
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

filtered = df.copy()

# Topic Search

if topic:
mask = pd.Series(False, index=filtered.index)

```
for col in filtered.columns:
    mask |= filtered[col].astype(str).str.contains(
        topic,
        case=False,
        na=False
    )

filtered = filtered[mask]
```

# Key Filter

if selected_keys:
filtered = filtered[
filtered["Key"].isin(selected_keys)
]

# Duration Filter

if selected_duration:
filtered = filtered[
filtered["Duration"].isin(selected_duration)
]

# Institute Filter

if selected_institute:
filtered = filtered[
filtered["Institute"].isin(selected_institute)
]

# Start Date

if start_after:
filtered = filtered[
filtered["Start date"] >= pd.to_datetime(start_after)
]

# Exam Date

if exam_before:
filtered = filtered[
filtered["Exam date"] <= pd.to_datetime(exam_before)
]

# Recommendation Engine

if recommendation != "All":

```
keywords = {
    "BCA Students": [
        "python","java","dbms","database",
        "web","cloud","cyber","programming",
        "ai","machine learning"
    ],

    "MCA Students": [
        "ai","machine learning",
        "deep learning","cloud",
        "cyber security","data science"
    ],

    "Management Students": [
        "management","marketing",
        "finance","business",
        "entrepreneurship","hr"
    ],

    "Mathematics Students": [
        "mathematics","statistics",
        "probability","calculus",
        "algebra"
    ]
}

mask = pd.Series(False, index=filtered.index)

for word in keywords[recommendation]:
    mask |= filtered["Course Name"].astype(str).str.contains(
        word,
        case=False,
        na=False
    )

filtered = filtered[mask]
```

# DASHBOARD

st.subheader("📊 Dashboard")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Courses Found", len(filtered))

c2.metric(
"Institutes",
filtered["Institute"].nunique()
)

c3.metric(
"Disciplines",
filtered["Discipline"].nunique()
)

c4.metric(
"Categories",
filtered["Key"].nunique()
)

st.divider()

# QUICK BUTTONS

st.subheader("🚀 Quick Filters")

q1, q2, q3 = st.columns(3)

with q1:
if st.button("💻 Computer Science"):
filtered = filtered[
filtered["Key"].astype(str).str.contains(
"CS",
case=False,
na=False
)
]

with q2:
if st.button("📈 Management"):
filtered = filtered[
filtered["Key"].astype(str).str.contains(
"MGMT",
case=False,
na=False
)
]

with q3:
if st.button("➗ Mathematics"):
filtered = filtered[
filtered["Key"].astype(str).str.contains(
"Math",
case=False,
na=False
)
]

st.divider()

st.subheader(f"📚 Available Courses ({len(filtered)})")

if filtered.empty:
st.warning("No courses found.")
st.stop()

for _, row in filtered.iterrows():

```
with st.container():

    st.markdown(f"## 🎓 {row['Course Name']}")

    a, b, c = st.columns(3)

    with a:
        st.write("**Institute:**", row["Institute"])
        st.write("**Category:**", row["Key"])
        st.write("**Duration:**", row["Duration"])

    with b:
        st.write("**Start Date:**", row["Start date"].date())
        st.write("**End Date:**", row["End date"].date())

    with c:
        st.write("**Exam Date:**", row["Exam date"].date())
        st.write("**Enroll Till:**", row["Enrollment End date"].date())

    st.link_button(
        "🔗 Enroll Now",
        row["Click here to Join the course"]
    )

    with st.expander("📄 Full Details"):

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
```

csv = filtered.to_csv(index=False)

st.download_button(
"⬇ Download Filtered Courses",
csv,
file_name="nptel_courses.csv",
mime="text/csv"
)
