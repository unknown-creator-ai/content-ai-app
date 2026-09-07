import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import io

# 1. पेज सेटअप & ChatGPT डार्क-स्टाइल मोबाइल लेआउट
st.set_page_config(page_title="Diva AI Pro", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {display:none !important;}
    .block-container {padding-top: 1rem; padding-bottom: 5.5rem;}
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 10px;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .top-title {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Gemini AI सेटअप
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY कॉन्फ़िगर नहीं है!")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_gemini():
    for name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
        try:
            m = genai.GenerativeModel(name)
            m.generate_content("ping")
            return m
        except Exception:
            continue
    return genai.GenerativeModel("gemini-pro")

model = load_gemini()

# 3. टॉप बार (Diva AI + Quick Clear Chat)
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="top-title">⚡ Diva AI Pro</div>', unsafe_allow_html=True)
with c2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. साइडबार: फेस-प्रिजर्विंग फोटो स्टूडियो (Face Safe Enhancer)
with st.sidebar:
    st.title("🎨 Face-Safe Studio")
    st.caption("चेहरे की पहचान बदले बिना नेचुरल लाइटिंग और स्किन एनहांसमेंट")
    
    uploaded_file = st.file_uploader("फ़ोटो चुनें", type=["jpg", "jpeg", "png"])
    final_image = None
    
    if uploaded_file:
        raw_img = Image.open(uploaded_file).convert("RGB")
        
        # प्रो-ग्रेड फेस सेफ कंट्रोल्स
        st.markdown("**नेचुरल रीटचिंग टूल्स**")
        lighting = st.slider("☀️ स्टूडियो लाइट (Exposure)", 0.8, 1.6, 1.0, 0.05)
        contrast = st.slider("🌓 डेप्थ & क्लैरिटी (Contrast)", 0.8, 1.4, 1.05, 0.05)
        skin_glow = st.slider("✨ वॉर्म स्किन ग्लो (Warmth)", -20, 20, 0, 2)
        sharpness = st.slider("🔍 डिटेल शार्पनेस", 0.8, 2.0, 1.1, 0.1)

        # 1. लाइटिंग और कॉन्ट्रास्ट
        img_proc = ImageEnhance.Brightness(raw_img).enhance(lighting)
        img_proc = ImageEnhance.Contrast(img_proc).enhance(contrast)
        img_proc = ImageEnhance.Sharpness(img_proc).enhance(sharpness)
        
        # 2. फेस-सेफ वॉर्मथ ट्यूनिंग (RGB बैलेंस)
        if skin_glow != 0:
            arr = np.array(img_proc, dtype=np.int16)
            arr[:, :, 0] = np.clip(arr[:, :, 0] + skin_glow, 0, 255) # Red
            arr[:, :, 2] = np.clip(arr[:, :, 2] - skin_glow, 0, 255) # Blue
            img_proc = Image.fromarray(arr.astype(np.uint8))

        final_image = img_proc
        st.image(final_image, caption="Enhanced Preview", use_container_width=True)

        # डाउनलोड बटन
        buf = io.BytesIO()
        final_image.save(buf, format="JPEG", quality=95)
        st.download_button("📥 HD फ़ोटो सेव करें", data=buf.getvalue(), file_name="diva_portrait.jpg", mime="image/jpeg", use_container_width=True)

# 5. वॉइस इनपुट टूल (माइक)
with st.expander("🎙️ वॉइस मैसेज भेजें (Tap to record)", expanded=False):
    audio_val = st.audio_input("अपनी आवाज़ रिकॉर्ड करें")

# 6. चैट हिस्ट्री मैनेजमेंट
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# 7. इनपुट हैंडलर (टेक्स्ट, वॉइस और इमेज)
prompt = st.chat_input("Ask Diva AI anything...")

user_input = None
audio_to_process = None

if prompt:
    user_input = prompt
elif audio_val:
    user_input = "🎙️ [वॉइस मैसेज प्राप्त हुआ]"
    audio_to_process = audio_val

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # ChatGPT जैसी लाइव स्ट्रीमिंग
    with st.chat_message("assistant", avatar="⚡"):
        def generate_chunks():
            try:
                inputs = []
                if audio_to_process:
                    audio_bytes = audio_to_process.read()
                    inputs.append({"mime_type": "audio/wav", "data": audio_bytes})
                    inputs.append("कृपया इस ऑडियो को सुनें और हिंदी में सटीक उत्तर दें।")
                else:
                    inputs.append(prompt)

                if final_image:
                    inputs.append(final_image)

                response = model.generate_content(inputs, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            except Exception as err:
                yield f"एरर: {err}"

        full_response = st.write_stream(generate_chunks)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

