import httpx
import streamlit as st

st.set_page_config(page_title="ALPHAR", page_icon="🔧", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #0b1020; }
    .block-container { max-width: 1180px; padding-top: 2rem; }
    .hero { padding: 1rem 0 1.5rem; }
    .hero h1 { color: #8be9fd; margin-bottom: 0.2rem; }
    .hero p { color: #a7b0c0; font-size: 1.1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero"><h1>⚡ ALPHAR</h1>'
    "<p>Autonomous Software Engineering Agent · Understand. Fix. Test. Verify.</p>"
    "</div>",
    unsafe_allow_html=True,
)

repository, task = st.columns(2)
with repository:
    st.subheader("Repository")
    st.code("demo_repo", language="text")
with task:
    st.subheader("Task")
    st.code("Find and fix the bug in this repository.", language="text")

if st.button("🚀 RUN ALPHAR", type="primary", use_container_width=True):
    st.session_state.pop("result", None)
    with st.spinner("Running the real analysis and verification loop..."):
        try:
            response = httpx.post("http://127.0.0.1:8000/run", timeout=60)
            response.raise_for_status()
            st.session_state["result"] = response.json()
        except httpx.HTTPError as exc:
            st.error(f"❌ ALPHAR encountered an error: {exc}")

result = st.session_state.get("result")
if result:
    st.subheader("Agent activity")
    stages = "  ↓  ".join(item["agent"] for item in result["activity"])
    st.caption(stages)
    for item in result["activity"]:
        st.success(f"✓ {item['agent']} — {item['message']}")

    issue = result["plan"]["issue"]
    st.subheader("Bug detected")
    left, right = st.columns(2)
    with left:
        st.write(f"**Severity:** {issue['severity']}")
        st.write(f"**File:** `{issue['file']}:{issue['line']}`")
        st.write(f"**Function:** `{issue['function']}()`")
        st.write(f"**Issue:** {issue['title']}")
        st.write(issue["explanation"])
        st.subheader("Root cause")
        st.write(result["plan"]["root_cause"])
    with right:
        st.subheader("AI analysis")
        st.write(f"Source: `{result['plan']['source']}`")
        if result["plan"]["ai_error"]:
            st.warning(result["plan"]["ai_error"])
        st.subheader("Generated fix")
        st.write(result["plan"]["proposed_fix"])
        st.subheader("Tests")
        st.code(f"Before:\n{result['tests_before']['output']}\n\nAfter:\n{result['tests_after']['output']}")

    st.subheader("Actual code diff")
    st.code(result["patch"]["diff"], language="diff")
    st.success(result["status"])

st.divider()
st.subheader("Team")
st.caption("VITV_ALPHAR_1 · VIT Vellore · Samsung PRISM | Gen AI Hackathon 2026")
st.table(
    [
        {"Member": "Lakshya Singh", "Registration No.": "24BDS0054", "Role": "Team Lead / AI & Backend"},
        {"Member": "Hardik Vikas Jain", "Registration No.": "24BCI0294", "Role": "AI / Backend"},
        {"Member": "Rupanshu", "Registration No.": "24BCI0308", "Role": "Frontend / Integration"},
        {"Member": "Apoorv Sharma", "Registration No.": "24BCT0243", "Role": "Testing / Engineering"},
    ]
)
