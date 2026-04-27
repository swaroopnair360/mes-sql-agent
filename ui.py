import streamlit as st
import requests
import json

# Page config
st.set_page_config(page_title="MES SQL Generator", layout="centered")

# ---------- Feedback Save Function ----------
def save_feedback(question, sql, feedback):
    data = {
        "question": question,
        "sql": sql,
        "feedback": feedback
    }

    with open("feedback.json", "a") as f:
        f.write(json.dumps(data) + "\n")

# ---------- Session State ----------
if "sql_part" not in st.session_state:
    st.session_state.sql_part = ""
if "explanation_part" not in st.session_state:
    st.session_state.explanation_part = ""
if "question" not in st.session_state:
    st.session_state.question = ""

# ---------- Header ----------
st.markdown("""
# 🧠 MES SQL Generator
Ask your question and get SQL instantly
""")

st.divider()

# ---------- Input ----------
question = st.text_input(
    "💬 Enter your question",
    placeholder="e.g. Show WIP for last 24 hours"
)

# ---------- Generate Button ----------
if st.button("⚡ Generate SQL", use_container_width=True):
    if question:
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    "http://127.0.0.1:8000/generate-sql",
                    json={"question": question}
                )

                output = res.text.encode().decode("unicode_escape")

                # Clean markdown
                output = output.replace("```sql", "").replace("```", "").strip()

                # Split SQL & Explanation
                if "Explanation:" in output:
                    parts = output.split("Explanation:")
                    sql_part = parts[0].replace("SQL:", "").strip()
                    explanation_part = parts[1].strip()
                else:
                    sql_part = output
                    explanation_part = ""

                # Save to session (IMPORTANT)
                st.session_state.sql_part = sql_part
                st.session_state.explanation_part = explanation_part
                st.session_state.question = question

            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please enter a question")

# ---------- Display Output ----------
if st.session_state.sql_part:

    st.divider()

    st.markdown("### 📄 Generated SQL")
    st.code(st.session_state.sql_part, language="sql")

    if st.session_state.explanation_part:
        st.markdown("### 💡 Explanation")
        st.info(st.session_state.explanation_part)

    # ---------- Feedback Section ----------
    st.divider()
    st.markdown("### 👍 Was this helpful?")

    col1, col2 = st.columns(2)

    if col1.button("👍 Good"):
        save_feedback(
            st.session_state.question,
            st.session_state.sql_part,
            "good"
        )
        st.success("Feedback saved!")

    if col2.button("👎 Bad"):
        save_feedback(
            st.session_state.question,
            st.session_state.sql_part,
            "bad"
        )
        st.warning("Feedback saved!")

# ---------- Footer ----------
st.divider()
st.caption("Built with ❤️ for MES automation")