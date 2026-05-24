import streamlit as st
import os
from dotenv import load_dotenv

from database import init_db
from llm import generate_text

from memory import (
    extract_concepts,
    save_concepts,
    get_learning_context,
    update_mastery
)

from quiz import (
    get_weakest_concept,
    generate_question,
    evaluate_answer
)


# -----------------------------
# INIT
# -----------------------------

load_dotenv()
init_db()

st.title("🧠 Neuroscience Tutor")


# -----------------------------
# SESSION STATE
# -----------------------------

if "current_q" not in st.session_state:
    st.session_state.current_q = None

if "current_c" not in st.session_state:
    st.session_state.current_c = None


# -----------------------------
# SIDEBAR QUIZ
# -----------------------------

with st.sidebar:

    st.header("Quiz Mode")

    if st.button("Quiz Me"):

        weak = get_weakest_concept()

        if weak:
            concept, _ = weak

            q = generate_question(concept)

            st.session_state.current_q = q
            st.session_state.current_c = concept

        else:
            st.warning("No data yet.")


# -----------------------------
# QUIZ UI
# -----------------------------

if st.session_state.current_q:

    st.subheader("Quiz Question")
    st.write(st.session_state.current_q)

    ans = st.text_input("Your answer")

    if st.button("Submit"):

        result = evaluate_answer(
            st.session_state.current_q,
            ans
        )

        st.write(result["feedback"])

        for m in result.get("misconceptions", []):
            st.write("•", m)

        update_mastery(
            st.session_state.current_c,
            result["score"]
        )

        st.success("Updated mastery!")

        st.session_state.current_q = None
        st.session_state.current_c = None


# -----------------------------
# CHAT INPUT
# -----------------------------

user_input = st.chat_input("Ask neuroscience...")

if user_input:

    st.chat_message("user").write(user_input)

    context = get_learning_context()

    prompt = f"""
You are a neuroscience tutor.

Use this learner profile:

{context}

User question:
{user_input}
"""

    response = generate_text(prompt)

    st.chat_message("assistant").write(response)

    data = extract_concepts(user_input, response)
    save_concepts(data["concepts"])