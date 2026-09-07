import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance
import numpy as np
import io
import uuid

# 1. पेज सेटअप और Gemini ऐप जैसा स्टाइल
st.set_page_config(page_title="Diva AI", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {display:none !important;}
    .block-container {padding-top: 1rem; padding-bottom: 5.5rem;}
    
    /* Gemini Greeting Style */
    .greeting-sub {
        font-size: 1.2rem;
        color: #888;
        font-weight: 500;
        margin-bottom: -5px;
    }
    .greeting-main {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
        margin-bottom: 2rem;
    }
    
    /* Action Buttons */
    div.stButton > button {
        border-radius: 12px;
        text-align: left;
        padding: 10px 16px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Gemini AI सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY नहीं मिली!")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    for name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
        try:
            m = genai.GenerativeModel(name)
            m.generate_content("hi")
            return m
        except Exception:
            continue
    return genai.GenerativeModel("gemini-pro")

model = get_model()

# 3. मल्टी-चैट सेशन मैनेजमेंट (Gemini साइडबार हिस्ट्री जैसी)
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} # format: {chat_id: {"title": "...", "messages": []}}

if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())[:8]
    st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

# 4. साइडबार (Google Gemini जैसा नेविगेशन और चैट हिस्ट्री)
with st.sidebar:
    # New Chat बटन
    if st.button("✏️ New chat", use_container_width=True):
        new_id = str(uuid.uuid4())[:8]
        st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("### 💬 Chats")
    
    # पुरानी चैट्स की लिस्ट
    chat_ids = list(st.session_state.all_chats.keys())
    for cid in reversed(chat_ids):
        chat_data = st.session_state.all_chats[cid]
        col_c, col_del = st.columns([4, 1])
        with col_c:
            label = ("👉 " if cid == st.session_state.current_chat_id else "") + chat_data["title"][:18]
            if st.button(label, key=f"chat_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{cid}"):
                del st.session_state.all_chats[cid]
                if st.session_state.current_chat_id == cid:
                    rem = list(st.session_state.all_chats.keys())
                    st.session_state.current_chat_id = rem[-1] if rem else None
                st.rerun()

    st.markdown("---")
    st.subheader("🎨 Face-Safe Studio")
    up_img = st.file_uploader("फ़ोटो अपलोड करें", type=["jpg", "jpeg", "png"], key="side_uploader")
    enhanced_img = None
    if up_img:
        base = Image.open(up_img).convert("RGB")
        b_val = st.slider("☀️ स्टूडियो लाइट", 0.8, 1.5, 1.05, 0.05)
        c_val = st.slider("🌓 डेप्थ & क्लैरिटी", 0.8, 1.4, 1.1, 0.05)
        w_val = st.slider("✨ स्किन ग्लो (Warmth)", -20, 20, 4, 2)
        
        proc = ImageEnhance.Brightness(base).enhance(b_val)
        proc = ImageEnhance.Contrast(proc).enhance(c_val)
        if w_val != 0:
            arr = np.array(proc, dtype=np.int16)
            arr[:, :, 0] = np.clip(arr[:, :, 0] + w_val, 0, 255)
            arr[:, :, 2] = np.clip(arr[:, :, 2] - w_val, 0, 255)
            proc = Image.fromarray(arr.astype(np.uint8))
        
        enhanced_img = proc
        st.image(enhanced_img, caption="Face-Preserved Preview", use_container_width=True)
        buf = io.BytesIO()
        enhanced_img.save(buf, format="JPEG", quality=95)
        st.download_button("📥 HD फ़ोटो सेव करें", data=buf.getvalue(), file_name="diva_edit.jpg", mime="image/jpeg", use_container_width=True)

# 5. वर्तमान चैट का डेटा लोड करना
current_id = st.session_state.current_chat_id
if not current_id or current_id not in st.session_state.all_chats:
    new_id = str(uuid.uuid4())[:8]
    st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id
    current_id = new_id

current_messages = st.session_state.all_chats[current_id]["messages"]

# 6. मुख्य स्क्रीन: खाली चैट होने पर Gemini जैसा वेलकम कार्ड
suggestion_clicked = None
if len(current_messages) == 0:
    st.markdown('<div class="greeting-sub">Hi Kundan</div>', unsafe_allow_html=True)
    st.markdown('<div class="greeting-main">Where should we start?</div>', unsafe_allow_html=True)
    
    # सजेशन बटन्स
    if st.button("🖼️ Create / Edit image", use_container_width=True):
        suggestion_clicked = "फोटो एडिट करने के बेहतरीन टिप्स बताओ"
    if st.button("🏏 Explore IPL Fan Zone", use_container_width=True):
        suggestion_clicked = "IPL के लेटेस्ट अपडेट्स और रोचक तथ्य बताओ"
    if st.button("🎵 Create music / lyrics", use_container_width=True):
        suggestion_clicked = "एक खूबसूरत गाने के बोल (lyrics) लिखकर दो"
    if st.button("📝 Write anything", use_container_width=True):
        suggestion_clicked = "मेरे लिए एक बेहतरीन विचार या पोस्ट लिखो"

# 7. पुरानी बातचीत स्क्रीन पर दिखाना
for msg in current_messages:
    av = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# 8. वॉइस मैसेज विकल्प
with st.expander("🎙️ वॉइस मैसेज (Tap to record)", expanded=False):
    audio_data = st.audio_input("माइक ऑन करें")

# 9. चैट इनपुट (टेक्स्ट या सजेशन)
prompt = st.chat_input("Ask Diva AI...")
if suggestion_clicked:
    prompt = suggestion_clicked

if prompt or audio_data:
    user_text = prompt if prompt else "🎙️ [वॉइस संदेश]"
    
    # पहली चैट का शीर्षक ऑटो-सेट करना
    if len(current_messages) == 0 and prompt:
        st.session_state.all_chats[current_id]["title"] = prompt[:22]

    current_messages.append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)

    with st.chat_message("assistant", avatar="✨"):
        def response_stream():
            try:
                inputs = []
                if audio_data and not prompt:
                    inputs.append({"mime_type": "audio/wav", "data": audio_data.read()})
                    inputs.append("कृपया इस वॉइस मैसेज को सुनकर हिंदी में उत्तर दें।")
                else:
                    inputs.append(prompt)
                
                if enhanced_img:
                    inputs.append(enhanced_img)

                res = model.generate_content(inputs, stream=True)
                for chunk in res:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                yield f"एरर: {e}"

        answer = st.write_stream(response_stream)
        current_messages.append({"role": "assistant", "content": answer})

