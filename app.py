import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. पेज सेटअप (मोबाइल पर साइडबार डिफ़ॉल्ट बंद ताकि स्क्रीन न ढके)
st.set_page_config(
    page_title="Diva AI Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. कस्टम मोबाइल CSS (सॉफ्ट और क्लीन लुक)
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #ffffff; }
    .title-box {
        background: #1a1f2c;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #2d3748;
    }
    .main-heading { font-size: 20px; font-weight: 700; color: #60a5fa; }
    .sub-heading { font-size: 13px; color: #9ca3af; }
</style>
""", unsafe_allow_html=True)

# 3. Gemini API सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY नहीं मिली! Streamlit Secrets चेक करें।")
    st.stop()

genai.configure(api_key=api_key)

# 4. स्टेट मैनेजमेंट
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 5. मुख्य टैब इंटरफेस
tab_chat, tab_studio = st.tabs(["💬 Diva AI चैट", "📸 प्रो स्टूडियो (Face-Safe)"])

# ==================== टैब 1: AI चैट ====================
with tab_chat:
    st.markdown("""
    <div class="title-box">
        <div class="main-heading">✨ Diva AI स्मार्ट असिस्टेंट</div>
        <div class="sub-heading">स्टडी नोट्स, कोडिंग, बिज़नेस या कुछ भी पूछें।</div>
    </div>
    """, unsafe_allow_html=True)

    # चैट हिस्ट्री
    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "⚡"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # वॉइस व टेक्स्ट इनपुट
    voice = st.audio_input("वॉइस इनपुट", key="chat_voice")
    text_in = st.chat_input("Diva से कुछ भी पूछें...")

    if text_in or voice:
        user_msg = text_in if text_in else "🎙️ [वॉइस संदेश]"
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        with st.chat_message("user", avatar="👤"):
            st.write(user_msg)

        with st.chat_message("assistant", avatar="⚡"):
            def stream_response():
                payload = []
                if voice and not text_in:
                    payload.append({"mime_type": "audio/wav", "data": voice.read()})
                    payload.append("कृपया इस वॉइस इनपुट का हिंदी में विस्तार से उत्तर दें।")
                else:
                    payload.append(text_in)

                # आपके चुने हुए मॉडल: 3.6-flash और 3.8-flash
                target_models = ["gemini-3.6-flash", "gemini-3.8-flash"]
                worked = False
                
                for m_name in target_models:
                    try:
                        m = genai.GenerativeModel(m_name)
                        res = m.generate_content(payload, stream=True)
                        for chunk in res:
                            if chunk.text:
                                yield chunk.text
                        worked = True
                        break
                    except Exception:
                        continue

                if not worked:
                    yield "⏳ Google कोटा लिमिट है। कृपया 10-15 सेकंड रुककर दोबारा पूछें।"

            full_reply = st.write_stream(stream_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_reply})

# ==================== टैब 2: प्रो स्टूडियो ====================
with tab_studio:
    st.markdown("""
    <div class="title-box">
        <div class="main-heading">📸 फ़ेस-सेफ़ बैकग्राउंड स्टूडियो</div>
        <div class="sub-heading">चेहरा 100% सेफ़ रहेगा — केवल बैकग्राउंड बदलेगा।</div>
    </div>
    """, unsafe_allow_html=True)

    up_img = st.file_uploader("फ़ोटो अपलोड करें", type=["jpg", "jpeg", "png"])
    if up_img:
        orig = Image.open(up_img)
        c1, c2 = st.columns(2)
        with c1:
            st.image(orig, caption="मूल फ़ोटो", use_container_width=True)

        bg_mode = st.selectbox(
            "नया बैकग्राउंड चुनें:",
            ["ट्रांसपेरेंट (PNG)", "सफ़ेद (Passport White)", "नेवी ब्लू (Studio Blue)", "सॉफ़्ट ग्रे (Modern Gray)", "कस्टम कलर व्हील"]
        )

        hex_color = "#ffffff"
        if bg_mode == "कस्टम कलर व्हील":
            hex_color = st.color_picker("पसंदीदा रंग चुनें", "#ffffff")

        if st.button("✨ बैकग्राउंड बदलें (1-Click)", use_container_width=True):
            with st.spinner("प्रोसेसिंग जारी है..."):
                try:
                    from rembg import remove
                    b_in = io.BytesIO()
                    orig.save(b_in, format="PNG")
                    cutout = Image.open(io.BytesIO(remove(b_in.getvalue()))).convert("RGBA")

                    if bg_mode == "ट्रांसपेरेंट (PNG)":
                        final_res = cutout
                    else:
                        color_presets = {
                            "सफ़ेद (Passport White)": (255, 255, 255),
                            "नेवी ब्लू (Studio Blue)": (24, 52, 115),
                            "सॉफ़्ट ग्रे (Modern Gray)": (224, 226, 230),
                        }
                        rgb = color_presets.get(bg_mode)
                        if not rgb:
                            rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

                        bg_layer = Image.new("RGBA", cutout.size, rgb + (255,))
                        bg_layer.paste(cutout, (0, 0), mask=cutout)
                        final_res = bg_layer.convert("RGB")

                    with c2:
                        st.image(final_res, caption="एडिटेड फ़ोटो", use_container_width=True)
                        b_out = io.BytesIO()
                        fmt = "PNG" if bg_mode == "ट्रांसपेरेंट (PNG)" else "JPEG"
                        final_res.save(b_out, format=fmt)
                        st.download_button(
                            label="📥 फ़ोटो डाउनलोड करें",
                            data=b_out.getvalue(),
                            file_name=f"edited_photo.{fmt.lower()}",
                            mime=f"image/{fmt.lower()}",
                            use_container_width=True
                        )
                except Exception as ex:
                    st.error(f"एरर आया: {ex}")

