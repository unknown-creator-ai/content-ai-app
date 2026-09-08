import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. पेज सेटअप
st.set_page_config(
    page_title="Diva AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. अल्ट्रा-क्लीन मोबाइल CSS
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    header { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #282a2c; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #c4c7c5;
        border-radius: 20px;
        padding: 6px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #282a2c !important;
        color: #a8c7fa !important;
    }
    div[data-testid="stChatMessage"] { background-color: transparent; }
</style>
""", unsafe_allow_html=True)

# 3. Gemini API सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY नहीं मिली!")
    st.stop()

genai.configure(api_key=api_key)

# 4. स्टेट मैनेजमेंट
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "temp_image" not in st.session_state:
    st.session_state.temp_image = None

tab_chat, tab_studio = st.tabs(["💬 Diva AI", "🎨 स्टूडियो"])

# ==================== टैब 1: Gemini स्टाइल चैट ====================
with tab_chat:
    # चैट हिस्ट्री
    if not st.session_state.chat_history:
        st.markdown("<h2 style='text-align: center; color: #a8c7fa; margin-top: 30px;'>Hello, I'm Diva AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8e918f;'>Ask anything, attach photos, or send voice notes.</p>", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "✨"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("image"):
                st.image(msg["image"], width=260)
            st.markdown(msg["content"])

    # अटैचमेंट और वॉइस के लिए मिनी पॉपओवर बार (Gemini जैसा `+` बटन)
    col_btn, col_preview = st.columns([1, 4])
    with col_btn:
        with st.popover("➕", use_container_width=True):
            st.markdown("**मीडिया जोड़ें**")
            up_img = st.file_uploader("📷 कैमरा / गैलरी", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if up_img:
                st.session_state.temp_image = Image.open(up_img)
            
            st.markdown("**वॉइस रिकॉर्डर**")
            voice_data = st.audio_input("वॉइस संदेश", label_visibility="collapsed")

    with col_preview:
        if st.session_state.temp_image:
            st.caption("✅ फोटो अटैच हो गई है")

    # चैट इनपुट बार
    text_prompt = st.chat_input("Ask Diva...")

    # मैसेज ट्रिगर
    if text_prompt or (voice_data and not text_prompt) or (st.session_state.temp_image and text_prompt):
        user_text = text_prompt if text_prompt else "🎙️ [वॉइस मैसेज]"
        active_img = st.session_state.temp_image
        
        st.session_state.chat_history.append({"role": "user", "content": user_text, "image": active_img})
        
        with st.chat_message("user", avatar="👤"):
            if active_img:
                st.image(active_img, width=260)
            st.write(user_text)

        with st.chat_message("assistant", avatar="✨"):
            def generate_reply():
                payload = []
                if active_img:
                    payload.append(active_img)
                if voice_data and not text_prompt:
                    payload.append({"mime_type": "audio/wav", "data": voice_data.read()})
                    payload.append("कृपया इस वॉइस मैसेज का हिंदी में विस्तार से उत्तर दें।")
                else:
                    payload.append(user_text)

                models = ["gemini-3.6-flash", "gemini-3.8-flash"]
                worked = False
                for m_name in models:
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
                    yield "⏳ Google कोटा सीमा पर है। कृपया 10-15 सेकंड रुककर दोबारा पूछें।"

            res_stream = st.write_stream(generate_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": res_stream, "image": None})
            # फोटो रीसेट
            st.session_state.temp_image = None
            st.rerun()

# ==================== टैब 2: प्रो स्टूडियो (फ़ेस-सेफ़) ====================
with tab_studio:
    st.markdown("### 📸 फेस-सेफ़ बैकग्राउंड स्टूडियो")
    st.caption("चेहरा 100% ओरिजिनल रहेगा — केवल बैकग्राउंड बदलेगा।")

    studio_file = st.file_uploader("फ़ोटो चुनें", type=["jpg", "jpeg", "png"], key="st_file")
    if studio_file:
        raw_pic = Image.open(studio_file)
        c1, c2 = st.columns(2)
        with c1:
            st.image(raw_pic, caption="मूल फ़ोटो", use_container_width=True)

        bg_mode = st.selectbox(
            "नया बैकग्राउंड चुनें:",
            ["ट्रांसपेरेंट (PNG)", "सफ़ेद (Passport White)", "नेवी ब्लू (Studio Blue)", "सॉफ़्ट ग्रे (Modern Gray)", "कस्टम रंग"]
        )

        hex_c = "#ffffff"
        if bg_mode == "कस्टम रंग":
            hex_c = st.color_picker("रंग चुनें", "#ffffff")

        if st.button("✨ बैकग्राउंड बदलें (1-Click)", use_container_width=True):
            with st.spinner("प्रोसेसिंग जारी है..."):
                try:
                    from rembg import remove
                    b_in = io.BytesIO()
                    raw_pic.save(b_in, format="PNG")
                    cutout = Image.open(io.BytesIO(remove(b_in.getvalue()))).convert("RGBA")

                    if bg_mode == "ट्रांसपेरेंट (PNG)":
                        final_pic = cutout
                    else:
                        color_map = {
                            "सफ़ेद (Passport White)": (255, 255, 255),
                            "नेवी ब्लू (Studio Blue)": (24, 52, 115),
                            "सॉफ़्ट ग्रे (Modern Gray)": (224, 226, 230),
                        }
                        rgb = color_map.get(bg_mode)
                        if not rgb:
                            rgb = tuple(int(hex_c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

                        bg_layer = Image.new("RGBA", cutout.size, rgb + (255,))
                        bg_layer.paste(cutout, (0, 0), mask=cutout)
                        final_pic = bg_layer.convert("RGB")

                    with c2:
                        st.image(final_pic, caption="एडिटेड फ़ोटो", use_container_width=True)
                        b_out = io.BytesIO()
                        fmt = "PNG" if bg_mode == "ट्रांसपेरेंट (PNG)" else "JPEG"
                        final_pic.save(b_out, format=fmt)
                        st.download_button(
                            label="📥 फ़ोटो डाउनलोड करें",
                            data=b_out.getvalue(),
                            file_name=f"diva_photo.{fmt.lower()}",
                            mime=f"image/{fmt.lower()}",
                            use_container_width=True
                        )
                except Exception as ex:
                    st.error(f"एरर आया: {ex}")

