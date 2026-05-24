import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


model = genai.GenerativeModel("models/gemini-2.5-flash")

st.title("Neuroscience Tutor")

user_input = st.text_input("Ask a neuroscience question:")

if user_input:
    response = model.generate_content(
        f"""
        You are a neuroscience tutor.
        Explain clearly and simply.
        Ask follow-up questions to check understanding.

        User question:
        {user_input}
        """
    )

    st.write(response.text)