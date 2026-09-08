import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Diva AI Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main app */
    .stApp {
        background: #0b0f19;
        color: #ffffff;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #101522;
        border-right: 1px solid #252b3a;
    }

    /* Header */
    .diva-header {
        padding: 15px 0 5px 0;
    }

    .diva-title {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(
            90deg,
            #ff4b91,
            #9b6cff,
            #4cc9f0
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .diva-subtitle {
        color: #8f98aa;
        font-size: 14px;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 8px;
        margin-bottom: 8px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #303749;
        background: #171d2b;
        color: white;
        transition: 0.2s;
    }

    .stButton > button:hover {
        border-color: #ff4b91;
        color: #ff75aa;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: #151b28;
        border-radius: 12px;
        padding: 10px 18px;
        color: #aab2c3;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(
            90deg,
            #ff3f8e,
            #8c5cff
        ) !important;
        color: white !important;
    }

    /* Cards */
    .feature-card {
        background: #131927;
        border: 1px solid #252c3d;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .feature-title {
        font-size: 18px;
        font-weight: 700;
    }

    .feature-text {
        color: #929bad;
        font-size: 13px;
    }

    /* Status */
    .online {
        color: #55e69b;
        font-size: 13px;
    }

</style>
""", unsafe_allow_html=True)

# ============================================================
# API SETUP
# ============================================================

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY नहीं मिली। "
        "`.streamlit/secrets.toml` में API key डालें।"
    )
    st.stop()

genai.configure(api_key=api_key)

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """
You are Diva AI, a highly capable, friendly and intelligent AI assistant.

Rules:
- Give accurate and useful answers.
- Understand Hindi, Hinglish and English.
- Keep answers clear and well structured.
- Use Markdown when useful.
- If the user asks for code, provide complete working code.
- Never claim to have performed an action you cannot perform.
"""

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-2.0-flash"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="diva-title">✨ Diva AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="online">● AI Online</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### ⚙️ AI Settings")

    model_options = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]

    selected_model = st.selectbox(
        "AI Model",
        model_options,
        index=(
            model_options.index(st.session_state.selected_model)
            if st.session_state.selected_model in model_options
            else 0
        )
    )

    st.session_state.selected_model = selected_model

    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1
    )

    st.session_state.temperature = temperature

    st.divider()

    st.markdown("### 🧠 Personality")

    system_prompt = st.text_area(
        "System Instructions",
        value=st.session_state.system_prompt,
        height=180
    )

    st.session_state.system_prompt = system_prompt

    st.divider()

    # New chat
    if st.button(
        "🆕 New Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    # Clear chat
    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption("Diva AI Pro 2.0")
    st.caption("Built with Python + Gemini")

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="diva-header">
    <div class="diva-title">Diva AI Pro</div>
    <div class="diva-subtitle">
        Your intelligent AI assistant & creative studio
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================

chat_tab, studio_tab, about_tab = st.tabs(
    [
        "💬 AI Chat",
        "🎨 Photo Studio",
        "ℹ️ About"
    ]
)

# ============================================================
# CHAT TAB
# ============================================================

with chat_tab:

    # Welcome screen
    if not st.session_state.messages:

        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                👋 Welcome to Diva AI
            </div>
            <div class="feature-text">
                Ask questions, write code, analyze images,
                brainstorm ideas or simply chat.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("💻 **Coding**\n\nBuild apps & debug code.")

        with col2:
            st.info("🧠 **Ideas**\n\nBrainstorm anything.")

        with col3:
            st.info("📸 **Vision**\n\nAnalyze images.")

    # --------------------------------------------------------
    # Display previous messages
    # --------------------------------------------------------

    for message in st.session_state.messages:

        role = message["role"]

        if role == "user":
            avatar = "👤"
        else:
            avatar = "✨"

        with st.chat_message(
            role,
            avatar=avatar
        ):
            st.markdown(message["content"])

    # --------------------------------------------------------
    # Image uploader
    # --------------------------------------------------------

    uploaded_image = st.file_uploader(
        "📎 Image attach करें",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="chat_image"
    )

    if uploaded_image:

        image = Image.open(uploaded_image)

        st.image(
            image,
            caption="Attached image",
            width=300
        )

    # --------------------------------------------------------
    # Voice input
    # --------------------------------------------------------

    voice = st.audio_input(
        "🎙️ Voice message",
        key="voice_input"
    )

    # --------------------------------------------------------
    # Chat input
    # --------------------------------------------------------

    prompt = st.chat_input(
        "Diva से कुछ भी पूछें..."
    )

    # --------------------------------------------------------
    # Process message
    # --------------------------------------------------------

    if prompt or voice:

        if prompt:
            user_text = prompt
        else:
            user_text = "🎙️ Voice message"

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        with st.chat_message(
            "user",
            avatar="👤"
        ):
            st.markdown(user_text)

        # ----------------------------------------------------
        # Assistant response
        # ----------------------------------------------------

        with st.chat_message(
            "assistant",
            avatar="✨"
        ):

            response_placeholder = st.empty()

            try:

                model = genai.GenerativeModel(
                    model_name=st.session_state.selected_model,
                    system_instruction=st.session_state.system_prompt
                )

                contents = []

                # Conversation history
                for msg in st.session_state.messages[:-1]:

                    contents.append(
                        {
                            "role": (
                                "user"
                                if msg["role"] == "user"
                                else "model"
                            ),
                            "parts": [
                                msg["content"]
                            ]
                        }
                    )

                # Current user message
                current_parts = []

                if prompt:
                    current_parts.append(prompt)

                # Image
                if uploaded_image:

                    image_bytes = uploaded_image.read()

                    current_parts.append(
                        {
                            "mime_type":
                                uploaded_image.type,
                            "data":
                                image_bytes
                        }
                    )

                # Voice
                if voice:

                    voice_bytes = voice.read()

                    current_parts.append(
                        {
                            "mime_type":
                                voice.type or "audio/wav",
                            "data":
                                voice_bytes
                        }
                    )

                    current_parts.append(
                        "Please understand the voice message "
                        "and respond appropriately."
                    )

                contents.append(
                    {
                        "role": "user",
                        "parts": current_parts
                    }
                )

                # Generation config
                generation_config = {
                    "temperature":
                        st.session_state.temperature
                }

                # Stream response
                response = model.generate_content(
                    contents,
                    generation_config=generation_config,
                    stream=True
                )

                full_response = ""

                for chunk in response:

                    try:
                        text = chunk.text
                    except Exception:
                        text = ""

                    if text:

                        full_response += text

                        response_placeholder.markdown(
                            full_response + "▌"
                        )

                        time.sleep(0.01)

                response_placeholder.markdown(
                    full_response
                )

                # Save response
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": full_response
                    }
                )

            except Exception as error:

                error_text = str(error)

                if "429" in error_text:

                    friendly_error = (
                        "⏳ **API limit reached.**\n\n"
                        "थोड़ी देर बाद फिर कोशिश करें।"
                    )

                elif "API key" in error_text:

                    friendly_error = (
                        "🔑 **API Key problem.**\n\n"
                        "अपनी Gemini API key check करें।"
                    )

                else:

                    friendly_error = (
                        "⚠️ **Something went wrong.**\n\n"
                        f"`{error_text}`"
                    )

                response_placeholder.error(
                    friendly_error
                )

# ============================================================
# PHOTO STUDIO
# ============================================================

with studio_tab:

    st.subheader("📸 Diva Pro Photo Studio")

    st.caption(
        "Background remove करें और नया background लगाएँ।"
    )

    uploaded_img = st.file_uploader(
        "अपनी फोटो चुनें",
        type=[
            "jpg",
            "png",
            "jpeg",
            "webp"
        ],
        key="studio_image"
    )

    if uploaded_img:

        input_image = Image.open(
            uploaded_img
        ).convert("RGBA")

        col1, col2 = st.columns(2)

        with col1:

            st.image(
                input_image,
                caption="Original",
                use_container_width=True
            )

        bg_choice = st.selectbox(
            "🎨 Background",
            [
                "Transparent",
                "Studio White",
                "Passport Blue",
                "Soft Gray",
                "Dark Mood",
                "Pink",
                "Purple"
            ]
        )

        # Optional resize
        resize_enabled = st.checkbox(
            "📐 Optimize image size",
            value=False
        )

        if st.button(
            "✨ Remove & Change Background",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                "AI background processing..."
            ):

                try:

                    from rembg import remove

                    # Input bytes
                    img_byte = io.BytesIO()

                    input_image.save(
                        img_byte,
                        format="PNG"
                    )

                    # Remove background
                    no_bg_bytes = remove(
                        img_byte.getvalue()
                    )

                    foreground = Image.open(
                        io.BytesIO(no_bg_bytes)
                    ).convert("RGBA")

                    # Optional optimization
                    if resize_enabled:

                        max_size = 1600

                        foreground.thumbnail(
                            (
                                max_size,
                                max_size
                            ),
                            Image.Resampling.LANCZOS
                        )

                    # Background
                    color_map = {

                        "Studio White":
                            (255, 255, 255),

                        "Passport Blue":
                            (20, 50, 120),

                        "Soft Gray":
                            (220, 220, 220),

                        "Dark Mood":
                            (15, 15, 15),

                        "Pink":
                            (255, 105, 180),

                        "Purple":
                            (110, 70, 180)
                    }

                    if bg_choice == "Transparent":

                        final_img = foreground

                        final_format = "PNG"
                        mime = "image/png"

                    else:

                        bg_color = color_map[
                            bg_choice
                        ]

                        background = Image.new(
                            "RGBA",
                            foreground.size,
                            bg_color + (255,)
                        )

                        background.paste(
                            foreground,
                            (0, 0),
                            foreground
                        )

                        final_img = background.convert(
                            "RGB"
                        )

                        final_format = "JPEG"
                        mime = "image/jpeg"

                    with col2:

                        st.image(
                            final_img,
                            caption="Final Result",
                            use_container_width=True
                        )

                        # Download
                        output = io.BytesIO()

                        final_img.save(
                            output,
                            format=final_format,
                            quality=95
                        )

                        st.download_button(
                            label="📥 Download Image",
                            data=output.getvalue(),
                            file_name=(
                                "diva_edited."
                                + final_format.lower()
                            ),
                            mime=mime,
                            use_container_width=True
                        )

                except ImportError:

                    st.error(
                        "❌ `rembg` install नहीं है.\n\n"
                        "Terminal में चलाएँ:\n"
                        "`pip install rembg`"
                    )

                except Exception as error:

                    st.error(
                        f"❌ Image processing error: {error}"
                    )

# ============================================================
# ABOUT
# ============================================================

with about_tab:

    st.subheader("✨ About Diva AI")

    st.markdown("""
    ### Diva AI Pro

    Diva एक multi-purpose AI assistant है जो:

    - 💬 Intelligent conversations
    - 🧠 Multi-turn context
    - 📸 Image understanding
    - 🎙️ Voice messages
    - 💻 Coding assistance
    - 🎨 Photo background editing
    - ⚙️ Custom AI personality
    - 🤖 Multiple Gemini models

    को एक ही application में combine करता है।
    """)

    st.success(
        "🚀 Diva AI Pro — Built for a better AI experience."
    )
