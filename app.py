import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. पेज सेटअप
st.set_page_config(
    page_title="Diva AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. अल्ट्रा-मोबाइल फ्रेंडली Gemini स्टाइल CSS
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    header { visibility: hidden; }
    
    /* टैब बार को स्लीक बनाना */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; border-bottom: 1px solid #282a2c; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #9ca3af;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #282a2c !important;
        color: #a8c7fa !important;
    }

    /* चैट एरिया में पैडिंग ताकि इनपुट बार टेक्स्ट को न दबाए */
    .chat-scroll {
        padding-bottom: 20px;
    }

    /* इनपुट सेक्शन को एक ही कार्ड में पैक करना */
    div[data-testid="stExpander"] {
        background-color: #1e1f20;
        border: 1px solid #3c4043;
        border-radius: 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Gemini API सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY नहीं मिली!")
    st.stop()

genai.configure(api_key=api_key)

# 4. स्टेट इनिशियलाइज़ेशन
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "attached_img" not in st.session_state:
    st.session_state.attached_img = None

tab_chat, tab_studio = st.tabs(["💬 Diva AI", "🎨 स्टूडियो"])

# ==================== टैब 1: Diva AI ====================
with tab_chat:
    st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.markdown("<h2 style='text-align: center; color: #a8c7fa; margin-top: 25px;'>Hello, I'm Diva AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8e918f; font-size: 14px;'>Ask anything, attach photos, or record voice notes.</p>", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "✨"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("image"):
                st.image(msg["image"], width=240)
            st.markdown(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    # मीडिया अटैचमेंट और वॉइस के लिए कॉम्पैक्ट टॉगल (स्क्रीन पर बड़ा बॉक्स नहीं बनेगा)
    with st.expander("📎 फ़ोटो / वॉइस अटैच करें (Tap to expand)"):
        f_up = st.file_uploader("📷 कैमरा या गैलरी से फ़ोटो लें", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if f_up:
            st.session_state.attached_img = Image.open(f_up)
            st.success("✅ फ़ोटो अटैच हो गई")
        v_rec = st.audio_input("🎙️ वॉइस मैसेज रिकॉर्ड करें", label_visibility="collapsed")

    # सिंगल नेटिव चैट इनपुट बार (यह अपने आप स्क्रीन के बॉटम पर चिपकता है)
    prompt_placeholder = "Ask Diva..." if not st.session_state.attached_img else "Ask Diva... [फ़ोटो अटैच है]"
    prompt = st.chat_input(prompt_placeholder)

    if prompt or (v_rec and not prompt) or (st.session_state.attached_img and prompt):
        user_query = prompt if prompt else "🎙️ [वॉइस मैसेज]"
        cur_image = st.session_state.attached_img

        st.session_state.chat_history.append({"role": "user", "content": user_query, "image": cur_image})

        with st.chat_message("user", avatar="👤"):
            if cur_image:
                st.image(cur_image, width=240)
            st.write(user_query)

        with st.chat_message("assistant", avatar="✨"):
            def run_gemini():
                payload = []
                if cur_image:
                    payload.append(cur_image)
                if v_rec and not prompt:
                    payload.append({"mime_type": "audio/wav", "data": v_rec.read()})
                    payload.append("कृपया इस वॉइस मैसेज का हिंदी में विस्तार से उत्तर दें।")
                else:
                    payload.append(user_query)

                models = ["gemini-3.6-flash", "gemini-3.8-flash"]
                worked = False
                for m in models:
                    try:
                        ai_mod = genai.GenerativeModel(m)
                        res = ai_mod.generate_content(payload, stream=True)
                        for chunk in res:
                            if chunk.text:
                                yield chunk.text
                        worked = True
                        break
                    except Exception:
                        continue

                if not worked:
                    yield "⏳ कोटा सीमा पर है, कृपया 10-15 सेकंड बाद पूछें।"

            out = st.write_stream(run_gemini)
            st.session_state.chat_history.append({"role": "assistant", "content": out, "image": None})
            st.session_state.attached_img = None
            st.rerun()

# ==================== टैब 2: फ़ेस-सेफ़ स्टूडियो ====================
with tab_studio:
    st.markdown("### 📸 फ़ेस-सेफ़ स्टूडियो")
    st.caption("चेहरे में 0% बदलाव — सिर्फ बैकग्राउंड बदलेगा।")

    file_item = st.file_uploader("फ़ोटो अपलोड करें", type=["jpg", "jpeg", "png"], key="studio_file_box")
    if file_item:
        in_img = Image.open(file_item)
        st.image(in_img, caption="मूल फ़ोटो", use_container_width=True)

        choice = st.selectbox(
            "बैकग्राउंड रंग चुनें:",
            ["ट्रांसपेरेंट (PNG)", "सफ़ेद (Passport White)", "नेवी ब्लू (Studio Blue)", "सॉफ़्ट ग्रे (Modern Gray)", "कस्टम रंग"]
        )

        hex_code = "#ffffff"
        if choice == "कस्टम रंग":
            hex_code = st.color_picker("रंग पिक करें", "#ffffff")

        if st.button("✨ बैकग्राउंड बदलें (1-Click)", use_container_width=True):
            with st.spinner("AI बैकग्राउंड बदल रहा है..."):
                try:
                    from rembg import remove
                    b_in = io.BytesIO()
                    in_img.save(b_in, format="PNG")
                    cut = Image.open(io.BytesIO(remove(b_in.getvalue()))).convert("RGBA")

                    if choice == "ट्रांसपेरेंट (PNG)":
                        res_img = cut
                    else:
                        palette = {
                            "सफ़ेद (Passport White)": (255, 255, 255),
                            "नेवी ब्लू (Studio Blue)": (24, 52, 115),
                            "सॉफ़्ट ग्रे (Modern Gray)": (224, 226, 230),
                        }
                        rgb = palette.get(choice)
                        if not rgb:
                            rgb = tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

                        bg_layer = Image.new("RGBA", cut.size, rgb + (255,))
                        bg_layer.paste(cut, (0, 0), mask=cut)
                        res_img = bg_layer.convert("RGB")

                    st.image(res_img, caption="फाइनल रिजल्ट", use_container_width=True)
                    b_out = io.BytesIO()
                    fmt = "PNG" if choice == "ट्रांसपेरेंट (PNG)" else "JPEG"
                    res_img.save(b_out, format=fmt)
                    st.download_button(
                        "📥 डाउनलोड करें",
                        data=b_out.getvalue(),
                        file_name=f"diva_photo.{fmt.lower()}",
                        mime=f"image/{fmt.lower()}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"त्रुटि: {e}")

