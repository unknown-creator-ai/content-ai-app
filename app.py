import streamlit as st
from google import genai

st.title("My AI App")

key = st.text_input("Gemini API Key:", type="password")
prompt = st.text_input("Enter prompt:")

if st.button("Generate"):
    client = genai.Client(api_key=key)
    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    st.write(res.text)
