import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance
import time

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(
    page_title="Diva AI - Smart Multimodal Assistant",
    page_icon="⚡",
    layout="wide"
)

# 2. Gemini AI सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY नहीं मिली! कृपया Streamlit Secrets में डालें।")
    st.stop()

genai.configure(api_key=api_key)

# 3. सेशन मैनेजमेंट
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"चैट 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "चैट 1"

# 4. साइडबार - टूल्स और हिस्ट्री
with st.sidebar:
    st.title("⚡ Diva AI Studio")
    
    # नया चैट बटन
    if st.button("➕ नई चैट शुरू करें", use_container_width=True):
        new_chat_name = f"चैट {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
        st.rerun()

    # चैट सेलेक्टर
    chat_list = list(st.session_state.all_chats.keys())
    st.session_state.current_chat = st.selectbox(
        "पिछली बातचीत:",
        chat_list,
        index=chat_list.index(st.session_state.current_chat)
    )

    st.markdown("---")
    st.subheader("📸 Face-Safe Studio")
    uploaded_file = st.file_uploader("फ़ोटो अपलोड करें", type=["jpg", "png", "jpeg"])
    enhanced_img = None
    
    if uploaded_file:
        raw_img = Image.open(uploaded_file)
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0)
        contrast = st.slider("Contrast", 0.5, 2.0, 1.0)
        
        img = ImageEnhance.Brightness(raw_img).enhance(brightness)
        enhanced_img = ImageEnhance.Contrast(img).enhance(contrast)
        st.image(enhanced_img, caption="प्रिव्यू", use_container_width=True)

    st.markdown("---")
    # चैट डाउनलोड बटन (कॉलेज प्रोजेक्ट फ़ीचर)
    current_history = st.session_state.all_chats[st.session_state.current_chat]
    chat_download_text = ""
    for msg in current_history:
        chat_download_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
        
    st.download_button(
        label="📥 चैट हिस्ट्री डाउनलोड करें",
        data=chat_download_text,
        file_name=f"{st.session_state.current_chat}_transcript.txt",
        mime="text/plain",
        use_container_width=True
    )

# 5. मुख्य चैट स्क्रीन
st.header(f"💬 {st.session_state.current_chat}")

# पुरानी बातचीत दिखाना
for msg in current_history:
    avatar = "👤" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# वॉयस इनपुट
audio_input = st.audio_input("वॉइस मैसेज (Tap to record)")

# टेक्स्ट इनपुट
prompt = st.chat_input("Ask Diva AI...")

# 6. AI रिस्पॉन्स हैंडलर (ऑटो एरर-प्रूफ)
if prompt or audio_input:
    user_text = prompt if prompt else "🎙️ [वॉइस मैसेज]"
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar="👤"):
        st.write(user_text)

    with st.chat_message("assistant", avatar="⚡"):
        def generate_ai_response():
            payload = []
            if audio_input and not prompt:
                payload.append({"mime_type": "audio/wav", "data": audio_input.read()})
                payload.append("कृपया इस वॉइस मैसेज को समझकर हिंदी में उत्तर दें।")
            else:
                payload.append(prompt)
                
            if enhanced_img:
                payload.append(enhanced_img)

            # सुरक्षित मॉडल रनिंग
            try:
                model = genai.GenerativeModel("gemini-3.6-flash")
                response = model.generate_content(payload, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                if "429" in str(e):
                    yield "⏳ **ट्रैफ़िक ज़्यादा है:** Google की फ़्री लिमिट के कारण थोड़ा विराम लगा है। कृपया 30-40 सेकंड रुककर दोबारा पूछें।"
                else:
                    yield f"⚠️ एक तकनीकी समस्या आई: {e}"

        final_response = st.write_stream(generate_ai_response)
        st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": final_response})

