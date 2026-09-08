import streamlit as st
from google import genai
from PIL import Image
import io
import base64

# ============================================================
# PAGE SETUP
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

.stApp {
    background: #0b0f19;
    color: white;
}

section[data-testid="stSidebar"] {
    background: #101522;
    border-right: 1px solid #252b3a;
}

.diva-title {
    font-size: 34px;
    font-weight: 900;
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
    margin-bottom: 25px;
}

.feature-card {
    background: #131927;
    border: 1px solid #252c3d;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 15px;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid #303749;
    background: #171d2b;
    color: white;
}

.stButton > button:hover {
    border-color: #ff4b91;
    color: #ff75aa;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #151b28;
    border-radius: 12px;
    padding: 10px 18px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(
        90deg,
        #ff3f8e,
        #8c5cff
    ) !important;
    color: white !important;
}

[data-testid="stChatMessage"] {
    border-radius: 18px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# GEMINI API
# ============================================================

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY नहीं मिली।\n\n"
        "`.streamlit/secrets.toml` में API key डालें।"
    )
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini Client error: {e}")
    st.stop()

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interaction_id" not in st.session_state:
    st.session_state.interaction_id = None

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-3.6-flash"

if "thinking_level" not in st.session_state:
    st.session_state.thinking_level = "medium"

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Diva AI Pro.

You are a smart, friendly and helpful AI assistant.

You understand Hindi, Hinglish and English.

Rules:

1. Reply in the language used by the user.
2. Give accurate and useful answers.
3. Keep simple answers short.
4. Give detailed answers when needed.
5. Use Markdown when useful.
6. For coding questions, provide complete working code.
7. Explain difficult things simply.
8. If an image is provided, analyze it carefully.
9. Never pretend you performed an action that you cannot perform.
10. Be friendly and professional.
"""

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="diva-title">✨ Diva AI</div>',
        unsafe_allow_html=True
    )

    st.caption("● AI Online")

    st.divider()

    # New chat
    if st.button(
        "🆕 नई चैट",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.interaction_id = None

        st.rerun()

    # Clear
    if st.button(
        "🗑️ चैट साफ करें",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.interaction_id = None

        st.rerun()

    st.divider()

    st.subheader("⚙️ AI Settings")

    model_options = [
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash"
    ]

    selected_model = st.selectbox(
        "AI Model",
        model_options,
        index=model_options.index(
            st.session_state.selected_model
        )
        if st.session_state.selected_model in model_options
        else 0
    )

    st.session_state.selected_model = selected_model

    thinking_level = st.selectbox(
        "🧠 Thinking Level",
        [
            "minimal",
            "low",
            "medium",
            "high"
        ],
        index=2
    )

    st.session_state.thinking_level = thinking_level

    st.divider()

    st.markdown("### 🚀 Features")

    st.caption("💬 Smart AI Chat")
    st.caption("🧠 Conversation Memory")
    st.caption("🖼️ Image Understanding")
    st.caption("🎙️ Voice Input")
    st.caption("🎨 Photo Studio")
    st.caption("⚡ Gemini 3.6 Flash")

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="diva-title">Diva AI Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="diva-subtitle">'
    'आपका स्मार्ट AI Assistant और Creative Studio'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# TABS
# ============================================================

chat_tab, photo_tab, about_tab = st.tabs(
    [
        "💬 AI Chat",
        "🎨 Photo Studio",
        "ℹ️ About"
    ]
)

# ============================================================
# CHAT
# ============================================================

with chat_tab:

    # Welcome
    if not st.session_state.messages:

        st.markdown("""
        <div class="feature-card">

        <h3>👋 नमस्ते! मैं Diva AI हूँ</h3>

        <p>
        मुझसे coding, पढ़ाई, business,
        ideas, images या किसी भी विषय के बारे में पूछें।
        </p>

        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info(
                "💻 **Coding**\n\n"
                "Python, websites और apps"
            )

        with col2:
            st.info(
                "🧠 **Ideas**\n\n"
                "Business और creative ideas"
            )

        with col3:
            st.info(
                "📸 **Vision**\n\n"
                "Images को समझें"
            )

    # --------------------------------------------------------
    # OLD MESSAGES
    # --------------------------------------------------------

    for message in st.session_state.messages:

        avatar = (
            "👤"
            if message["role"] == "user"
            else "✨"
        )

        with st.chat_message(
            message["role"],
            avatar=avatar
        ):

            st.markdown(
                message["content"]
            )

    # --------------------------------------------------------
    # IMAGE UPLOAD
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

        preview = Image.open(
            uploaded_image
        )

        st.image(
            preview,
            caption="Attached Image",
            width=280
        )

    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    voice_file = st.audio_input(
        "🎙️ Voice message",
        key="voice_input"
    )

    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    prompt = st.chat_input(
        "Diva से कुछ भी पूछें..."
    )

    # --------------------------------------------------------
    # SEND MESSAGE
    # --------------------------------------------------------

    if prompt or voice_file:

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

            if uploaded_image:

                st.image(
                    Image.open(uploaded_image),
                    width=250
                )

        # ----------------------------------------------------
        # BUILD INPUT
        # ----------------------------------------------------

        input_data = []

        # Text
        if prompt:

            input_data.append(
                {
                    "type": "text",
                    "text": prompt
                }
            )

        # Image
        if uploaded_image:

            image_bytes = uploaded_image.getvalue()

            image_base64 = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            input_data.append(
                {
                    "type": "image",
                    "data": image_base64,
                    "mime_type": uploaded_image.type
                }
            )

            if not prompt:

                input_data.append(
                    {
                        "type": "text",
                        "text": (
                            "इस image को ध्यान से "
                            "analyze करो और इसका "
                            "विस्तार से वर्णन करो।"
                        )
                    }
                )

        # Voice
        if voice_file:

            audio_bytes = voice_file.getvalue()

            audio_base64 = base64.b64encode(
                audio_bytes
            ).decode("utf-8")

            input_data.append(
                {
                    "type": "audio",
                    "data": audio_base64,
                    "mime_type": (
                        voice_file.type
                        or "audio/wav"
                    )
                }
            )

            input_data.append(
                {
                    "type": "text",
                    "text": (
                        "इस voice message को समझकर "
                        "उपयोगी उत्तर दो।"
                    )
                }
            )

        # ----------------------------------------------------
        # AI RESPONSE
        # ----------------------------------------------------

        with st.chat_message(
            "assistant",
            avatar="✨"
        ):

            try:

                request = {
                    "model":
                        st.session_state.selected_model,

                    "input":
                        input_data,

                    "system_instruction":
                        SYSTEM_PROMPT,

                    "generation_config": {
                        "thinking_level":
                            st.session_state.thinking_level
                    }
                }

                # Continue conversation
                if st.session_state.interaction_id:

                    request[
                        "previous_interaction_id"
                    ] = st.session_state.interaction_id

                # Gemini request
                interaction = client.interactions.create(
                    **request
                )

                # Save conversation ID
                if getattr(
                    interaction,
                    "id",
                    None
                ):

                    st.session_state.interaction_id = (
                        interaction.id
                    )

                # Get answer
                answer = getattr(
                    interaction,
                    "output_text",
                    None
                )

                # Fallback
                if not answer:

                    answer = ""

                    for step in getattr(
                        interaction,
                        "steps",
                        []
                    ):

                        if getattr(
                            step,
                            "type",
                            ""
                        ) == "model_output":

                            for block in getattr(
                                step,
                                "content",
                                []
                            ):

                                if getattr(
                                    block,
                                    "type",
                                    ""
                                ) == "text":

                                    answer += (
                                        block.text
                                    )

                if not answer:

                    answer = (
                        "मुझे इस बार कोई उत्तर नहीं मिला। "
                        "कृपया दोबारा कोशिश करें।"
                    )

                st.markdown(answer)

                # Save AI message
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as error:

                error_text = str(error)

                if "429" in error_text:

                    st.error(
                        "⏳ API की limit पूरी हो गई है। "
                        "थोड़ी देर बाद फिर कोशिश करें।"
                    )

                elif (
                    "401" in error_text
                    or "403" in error_text
                    or "API key" in error_text
                ):

                    st.error(
                        "🔑 Gemini API key में समस्या है। "
                        "अपनी `GEMINI_API_KEY` check करें।"
                    )

                elif "404" in error_text:

                    st.error(
                        "❌ Model उपलब्ध नहीं है। "
                        "Sidebar से दूसरा model चुनकर देखें।"
                    )

                else:

                    st.error(
                        "⚠️ Gemini Error:\n\n"
                        + error_text
                    )

