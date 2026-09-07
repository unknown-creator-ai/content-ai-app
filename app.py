import streamlit as st
from google import genai

st.title("Smart AI")

prompt = st.text_input("Enter prompt:")

if st.button("Generate"):
    if not prompt:
        st.warning("Please enter a prompt.")
    else:
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.write(res.text)
        except Exception as e:
            st.error(f"Error details: {e}")

