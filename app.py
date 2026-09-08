import streamlit as st
from google import genai
from PIL import Image
import io
import base64
import uuid

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Diva AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

.stApp {
    background:
        radial-gradient(
            circle at 50% -10%,
            #252044 0%,
            #101119 35%,
            #090a0f 75%
        );
    color: #f5f5f7;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 100% !important;
    padding: 12px 3vw 120px 3vw !important;
}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #101116;
    border-right: 1px solid #252731;
}

section[data-testid="stSidebar"] .block-container {
    padding: 20px 14px !important;
}

/* ---------- LOGO ---------- */

.logo {
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -1px;

    background: linear-gradient(
        90deg,
        #ff4d9d,
        #9d6cff,
        #55d7ff
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #8f94a3;
    font-size: 14px;
}

/* ---------- TOP BAR ---------- */

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 10px 4px 15px;

    border-bottom: 1px solid #242731;
}

.top-name {
    font-size: 20px;
    font-weight: 700;
}

.status {
    color: #59e69b;
    font-size: 13px;
}

/* ---------- WELCOME ---------- */

.welcome {
    min-height: 55vh;

    display: flex;
    flex-direction: column;

    justify-content: center;
    align-items: center;

    text-align: center;
}

.welcome-icon {
    font-size: 64px;
    margin-bottom: 12px;
}