# ============================================================
# PHOTO STUDIO
# ============================================================

with photo_tab:

    st.subheader(
        "📸 Diva Pro Photo Studio"
    )

    st.caption(
        "Background हटाएँ और नया background लगाएँ।"
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

        if st.button(
            "✨ Background बदलें",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                "Photo process हो रही है..."
            ):

                try:

                    from rembg import remove

                    # Convert image
                    image_bytes = io.BytesIO()

                    input_image.save(
                        image_bytes,
                        format="PNG"
                    )

                    # Remove background
                    result = remove(
                        image_bytes.getvalue()
                    )

                    foreground = Image.open(
                        io.BytesIO(result)
                    ).convert("RGBA")

                    colors = {

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

                        final_image = foreground

                        file_format = "PNG"
                        mime_type = "image/png"

                    else:

                        background = Image.new(
                            "RGBA",
                            foreground.size,
                            colors[bg_choice] + (255,)
                        )

                        background.paste(
                            foreground,
                            (0, 0),
                            foreground
                        )

                        final_image = (
                            background.convert("RGB")
                        )

                        file_format = "JPEG"
                        mime_type = "image/jpeg"

                    with col2:

                        st.image(
                            final_image,
                            caption="Final Result",
                            use_container_width=True
                        )

                        output = io.BytesIO()

                        if file_format == "JPEG":

                            final_image.save(
                                output,
                                format="JPEG",
                                quality=95
                            )

                        else:

                            final_image.save(
                                output,
                                format="PNG"
                            )

                        st.download_button(
                            "📥 Download Photo",
                            data=output.getvalue(),
                            file_name=(
                                "diva_edited."
                                + file_format.lower()
                            ),
                            mime=mime_type,
                            use_container_width=True
                        )

                except ImportError:

                    st.error(
                        "❌ rembg installed नहीं है।"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Photo error: {e}"
                    )

# ============================================================
# ABOUT
# ============================================================

with about_tab:

    st.subheader("✨ Diva AI Pro")

    st.markdown("""
    ### Diva AI में

    - 💬 AI Chat
    - 🧠 Conversation Memory
    - 🖼️ Image Understanding
    - 🎙️ Voice Input
    - 🎨 Photo Studio
    - ⚡ Gemini 3.6 Flash
    - 🧠 Adjustable Thinking
    - 🌙 Modern Dark UI

    Diva AI का उद्देश्य एक ही जगह पर
    AI assistant और creative tools देना है।
    """)

    st.success(
        "🚀 Diva AI Pro तैयार है!"
    )
