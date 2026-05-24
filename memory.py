import json
import os

import google.generativeai as genai

from dotenv import load_dotenv

from database import get_connection


# -----------------------------
# GEMINI SETUP
# -----------------------------

load_dotenv()

genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)


# -----------------------------
# HELPERS
# -----------------------------

def clean_json_response(text):

    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return text.strip()


# -----------------------------
# CONCEPT EXTRACTION
# -----------------------------

def extract_concepts(user_message, assistant_response):

    prompt = f"""
    Extract neuroscience concepts discussed.

    Return ONLY valid JSON.

    Format:

    {{
      "concepts": [
        {{
          "name": "...",
          "understanding": 0.0,
          "notes": "..."
        }}
      ]
    }}

    USER MESSAGE:
    {user_message}

    ASSISTANT RESPONSE:
    {assistant_response}
    """

    response = model.generate_content(prompt)

    raw_output = clean_json_response(
        response.text
    )

    try:

        parsed = json.loads(raw_output)

        return parsed

    except Exception as e:

        print("JSON parse error:", e)

        return {
            "concepts": []
        }


# -----------------------------
# SAVE CONCEPTS
# -----------------------------

def save_concepts(concepts):

    conn = get_connection()
    cursor = conn.cursor()

    for concept in concepts:

        cursor.execute("""
        SELECT id, mastery_score
        FROM concept_mastery
        WHERE concept_name = ?
        """, (concept["name"],))

        existing = cursor.fetchone()

        if existing:

            concept_id, old_score = existing

            new_score = (
                old_score * 0.7 +
                concept["understanding"] * 0.3
            )

            cursor.execute("""
            UPDATE concept_mastery
            SET mastery_score = ?,
                notes = ?,
                last_reviewed = datetime('now')
            WHERE id = ?
            """, (
                new_score,
                concept["notes"],
                concept_id
            ))

        else:

            cursor.execute("""
            INSERT INTO concept_mastery (
                concept_name,
                mastery_score,
                last_reviewed,
                times_quizzed,
                times_correct,
                notes
            )
            VALUES (?, ?, datetime('now'), 0, 0, ?)
            """, (
                concept["name"],
                concept["understanding"],
                concept["notes"]
            ))

    conn.commit()
    conn.close()


# -----------------------------
# UPDATE MASTERY
# -----------------------------

def update_mastery(concept_name, quiz_score):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT mastery_score,
           times_quizzed,
           times_correct
    FROM concept_mastery
    WHERE concept_name = ?
    """, (concept_name,))

    row = cursor.fetchone()

    if row:

        old_score, times_q, times_correct = row

        new_score = (
            old_score * 0.8 +
            quiz_score * 0.2
        )

        correct = 1 if quiz_score > 0.7 else 0

        cursor.execute("""
        UPDATE concept_mastery
        SET mastery_score = ?,
            times_quizzed = ?,
            times_correct = ?,
            last_reviewed = datetime('now')
        WHERE concept_name = ?
        """, (
            new_score,
            times_q + 1,
            times_correct + correct,
            concept_name
        ))

    conn.commit()
    conn.close()


# -----------------------------
# LEARNING CONTEXT
# -----------------------------

def get_learning_context():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT concept_name,
           mastery_score,
           notes
    FROM concept_mastery
    ORDER BY mastery_score ASC
    LIMIT 5
    """)

    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return "No prior learning data."

    context = "User learning profile:\n\n"

    for row in rows:

        context += f"""
        Concept: {row[0]}
        Mastery Score: {round(row[1], 2)}
        Notes: {row[2]}

        """

    return context