.welcome-title {
    font-size: clamp(34px, 5vw, 58px);
    font-weight: 850;

    background: linear-gradient(
        90deg,
        #ff65aa,
        #a778ff,
        #5bdcff
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-text {
    color: #9197a6;
    font-size: 16px;
    margin-top: 8px;
}

/* ---------- CARDS ---------- */

.card {
    background: rgba(23,25,33,.78);
    border: 1px solid #292c36;
    border-radius: 18px;

    padding: 18px;

    min-height: 105px;

    transition: .2s;
}

.card:hover {
    border-color: #a36cff;
    transform: translateY(-2px);
}

.card-title {
    font-weight: 700;
    font-size: 16px;
}

.card-text {
    color: #9298a7;
    font-size: 13px;
    margin-top: 6px;
}

/* ---------- CHAT ---------- */

[data-testid="stChatMessage"] {
    max-width: 900px !important;
    margin-left: auto !important;
    margin-right: auto !important;

    border-radius: 20px;
}

[data-testid="stChatMessageContent"] {
    font-size: 16px;
    line-height: 1.65;
}

/* ---------- INPUT ---------- */

[data-testid="stChatInput"] {
    max-width: 900px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stChatInput"] textarea {
    background: #181a22 !important;
    color: white !important;

    border: 1px solid #343742 !important;
    border-radius: 20px !important;
}

/* ---------- BUTTONS ---------- */

.stButton > button {
    border-radius: 13px;
    background: #171920;
    color: white;

    border: 1px solid #30333d;

    transition: .2s;
}

.stButton > button:hover {
    border-color: #ff579f;
    color: #ff75b1;
}

/* ---------- FILE UPLOADER ---------- */

[data-testid="stFileUploader"] {
    border-radius: 15px;
}

/* ---------- MOBILE ---------- */

@media(max-width: 700px) {

    .block-container {
        padding: 8px 10px 100px 10px !important;
    }

    .welcome {
        min-height: 50vh;
    }

    .welcome-icon {
        font-size: 48px;
    }

    [data-testid="stChatMessage"] {
        max-width: 100% !important;
    }

    [data-testid="stChatInput"] {
        max-width: 100% !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# API
# ============================================================

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY नहीं मिली।\n\n"
        "`.streamlit/secrets.toml` में अपनी API key डालें।"
    )
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini connection error: {e}")
    st.stop()

# ============================================================
# SESSION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interaction_id" not in st.session_state:
    st.session_state.interaction_id = None

if "model" not in st.session_state:
    st.session_state.model = "gemini-3.8-flash"

if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are Diva AI Pro.

You are an intelligent, friendly and highly capable AI assistant.

Language:
- Understand Hindi.
- Understand Hinglish.
- Understand English.
- Reply naturally in the user's language.

Behavior:
- Be accurate and helpful.
- Do not unnecessarily repeat the question.
- Keep simple answers concise.
- Give detailed answers for complex tasks.
- Use Markdown where helpful.
- Use headings and bullet points when useful.

Coding:
- Provide complete working code.
- Explain where code should be placed.
- Mention required packages when needed.
- Never invent APIs or functions.

Images:
- Carefully analyze uploaded images.
- Describe what is actually visible.
- Do not claim details that cannot be determined.

Important:
- Never claim to have completed an action you cannot perform.
- If something is uncertain, say so clearly.
"""

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="logo">✨ Diva AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Your intelligent AI companion</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # NEW CHAT
    if st.button(
        "＋  नई चैट",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.interaction_id = None
        st.session_state.chat_id = str(uuid.uuid4())

        st.rerun()

    st.divider()

    st.markdown("### 💬 Current Chat")

    if st.session_state.messages:

        first_message = next(
            (
                m["content"]
                for m in st.session_state.messages
                if m["role"] == "user"
            ),
            "नई चैट"
        )

        title = first_message[:35]

        if len(first_message) > 35:
            title += "..."

        st.caption("💬 " + title)

    else:

        st.caption("अभी कोई message नहीं है।")

    st.divider()

    st.markdown("### ⚙️ Model")

    selected_model = st.selectbox(
        "AI Model",
        [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.session_state.model = selected_model

    st.divider()

    st.markdown("### ✨ Diva")

    st.caption("● Online")
    st.caption("💬 Smart Chat")
    st.caption("🖼️ Image Understanding")
    st.caption("🎙️ Voice Input")
    st.caption("🌐 Web Search")
    st.caption("🎨 Photo Studio")

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.interaction_id = None

        st.rerun()

# ============================================================
# TOP BAR
# ============================================================

st.markdown(
    """
    <div class="topbar">

        <div class="top-name">
            ✨ Diva AI
        </div>

        <div class="status">
            ● Online
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TABS
# ============================================================

chat_tab, studio_tab = st.tabs(
    [
        "💬 Chat",
        "🎨 Photo Studio"
    ]
)

# ============================================================
# CHAT TAB
# ============================================================

with chat_tab:

    # --------------------------------------------------------
    # WELCOME
    # --------------------------------------------------------

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome">

                <div class="welcome-icon">
                    ✨
                </div>

                <div class="welcome-title">
                    Hello, I'm Diva
                </div>

                <div class="welcome-text">
                    पूछिए कुछ भी — मैं आपकी मदद करने के लिए तैयार हूँ।
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown(
                """
                <div class="card">
                    <div class="card-title">
                        💻 Coding
                    </div>
                    <div class="card-text">
                        Apps, Python, websites और debugging.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                """
                <div class="card">
                    <div class="card-title">
                        🧠 Ideas
                    </div>
                    <div class="card-text">
                        Business, study और creative ideas.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:

            st.markdown(
                """
                <div class="card">
                    <div class="card-title">
                        📸 Vision
                    </div>
                    <div class="card-text">
                        Images को समझें और analyze करें।
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # MESSAGE HISTORY
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
    # ATTACH IMAGE
    # --------------------------------------------------------

    attached_image = st.file_uploader(
        "📎 Image attach करें",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        key="chat_attachment",
        label_visibility="collapsed"
    )

    if attached_image:

        st.image(
            Image.open(attached_image),
            width=240,
            caption="Attached image"
        )

    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    voice = st.audio_input(
        "🎙️ Voice message",
        key="diva_voice"
    )

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    prompt = st.chat_input(
        "Diva से कुछ भी पूछें..."
    )

    # --------------------------------------------------------
    # SEND
    # --------------------------------------------------------

    if prompt or voice:

        user_text = (
            prompt
            if prompt
            else "🎙️ Voice message"
        )

        # USER MESSAGE

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

            if attached_image:

                st.image(
                    Image.open(attached_image),
                    width=240
                )

        # ----------------------------------------------------
        # PREPARE INPUT
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

        if attached_image:

            image_bytes = attached_image.getvalue()

            # Keep inline request reasonably small
            if len(image_bytes) <= 15 * 1024 * 1024:

                image_base64 = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                input_data.append(
                    {
                        "type": "image",
                        "data": image_base64,
                        "mime_type": attached_image.type
                    }
                )

            else:

                st.warning(
                    "Image बहुत बड़ी है। "
                    "कृपया 15 MB से छोटी image upload करें।"
                )

        # Voice

        if voice:

            audio_bytes = voice.getvalue()

            if len(audio_bytes) <= 15 * 1024 * 1024:

                audio_base64 = base64.b64encode(
                    audio_bytes
                ).decode("utf-8")

                input_data.append(
                    {
                        "type": "audio",
                        "data": audio_base64,
                        "mime_type": (
                            voice.type
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

            else:

                st.warning(
                    "Audio बहुत बड़ी है। "
                    "कृपया छोटी recording भेजें।"
                )

        if not input_data:

            input_data.append(
                {
                    "type": "text",
                    "text": user_text
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
                        st.session_state.model,

                    "input":
                        input_data,

                    "system_instruction":
                        SYSTEM_INSTRUCTION,

                    # Google Search for fresh information
                    "tools": [
                        {
                            "type": "google_search"
                        }
                    ]
                }

                # Conversation state

                if st.session_state.interaction_id:

                    request[
                        "previous_interaction_id"
                    ] = st.session_state.interaction_id

                # Create interaction

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
                    ""
                )

                if not answer:

                    # Fallback parser

                    collected = []

                    for step in getattr(
                        interaction,
                        "steps",
                        []
                    ):

                        for content in getattr(
                            step,
                            "content",
                            []
                        ):

                            text = getattr(
                                content,
                                "text",
                                None
                            )

                            if text:

                                collected.append(text)

                    answer = "\n".join(
                        collected
                    ).strip()

                if not answer:

                    answer = (
                        "मुझे इस बार कोई text response नहीं मिला। "
                        "कृपया दोबारा कोशिश करें।"
                    )

                st.markdown(answer)

                # Save

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                error_text = str(e)

                if "429" in error_text:

                    st.error(
                        "⏳ API limit पूरी हो गई है। "
                        "थोड़ी देर बाद फिर कोशिश करें।"
                    )

                elif (
                    "401" in error_text
                    or "403" in error_text
                    or "API key" in error_text
                ):

                    st.error(
                        "🔑 Gemini API key में समस्या है। "
                        "अपनी API key check करें।"
                    )

                elif "404" in error_text:

                    st.error(
                        "❌ Model उपलब्ध नहीं है। "
                        "Sidebar से दूसरा model चुनें।"
                    )

                elif "quota" in error_text.lower():

                    st.error(
                        "⏳ Gemini quota समाप्त हो गया है। "
                        "कुछ देर बाद फिर कोशिश करें।"
                    )

                else:

                    st.error(
                        "⚠️ Diva AI Error\n\n"
                        + error_text
                    )

# ============================================================
# PHOTO STUDIO
# ============================================================

with studio_tab:

    st.markdown(
        "## 🎨 Diva Photo Studio"
    )

    st.caption(
        "Background हटाएँ और नया background लगाएँ।"
    )

    photo = st.file_uploader(
        "📸 अपनी photo upload करें",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        key="studio_photo"
    )

    if photo:

        original = Image.open(
            photo
        ).convert("RGBA")

        left, right = st.columns(2)

        with left:

            st.image(
                original,
                caption="Original",
                use_container_width=True
            )

        background = st.selectbox(
            "🎨 Background",
            [
                "Transparent",
                "White",
                "Passport Blue",
                "Light Gray",
                "Black",
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

                    buffer = io.BytesIO()

                    original.save(
                        buffer,
                        format="PNG"
                    )

                    removed = remove(
                        buffer.getvalue()
                    )

                    foreground = Image.open(
                        io.BytesIO(removed)
                    ).convert("RGBA")

                    colors = {

                        "White":
                            (255, 255, 255),

                        "Passport Blue":
                            (20, 50, 120),

                        "Light Gray":
                            (220, 220, 220),

                        "Black":
                            (10, 10, 10),

                        "Pink":
                            (255, 105, 180),

                        "Purple":
                            (110, 70, 180)
                    }

                    if background == "Transparent":

                        final = foreground

                        file_type = "PNG"
                        mime = "image/png"

                    else:

                        new_background = Image.new(
                            "RGBA",
                            foreground.size,
                            colors[background] + (255,)
                        )

                        new_background.paste(
                            foreground,
                            (0, 0),
                            foreground
                        )

                        final = new_background.convert(
                            "RGB"
                        )

                        file_type = "JPEG"
                        mime = "image/jpeg"

                    with right:

                        st.image(
                            final,
                            caption="Final Result",
                            use_container_width=True
                        )

                        output = io.BytesIO()

                        if file_type == "JPEG":

                            final.save(
                                output,
                                format="JPEG",
                                quality=95,
                                optimize=True
                            )

                        else:

                            final.save(
                                output,
                                format="PNG",
                                optimize=True
                            )

                        st.download_button(
                            "📥 Download Photo",
                            data=output.getvalue(),
                            file_name=(
                                "diva_photo."
                                + file_type.lower()
                            ),
                            mime=mime,
                            use_container_width=True
                        )

                except ImportError:

                    st.error(
                        "❌ rembg install नहीं है।\n\n"
                        "Terminal में चलाएँ:\n"
                        "pip install rembg"
                    )

                except Exception as e:

                    st.error(
                        "❌ Photo processing error:\n\n"
                        + str(e)
                    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#666b78;
        font-size:12px;
        margin-top:40px;
    ">
        ✨ Diva AI Pro • Smart • Private • Creative
    </div>
    """,
    unsafe_allow_html=True
)
