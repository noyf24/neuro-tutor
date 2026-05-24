import json
from database import get_connection
from llm import generate_text


# -----------------------------
# CLEAN JSON HELPER
# -----------------------------

def clean_json(text: str) -> str:
    text = text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()


# -----------------------------
# EXTRACT CONCEPTS
# -----------------------------

def extract_concepts(user_message, assistant_response):

    prompt = f"""
Extract neuroscience concepts.

Return ONLY valid JSON:

{{
  "concepts": [
    {{
      "name": "string",
      "understanding": 0.0,
      "notes": "string"
    }}
  ]
}}

User:
{user_message}

Assistant:
{assistant_response}
"""

    raw = generate_text(prompt)
    raw = clean_json(raw)

    try:
        return json.loads(raw)
    except:
        return {"concepts": []}


# -----------------------------
# SAVE / UPDATE CONCEPTS
# -----------------------------

def save_concepts(concepts):

    conn = get_connection()
    cur = conn.cursor()

    for c in concepts:

        cur.execute("""
        SELECT id, mastery_score
        FROM concept_mastery
        WHERE concept_name = ?
        """, (c["name"],))

        row = cur.fetchone()

        if row:

            cid, old = row

            new_score = old * 0.7 + c["understanding"] * 0.3

            cur.execute("""
            UPDATE concept_mastery
            SET mastery_score = ?,
                notes = ?,
                last_reviewed = datetime('now')
            WHERE id = ?
            """, (new_score, c["notes"], cid))

        else:

            cur.execute("""
            INSERT INTO concept_mastery
            (concept_name, mastery_score, last_reviewed, times_quizzed, times_correct, notes)
            VALUES (?, ?, datetime('now'), 0, 0, ?)
            """, (c["name"], c["understanding"], c["notes"]))

    conn.commit()
    conn.close()


# -----------------------------
# UPDATE MASTERY AFTER QUIZ
# -----------------------------

def update_mastery(concept_name, score):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT mastery_score, times_quizzed, times_correct
    FROM concept_mastery
    WHERE concept_name = ?
    """, (concept_name,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return

    old, tq, tc = row

    new_score = old * 0.8 + score * 0.2
    correct = 1 if score > 0.7 else 0

    cur.execute("""
    UPDATE concept_mastery
    SET mastery_score = ?,
        times_quizzed = ?,
        times_correct = ?,
        last_reviewed = datetime('now')
    WHERE concept_name = ?
    """, (new_score, tq + 1, tc + correct, concept_name))

    conn.commit()
    conn.close()


# -----------------------------
# LEARNING CONTEXT
# -----------------------------

def get_learning_context():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT concept_name, mastery_score, notes
    FROM concept_mastery
    ORDER BY mastery_score ASC
    LIMIT 5
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No learning history yet."

    text = "USER LEARNING PROFILE:\n\n"

    for r in rows:
        text += f"""
Concept: {r[0]}
Mastery: {round(r[1], 2)}
Notes: {r[2]}
"""

    return text