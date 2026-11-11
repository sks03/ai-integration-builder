import os, re, requests, streamlit as st
from generator import generate_connector
from reviewer import review_connector
from safeguards import static_checks
from runner import run_dry

DEFAULT_PAGES = "\n".join([
    "https://developer.calendly.com/api-docs/calendly-api/organizations/list-organization-memberships.md",
    "https://developer.calendly.com/api-docs/calendly-api/scheduled-events/list-scheduled-events.md",
])

st.set_page_config(page_title="Integration Builder", layout="wide")
st.title("Integration Builder")
st.caption("Environment: SANDBOX | Read-only")

urls = st.text_area("API docs URLs (one per line; Markdown .md pages work best)", DEFAULT_PAGES, height=120)
pasted = st.text_area("Optional: paste API doc text here (used instead of the URLs if filled)", height=150)

def clean(text, url):
    if url.endswith(".md"):
        return text.split("**SDK Code**")[0]
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)

def get_docs():
    if pasted.strip():
        return pasted.strip()[:60000]
    parts = []
    for u in [x.strip() for x in urls.splitlines() if x.strip()]:
        try:
            r = requests.get(u, timeout=30)
            r.raise_for_status()
            parts.append(f"=== SOURCE: {u} ===\n" + clean(r.text, u))
        except Exception as e:
            st.warning(f"Could not fetch {u}: {e}")
    return "\n\n".join(parts)[:60000]

if st.button("1. Generate connector"):
    with st.spinner("Fetching docs and generating..."):
        docs = get_docs()
        if not docs.strip():
            st.error("No documentation could be fetched. Check the URLs or paste the docs text.")
            st.stop()
        out = generate_connector(docs)
        blocks = re.findall(r"```python\n(.*?)```", out, re.S)
        code = max(blocks, key=len) if blocks else out
        os.makedirs("generated", exist_ok=True)
        with open("generated/connector.py", "w", encoding="utf-8") as f:
            f.write(code)
        st.session_state.update(docs=docs, full=out, code=code, review=None, static=None)

if "code" in st.session_state:
    st.caption(f"Docs sent to the model: {len(st.session_state['docs'])} characters")
    st.subheader("Generated output")
    st.markdown(st.session_state["full"])

    if st.button("2. Run safety review (reads generated/connector.py)"):
        with open("generated/connector.py", encoding="utf-8") as f:
            st.session_state["code"] = f.read()
        st.session_state["static"] = static_checks(st.session_state["code"])
        st.session_state["review"] = review_connector(st.session_state["docs"], st.session_state["code"])

    s, r = st.session_state.get("static"), st.session_state.get("review")
    if s and r:
        c1, c2 = st.columns(2)
        c1.metric("Static checks", "PASS" if s["passed"] else "FAIL")
        c2.metric("AI review", r.get("verdict", "FAIL"))
        st.json({"static": s, "ai_review": r})
        ok = s["passed"] and r.get("verdict") == "PASS"
        if not ok:
            st.error("Blocked: fix the issues above before running.")
        if st.button("3. Run in sandbox (dry run)", disabled=not ok):
            st.code(run_dry("generated/connector.py"))