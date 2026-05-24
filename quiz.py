import json
from llm import generate_text
from database import get_connection


# -----------------------------
# GET WEAKEST CONCEPT
# -----------------------------

def get_weakest_concept():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT concept_name, mastery_score
    FROM concept_mastery
    ORDER BY mastery_score ASC
    LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()

    return row


# -----------------------------
# GENERATE QUESTION
# -----------------------------

def generate_question(concept):

    prompt = f"""
Create ONE neuroscience retrieval question.

Concept: {concept}

Rules:
- conceptual
- requires reasoning
- no trivia
"""

    return generate_text(prompt)


# -----------------------------
# EVALUATE ANSWER
# -----------------------------

def evaluate_answer(question, answer):

    prompt = f"""
Evaluate neuroscience answer.

Return ONLY JSON:

{{
  "score": 0.0,
  "feedback": "string",
  "misconceptions": ["string"]
}}

Question:
{question}

Answer:
{answer}
"""

    raw = generate_text(prompt)

    try:
        return json.loads(raw.strip())
    except:
        return {
            "score": 0.0,
            "feedback": "Could not evaluate answer.",
            "misconceptions": []
        }