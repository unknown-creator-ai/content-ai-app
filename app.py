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

# 2. कस्टम CSS (Gemini स्टाइल बॉटम बार और डार्क थीम)
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    header { visibility: hidden; }
    
    /* टैब बार स्टाइल */
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
    
    /* बॉटम डॉक कंटेनर */
    .bottom-bar {
        position: fixed;
        bottom: 15px;
        left: 5%;
        width: 90%;
        background-color: #1e1f20;
        border-radius: 28px;
        padding: 6px 14px;
        display: flex;
        align-items: center;
        border: 1px solid #3c4043;
        z-index: 9999;
    }
    
    /* मुख्य चैट एरिया के नीचे स्पेस ताकि टेक्स्ट न छिपे */
    .chat-container {
        padding-bottom: 120px;
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
if "attached_image" not in st.session_state:
    st.session_state.attached_image = None

tab_chat, tab_studio = st.tabs(["💬 Diva AI", "🎨 स्टूडियो"])

# ==================== टैब 1: Diva AI (Gemini Bar) ====================
with tab_chat:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        st.markdown("<h2 style='text-align: center; color: #a8c7fa; margin-top: 40px;'>Hello, I'm Diva AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8e918f;'>Ask anything, attach photos, or record voice.</p>", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "✨"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("image"):
                st.image(msg["image"], width=240)
            st.markdown(msg["content"])
            
    st.markdown('</div>', unsafe_allow_html=True)

    # सिंगल इनपुट रो (Gemini जैसा)
    col_plus, col_txt, col_send = st.columns([1, 6, 1])

    with col_plus:
        with st.popover("➕", use_container_width=True):
            st.markdown("**मीडिया व टूल्स**")
            file_up = st.file_uploader("📷 फ़ोटो चुनें", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if file_up:
                st.session_state.attached_image = Image.open(file_up)
                st.success("फ़ोटो जोड़ी गई!")
            
            st.markdown("**वॉइस रिकॉर्डर**")
            v_msg = st.audio_input("वॉइस रिकॉर्ड करें", label_visibility="collapsed")

    with col_txt:
        user_input = st.text_input(
            "मैसेज", 
            placeholder="Ask Diva... " + ("(फ़ोटो अटैच है)" if st.session_state.attached_image else ""), 
            label_visibility="collapsed",
            key="user_text_query"
        )

    with col_send:
        send_btn = st.button("➔", use_container_width=True)

    # मैसेज प्रोसेस करना
    if send_btn and (user_input or v_msg or st.session_state.attached_image):
        final_text = user_input if user_input else ("🎙️ [वॉइस संदेश]" if v_msg else "📎 [फ़ोटो अपलोड]")
        cur_img = st.session_state.attached_image

        st.session_state.chat_history.append({"role": "user", "content": final_text, "image": cur_img})

        with st.chat_message("user", avatar="👤"):
            if cur_img:
                st.image(cur_img, width=240)
            st.write(final_text)

        with st.chat_message("assistant", avatar="✨"):
            def execute_reply():
                payload = []
                if cur_img:
                    payload.append(cur_img)
                if v_msg and not user_input:
                    payload.append({"mime_type": "audio/wav", "data": v_msg.read()})
                    payload.append("कृपया इस वॉइस मैसेज का हिंदी में विस्तार से उत्तर दें।")
                else:
                    payload.append(final_text)

                models = ["gemini-3.6-flash", "gemini-3.8-flash"]
                success = False
                for m_name in models:
                    try:
                        m = genai.GenerativeModel(m_name)
                        res = m.generate_content(payload, stream=True)
                        for chunk in res:
                            if chunk.text:
                                yield chunk.text
                        success = True
                        break
                    except Exception:
                        continue

                if not success:
                    yield "⏳ Google कोटा सीमा पर है। कृपया 10-15 सेकंड रुककर दोबारा पूछें।"

            out_text = st.write_stream(execute_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": out_text, "image": None})
            
            # अटैचमेंट साफ़ करना
            st.session_state.attached_image = None
            st.rerun()

# ==================== टैब 2: प्रो स्टूडियो (फ़ेस-सेफ़) ====================
with tab_studio:
    st.markdown("### 📸 फेस-सेफ़ बैकग्राउंड स्टूडियो")
    st.caption("चेहरा 100% ओरिजिनल रहेगा — केवल बैकग्राउंड बदलेगा।")

    studio_pic = st.file_uploader("फ़ोटो अपलोड करें", type=["jpg", "jpeg", "png"], key="st_pic_box")
    if studio_pic:
        img_src = Image.open(studio_pic)
        c1, c2 = st.columns(2)
        with c1:
            st.image(img_src, caption="मूल फ़ोटो", use_container_width=True)

        mode_bg = st.selectbox(
            "बैकग्राउंड रंग चुनें:",
            ["ट्रांसपेरेंट (PNG)", "सफ़ेद (Passport White)", "नेवी ब्लू (Studio Blue)", "सॉफ़्ट ग्रे (Modern Gray)", "कस्टम रंग"]
        )

        hex_val = "#ffffff"
        if mode_bg == "कस्टम रंग":
            hex_val = st.color_picker("रंग पिक करें", "#ffffff")

        if st.button("✨ बैकग्राउंड बदलें (1-Click)", use_container_width=True):
            with st.spinner("AI प्रोसेसिंग जारी है..."):
                try:
                    from rembg import remove
                    b_in = io.BytesIO()
                    img_src.save(b_in, format="PNG")
                    cutout = Image.open(io.BytesIO(remove(b_in.getvalue()))).convert("RGBA")

                    if mode_bg == "ट्रांसपेरेंट (PNG)":
                        final_out = cutout
                    else:
                        palette = {
                            "सफ़ेद (Passport White)": (255, 255, 255),
                            "नेवी ब्लू (Studio Blue)": (24, 52, 115),
                            "सॉफ़्ट ग्रे (Modern Gray)": (224, 226, 230),
                        }
                        rgb = palette.get(mode_bg)
                        if not rgb:
                            rgb = tuple(int(hex_val.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

                        bg_layer = Image.new("RGBA", cutout.size, rgb + (255,))
                        bg_layer.paste(cutout, (0, 0), mask=cutout)
                        final_out = bg_layer.convert("RGB")

                    with c2:
                        st.image(final_out, caption="एडिटेड फ़ोटो", use_container_width=True)
                        b_out = io.BytesIO()
                        fmt = "PNG" if mode_bg == "ट्रांसपेरेंट (PNG)" else "JPEG"
                        final_out.save(b_out, format=fmt)
                        st.download_button(
                            label="📥 डाउनलोड करें",
                            data=b_out.getvalue(),
                            file_name=f"diva_edit.{fmt.lower()}",
                            mime=f"image/{fmt.lower()}",
                            use_container_width=True
                        )
                except Exception as err:
                    st.error(f"एरर आया: {err}")

