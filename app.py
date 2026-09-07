import streamlit as st
from google import genai

st.title("My AI App")

key = st.text_input("Gemini API Key:", type="password")
prompt = st.text_input("Enter prompt:")

if st.button("Generate"):
    if key and prompt:
        client = genai.Client(api_key=key.strip())
        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        st.write(res.text)
    else:
        st.warning("Please enter both API key and prompt.")
