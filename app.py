import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import io

# 1. पेज सेटअप और ChatGPT जैसा क्लीन मोबाइल लुक
st.set_page_config(page_title="Diva AI", page_icon="✨", layout="wide")

# ऊपर का हेडर, वॉटरमार्क और फ़ालतू बटन छिपाने के लिए CSS
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding-top: 1rem; padding-bottom: 5rem;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 2. Gemini AI सेटअप
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6flash")
else:
    st.warning("⚠️ कृपया Streamlit Secrets में GEMINI_API_KEY सेट करें।")

# 3. साइडबार: Clear Chat + Photo Editor Studio
with st.sidebar:
    st.title("⚙️ Diva AI Tools")
    
    # चैट डिलीट करने का बटन
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("🎨 Photo Editor Studio")
    uploaded_file = st.file_uploader("फ़ोटो अपलोड करें", type=["jpg", "jpeg", "png"])
    
    edited_image = None
    if uploaded_file:
        img = Image.open(uploaded_file)
        
        # एडिटिंग टूल्स
        st.markdown("### फ़ोटो एडिट टूल्स")
        rotate_deg = st.selectbox("घुमाएँ (Rotate)", [0, 90, 180, 270])
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
        contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
        sharpness = st.slider("Sharpness", 0.5, 3.0, 1.0, 0.1)
        filter_mode = st.selectbox("फ़िल्टर चुनें", ["Normal", "Black & White (Grayscale)", "Blur", "Contour"])

        # एडिटिंग लागू करना
        edited_image = img.rotate(rotate_deg, expand=True)
        enhancer = ImageEnhance.Brightness(edited_image)
        edited_image = enhancer.enhance(brightness)
        enhancer = ImageEnhance.Contrast(edited_image)
        edited_image = enhancer.enhance(contrast)
        enhancer = ImageEnhance.Sharpness(edited_image)
        edited_image = enhancer.enhance(sharpness)

        if filter_mode == "Black & White (Grayscale)":
            edited_image = edited_image.convert("L")
        elif filter_mode == "Blur":
            edited_image = edited_image.filter(ImageFilter.BLUR)
        elif filter_mode == "Contour":
            edited_image = edited_image.filter(ImageFilter.CONTOUR)

        st.image(edited_image, caption="Edited Preview", use_container_width=True)
        
        # एडिटेड फ़ोटो डाउनलोड करने का बटन
        buf = io.BytesIO()
        save_format = "PNG" if img.format == "PNG" else "JPEG"
        if edited_image.mode == "L":
            edited_image.save(buf, format=save_format)
        else:
            edited_image.convert("RGB").save(buf, format="JPEG")
            
        st.download_button(
            label="📥 Save / Download Photo",
            data=buf.getvalue(),
            file_name="diva_edited.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

# 4. मुख्य स्क्रीन: Diva AI ChatGPT इंटरफ़ेस
st.title("✨ Diva AI")

# चैट मेमोरी
if "messages" not in st.session_state:
    st.session_state.messages = []

# पिछली बातचीत बबल्स में दिखाना
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# नीचे ChatGPT जैसा इनपुट बार
if prompt := st.chat_input("Ask Diva AI anything..."):
    # यूज़र का मैसेज जोड़ना
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI का जवाब तैयार करना
    with st.chat_message("assistant"):
        with st.spinner("Diva AI सोच रही है..."):
            try:
                # अगर साइडबार में फ़ोटो है तो फ़ोटो + टेक्स्ट दोनों AI को भेजें
                if edited_image:
                    img_to_send = edited_image.convert("RGB") if edited_image.mode == "L" else edited_image
                    response = model.generate_content([prompt, img_to_send])
                else:
                    response = model.generate_content(prompt)
                
                reply_text = response.text
                st.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
            except Exception as e:
                error_msg = f"क्षमा करें, एरर आया: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
