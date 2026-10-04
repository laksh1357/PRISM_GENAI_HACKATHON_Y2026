import streamlit as st
import httpx

st.set_page_config(page_title="ALPHAR", page_icon="🔧", layout="wide")

st.markdown(
    "<style>body { background: #0e1117; } .block-container { max-width: 1200px; }</style>",
    unsafe_allow_html=True,
)
st.title("ALPHAR")
st.caption("Autonomous Software Engineering Agent")

st.subheader("Repository task")
st.code("demo_repo", language="text")
st.write("Find and fix the calculator average bug.")

if st.button("Run ALPHAR", type="primary"):
    with st.spinner("Running the real analysis and verification loop..."):
        try:
            response = httpx.post("http://127.0.0.1:8000/run", timeout=60)
            response.raise_for_status()
            st.session_state["result"] = response.json()
        except httpx.HTTPError as exc:
            st.error(f"Backend error: {exc}")

result = st.session_state.get("result")
if result:
    st.subheader("Agent activity")
    for step in result["activity"]:
        st.success(f"✓ {step}")

    issue = result["plan"]["issue"]
    left, right = st.columns(2)
    with left:
        st.subheader("Detected issue")
        st.write(f"**{issue['title']}** in `{issue['file']}:{issue['line']}`")
        st.write(issue["explanation"])
        st.subheader("Root cause")
        st.write(result["plan"]["root_cause"])
    with right:
        st.subheader("Generated fix")
        st.write(result["plan"]["proposed_fix"])
        st.subheader("Tests")
        st.code(f"Before:\n{result['tests_before']['output']}\n\nAfter:\n{result['tests_after']['output']}")

    st.subheader("Actual code diff")
    st.code(result["patch"]["diff"], language="diff")
    st.success(result["status"])
