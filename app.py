import streamlit as st
from google import genai

st.title("My AI App")

key = st.text_input("Gemini API Key:", type="password")
prompt = st.text_input("Enter prompt:")

if st.button("Generate"):
    if not key:
        st.warning("Please enter your Gemini API Key.")
    elif not prompt:
        st.warning("Please enter a prompt.")
    else:
        try:
            client = genai.Client(api_key=key.strip())
            res = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            st.write(res.text)
        except Exception as e:
            st.error(f"Error details: {e}")
