import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. पेज सेटअप
st.set_page_config(
    page_title="Diva AI Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. मॉडर्न चैट UI CSS (Gemini स्टाइल बॉटम बार)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; margin-bottom: 12px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e222d;
        border-radius: 8px;
        color: #9ca3af;
        padding: 8px 18px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }
    .input-panel {
        background-color: #1a1f2c;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. API सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY नहीं मिली! कृपया Streamlit Secrets में डालें।")
    st.stop()

genai.configure(api_key=api_key)

# 4. सेशन स्टेट
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

tab_chat, tab_studio = st.tabs(["💬 Diva AI चैट", "📸 प्रो स्टूडियो (Face-Safe)"])

# ==================== टैब 1: चैट बार (कैमरा, गैलरी, वॉइस & टेक्स्ट) ====================
with tab_chat:
    # चैट इतिहास
    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "✨"
        with st.chat_message(msg["role"], avatar=avatar):
            if "image" in msg and msg["image"]:
                st.image(msg["image"], width=250)
            st.markdown(msg["content"])

    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    col_attach, col_voice = st.columns([1, 1])
    
    with col_attach:
        # गैलरी / कैमरा अटैचमेंट बटन
        uploaded_media = st.file_uploader("📎 कैमरा / गैलरी से फ़ोटो जोड़ें", type=["jpg", "jpeg", "png"], key="chat_media")
    
    with col_voice:
        # वॉइस इनपुट
        audio_in = st.audio_input("🎙️ वॉइस मैसेज रिकॉर्ड करें", key="voice_bar")
    st.markdown('</div>', unsafe_allow_html=True)

    # मुख्य टेक्स्ट इनपुट बार
    text_prompt = st.chat_input("Diva से कुछ भी पूछें...")

    # जब यूज़र मैसेज, फ़ोटो या वॉइस भेजे
    if text_prompt or audio_in or uploaded_media:
        user_text = text_prompt if text_prompt else ("🎙️ [वॉइस संदेश]" if audio_in else "📎 [फ़ोटो अपलोड]")
        
        chat_entry = {"role": "user", "content": user_text, "image": None}
        input_img = None
        if uploaded_media:
            input_img = Image.open(uploaded_media)
            chat_entry["image"] = input_img

        st.session_state.chat_history.append(chat_entry)
        
        with st.chat_message("user", avatar="👤"):
            if input_img:
                st.image(input_img, width=250)
            st.write(user_text)

        with st.chat_message("assistant", avatar="✨"):
            def stream_multimodal_reply():
                payload = []
                
                # इमेज जोड़ना
                if input_img:
                    payload.append(input_img)
                    
                # वॉइस या टेक्स्ट जोड़ना
                if audio_in and not text_prompt:
                    payload.append({"mime_type": "audio/wav", "data": audio_in.read()})
                    payload.append("कृपया इस वॉइस मैसेज/फ़ोटो को देखकर विस्तार से उत्तर दें।")
                else:
                    msg_to_send = text_prompt if text_prompt else "इस फ़ोटो को समझकर पूरा विवरण दें।"
                    payload.append(msg_to_send)

                # ऑटो-फ़ॉलबैक (3.6 और 3.8 मॉडल)
                models_to_try = ["gemini-3.6-flash", "gemini-3.8-flash"]
                responded = False
                
                for m_name in models_to_try:
                    try:
                        m = genai.GenerativeModel(m_name)
                        res = m.generate_content(payload, stream=True)
                        for chunk in res:
                            if chunk.text:
                                yield chunk.text
                        responded = True
                        break
                    except Exception:
                        continue

                if not responded:
                    yield "⏳ Google कोटा सीमा पर है। कृपया 10-15 सेकंड रुककर दोबारा प्रयास करें।"

            full_reply = st.write_stream(stream_multimodal_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": full_reply, "image": None})

# ==================== टैब 2: प्रो स्टूडियो (फ़ेस-सेफ़ बैकग्राउंड चेंजर) ====================
with tab_studio:
    st.markdown("### 📸 फेस-सेफ़ बैकग्राउंड स्टूडियो")
    st.caption("चेहरा 100% सुरक्षित रहेगा — पासपोर्ट या कस्टम बैकग्राउंड लगाएँ।")

    studio_img = st.file_uploader("फ़ोटो चुनें", type=["jpg", "jpeg", "png"], key="studio_uploader")
    if studio_img:
        orig = Image.open(studio_img)
        c1, c2 = st.columns(2)
        with c1:
            st.image(orig, caption="मूल फ़ोटो", use_container_width=True)

        bg_mode = st.selectbox(
            "नया बैकग्राउंड रंग चुनें:",
            ["ट्रांसपेरेंट (PNG)", "सफ़ेद (Passport White)", "नेवी ब्लू (Studio Blue)", "सॉफ़्ट ग्रे (Modern Gray)", "कस्टम कलर व्हील"]
        )

        hex_color = "#ffffff"
        if bg_mode == "कस्टम कलर व्हील":
            hex_color = st.color_picker("पसंदीदा रंग चुनें", "#ffffff")

        if st.button("✨ बैकग्राउंड बदलें (1-Click)", use_container_width=True):
            with st.spinner("AI बैकग्राउंड बदल रहा है..."):
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
                            label="📥 एडिटेड फ़ोटो डाउनलोड करें",
                            data=b_out.getvalue(),
                            file_name=f"diva_photo.{fmt.lower()}",
                            mime=f"image/{fmt.lower()}",
                            use_container_width=True
                        )
                except Exception as ex:
                    st.error(f"एरर आया: {ex}")

