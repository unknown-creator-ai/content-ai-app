import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance
import io

# 1. पेज सेटअप
st.set_page_config(
    page_title="Diva AI Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. कस्टम CSS (सॉफ्ट और क्लीन लुक)
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e222d;
        border-radius: 8px;
        color: white;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Gemini AI सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY नहीं मिली! Streamlit Secrets चेक करें।")
    st.stop()

genai.configure(api_key=api_key)

# 4. सेशन स्टेट
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 5. मुख्य टैब इंटरफेस
tab1, tab2 = st.tabs(["💬 AI चैट असिस्टेंट", "🎨 प्रो फोटो स्टूडियो"])

# ==================== टैब 1: AI चैट ====================
with tab1:
    st.subheader("⚡ Diva AI स्मार्ट चैट")
    
    # पुरानी बातचीत
    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "⚡"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # वॉइस इनपुट
    voice = st.audio_input("वॉइस संदेश भेजें", key="chat_voice")

    # टेक्स्ट इनपुट
    text_prompt = st.chat_input("Diva से कुछ भी पूछें...")

    if text_prompt or voice:
        query = text_prompt if text_prompt else "🎙️ [वॉइस संदेश]"
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user", avatar="👤"):
            st.write(query)

        with st.chat_message("assistant", avatar="⚡"):
            def stream_response():
                try:
                    model = genai.GenerativeModel("gemini-3.6-flash")
                    payload = []
                    if voice and not text_prompt:
                        payload.append({"mime_type": "audio/wav", "data": voice.read()})
                        payload.append("कृपया इस वॉइस मैसेज को सुनकर विस्तार से उत्तर दें।")
                    else:
                        payload.append(text_prompt)

                    res = model.generate_content(payload, stream=True)
                    for chunk in res:
                        if chunk.text:
                            yield chunk.text
                except Exception as err:
                    if "429" in str(err):
                        yield "⏳ Google कोटा लिमिट है, कृपया 10 सेकंड बाद दोबारा पूछें।"
                    else:
                        yield f"तकनीकी समस्या: {err}"

            bot_reply = st.write_stream(stream_response)
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# ==================== टैब 2: प्रो फोटो एडिटर (Face-Safe) ====================
with tab2:
    st.subheader("📸 फेस-सेफ बैकग्राउंड रिमूवर")
    st.caption("चेहरे या बॉडी में 0% बदलाव — सिर्फ बैकग्राउंड बदलेगा।")

    uploaded_img = st.file_uploader("अपनी फोटो चुनें", type=["jpg", "png", "jpeg"])

    if uploaded_img:
        input_image = Image.open(uploaded_img)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(input_image, caption="मूल फोटो (Original)", use_container_width=True)

        # बैकग्राउंड कलर चुनने का विकल्प
        bg_choice = st.selectbox(
            "नया बैकग्राउंड रंग चुनें:",
            ["पारदर्शी (Transparent PNG)", "सफेद (Studio White)", "नेवी ब्लू (Passport Blue)", "लाइट ग्रे (Soft Gray)", "काला (Dark Mood)"]
        )

        if st.button("✨ बैकग्राउंड बदलें (1-Click)", use_container_width=True):
            with st.spinner("प्रोसेसिंग जारी है... चेहरे को सुरक्षित रखा जा रहा है..."):
                try:
                    from rembg import remove
                    
                    # बैकग्राउंड हटाना
                    img_byte = io.BytesIO()
                    input_image.save(img_byte, format="PNG")
                    no_bg_bytes = remove(img_byte.getvalue())
                    foreground = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")

                    # नया बैकग्राउंड लगाना
                    if bg_choice == "पारदर्शी (Transparent PNG)":
                        final_img = foreground
                    else:
                        color_map = {
                            "सफेद (Studio White)": (255, 255, 255),
                            "नेवी ब्लू (Passport Blue)": (20, 50, 120),
                            "लाइट ग्रे (Soft Gray)": (220, 220, 220),
                            "काला (Dark Mood)": (15, 15, 15)
                        }
                        bg_color = color_map[bg_choice]
                        background = Image.new("RGBA", foreground.size, bg_color + (255,))
                        background.paste(foreground, (0, 0), mask=foreground)
                        final_img = background.convert("RGB")

                    with col2:
                        st.image(final_img, caption="फाइनल रिजल्ट", use_container_width=True)
                        
                        # डाउनलोड बटन
                        buf = io.BytesIO()
                        final_format = "PNG" if bg_choice == "पारदर्शी (Transparent PNG)" else "JPEG"
                        final_img.save(buf, format=final_format)
                        st.download_button(
                            label="📥 एडिटेड फोटो डाउनलोड करें",
                            data=buf.getvalue(),
                            file_name=f"edited_photo.{final_format.lower()}",
                            mime=f"image/{final_format.lower()}",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"फोटो प्रोसेस करने में एरर आया: {e}")

