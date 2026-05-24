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
# GET WEAKEST CONCEPT
# -----------------------------

def get_weakest_concept():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT concept_name, mastery_score
    FROM concept_mastery
    ORDER BY mastery_score ASC
    LIMIT 1
    """)

    result = cursor.fetchone()

    conn.close()

    return result


# -----------------------------
# GENERATE QUESTION
# -----------------------------

def generate_question(concept):

    prompt = f"""
    Create ONE neuroscience retrieval question.

    Concept:
    {concept}

    Requirements:
    - concise
    - conceptual
    - reasoning-focused
    - avoid trivia
    """

    response = model.generate_content(prompt)

    return response.text


# -----------------------------
# EVALUATE ANSWER
# -----------------------------

def evaluate_answer(question, answer):

    prompt = f"""
    Evaluate this neuroscience answer.

    QUESTION:
    {question}

    USER ANSWER:
    {answer}

    Return ONLY valid JSON.

    Format:

    {{
      "score": 0.0,
      "feedback": "...",
      "misconceptions": [
        "..."
      ]
    }}
    """

    response = model.generate_content(prompt)

    raw_output = clean_json_response(
        response.text
    )

    try:

        parsed = json.loads(raw_output)

        return parsed

    except Exception as e:

        print("Evaluation parse error:", e)

        return {
            "score": 0.0,
            "feedback": "Could not evaluate answer.",
            "misconceptions": []
        }