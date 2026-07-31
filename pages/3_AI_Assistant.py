"""
3_AI_Assistant.py

AI Assistant page for the DX Usage Intelligence Dashboard.

Provides a natural-language chat interface over the latest
dashboard snapshot, backed by assistant.answer_question(). Includes
a row of suggested-question shortcuts and a persistent chat history
for the current browser session.

NOTE: no functional bugs found on this page — the logic here is
sound. Comments below are purely explanatory / documentation.
"""

import streamlit as st
from assistant import answer_question
from theme import apply_theme
from dashboard_components import hero, chat_bubble

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
apply_theme()
hero("🤖 AI Dashboard Assitant", "Ask questions about datasets, users, providers and dashboard statistics.")

# -------------------------------------------------------------------
# Session state setup
#
# "messages" holds the full chat history for this browser session
# (Streamlit re-runs the whole script on every interaction, so this
# needs to live in st.session_state to persist across reruns).
#
# "pending_prompt" is used to pass a suggested-question click through
# to the same handling code path as a typed chat_input message, so
# there's only one place that actually calls answer_question().
# -------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# OPTIONAL (not applied, just noting): st.session_state.messages grows
# for the entire browser session with no cap. For a long-running demo
# session this is very unlikely to matter, but if it ever needs
# bounding, something like
#   st.session_state.messages = st.session_state.messages[-40:]
# right after appending would cap it to the most recent ~20 exchanges.

SUGGESTED_QUESTIONS = [
    ("📦", "How many datasets are available?"),
    ("👤", "How many users are registered?"),
    ("🏢", "Which provider has the most datasets?"),
    ("🌍", "Which domain has the most datasets?"),
    ("🔓", "How many open datasets are there?"),
    ("📂", "How many dataset types are available?"),
]

# -------------------------------------------------------------------
# Suggested-question buttons
#
# Clicking a button stores its question text in pending_prompt rather
# than answering it immediately inline — this lets the single block
# further down handle both "typed" and "clicked" questions identically.
# -------------------------------------------------------------------

st.subheader("💡 Suggested Questions")
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for i, (icon, question) in enumerate(SUGGESTED_QUESTIONS):
    with cols[i % 3]:
        if st.button(f"{icon}  {question}", key=f"suggested_{i}", use_container_width=True):
            st.session_state.pending_prompt = question

st.divider()
st.subheader("💬 Ask a Question")
st.caption("Ask anything about datasets, users, providers, domains or recent changes.")

# -------------------------------------------------------------------
# Render existing conversation history
# -------------------------------------------------------------------

st.subheader("🤖 Conversation")
for message in st.session_state.messages:
    chat_bubble(message["role"], message["content"])

# -------------------------------------------------------------------
# Handle new input — either typed via chat_input, or a suggested
# question that was clicked above.
# -------------------------------------------------------------------

typed_prompt = st.chat_input("💬 Ask about datasets, users, providers, domains...")

prompt = typed_prompt or st.session_state.pending_prompt
st.session_state.pending_prompt = None  # consume it so it doesn't re-fire on the next rerun

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    chat_bubble("user", prompt)

    with st.spinner("🤖 Thinking..."):
        answer = answer_question(prompt)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    chat_bubble("assistant", answer)

st.divider()
st.caption("Responses are generated from the latest dashboard snapshot.")
