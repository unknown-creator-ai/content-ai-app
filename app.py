import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import uuid

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Diva AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CSS - FULL SCREEN MODERN UI
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Inter, Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 50% -15%,
            #292044 0%,
            #12131b 38%,
            #08090d 80%
        );
    color: #ffffff;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 100% !important;
    padding: 12px 3vw 100px 3vw !important;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #0e1016;
    border-right: 1px solid #272a35;
}

/* Logo */

.diva-logo {
    font-size: 30px;
    font-weight: 900;
    background: linear-gradient(
        90deg,
        #ff4f9a,
        #a36cff,
        #5bdcff
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.diva-small {
    color: #858b9b;
    font-size: 13px;
}

/* Top bar */

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 4px 14px;
    border-bottom: 1px solid #242732;
    margin-bottom: 10px;
}

.top-title {
    font-size: 20px;
    font-weight: 750;
}

.online {
    color: #55e69a;
    font-size: 13px;
}

/* Welcome */

.welcome {
    min-height: 55vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.welcome-icon {
    font-size: 65px;
}

.welcome-title {
    margin-top: 10px;
    font-size: clamp(36px, 6vw, 64px);
    font-weight: 900;
    background: linear-gradient(
        90deg,
        #ff62a8,
        #a879ff,
        #5bdcff
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-subtitle {
    margin-top: 8px;
    color: #969baa;
    font-size: 16px;
}

/* Feature cards */

.feature {
    background: rgba(25, 27, 36, .75);
    border: 1px solid #2b2e39;
    border-radius: 18px;
    padding: 18px;
    min-height: 110px;
    transition: .2s;
}

.feature:hover {
    border-color: #9a6cff;
    transform: translateY(-2px);
}

.feature-title {
    font-size: 16px;
    font-weight: 750;
}

.feature-text {
    color: #8f95a5;
    font-size: 13px;
    margin-top: 6px;
}

/* Chat */

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

/* Chat input */

[data-testid="stChatInput"] {
    max-width: 900px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stChatInput"] textarea {
    background: #181a22 !important;
    color: #ffffff !important;
    border: 1px solid #363946 !important;
    border-radius: 20px !important;
}

/* Buttons */

.stButton > button {
    border-radius: 13px;
    background: #171920;
    color: #ffffff;
    border: 1px solid #30333d;
}

.stButton > button:hover {
    border-color: #ff579f;
    color: #ff75b1;
}

/* Mobile */

@media(max-width: 700px) {

    .block-container {
        padding: 8px 10px 90px 10px !important;
    }

    .welcome {
        min-height: 48vh;
    }

    .welcome-icon {
        font-size: 48px;
    }

    .welcome-title {
        font-size: 40px;
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

# =========================================================
# API KEY
# =========================================================

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "🔑 GEMINI_API_KEY नहीं मिली।\n\n"
        "Streamlit Secrets में GEMINI_API_KEY डालें।"
    )
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini connection error: {e}")
    st.stop()

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "model" not in st.session_state:
    st.session_state.model = "gemini-3.8-flash"

# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are Diva AI Pro.

You are a highly capable, friendly and intelligent AI assistant.

Language:
- Understand Hindi.
- Understand Hinglish.
- Understand English.
- Reply naturally in the user's language.

Rules:
- Give accurate and useful answers.
- Do not unnecessarily repeat the user's question.
- Simple questions should receive concise answers.
- Complex questions should receive detailed answers.
- Use Markdown when useful.
- Use headings and bullet points when useful.

Coding:
- Provide complete working code.
- Clearly explain where code should be placed.
- Mention required packages when needed.
- Never invent package names or APIs.

Images:
- Analyze uploaded images carefully.
- Only describe things that are actually visible.
- If something cannot be determined, say so.

Important:
- Never claim you performed an action that you cannot perform.
- Be honest about limitations.
"""

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="diva-logo">✨ Diva AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="diva-small">'
        'Your intelligent AI companion'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # New Chat

    if st.button(
        "＋  नई चैट",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.chat_id = str(uuid.uuid4())

        st.rerun()

    st.divider()

    st.markdown("### ⚙️ Settings")

    model = st.selectbox(
        "Model",
        [
            "gemini-3.8-flash"
        ],
        index=0
    )

    st.session_state.model = model

    st.divider()

    st.markdown("### ✨ Features")

    st.caption("● AI Chat")
    st.caption("● Image Understanding")
    st.caption("● Voice Input")
    st.caption("● Google Search")
    st.caption("● Photo Studio")

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

# =========================================================
# TOP BAR
# =========================================================

st.markdown(
    """
    <div class="topbar">

        <div class="top-title">
            ✨ Diva AI
        </div>

        <div class="online">
            ● Online
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TABS
# =========================================================

chat_tab, photo_tab = st.tabs(
    [
        "💬 Chat",
        "🎨 Photo Studio"
    ]
)

# =========================================================
# CHAT
# =========================================================

with chat_tab:

    # -----------------------------------------------------
    # Welcome
    # -----------------------------------------------------

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

                <div class="welcome-subtitle">
                    Ask me anything. I'm here to help.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown(
                """
                <div class="feature">

                    <div class="feature-title">
                        💻 Coding
                    </div>

                    <div class="feature-text">
                        Python, apps, websites और debugging.
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                """
                <div class="feature">

                    <div class="feature-title">
                        🧠 Ideas
                    </div>

                    <div class="feature-text">
                        Study, business और creative ideas.
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:

            st.markdown(
                """
                <div class="feature">

                    <div class="feature-title">
                        📸 Vision
                    </div>

                    <div class="feature-text">
                        Images को समझें और analyze करें।
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # -----------------------------------------------------
    # History
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Image attachment
    # -----------------------------------------------------

    attached_image = st.file_uploader(
        "📎 Image",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="chat_image",
        label_visibility="collapsed"
    )

    if attached_image:

        preview = Image.open(
            attached_image
        )

        st.image(
            preview,
            width=260,
            caption="Attached image"
        )

    # -----------------------------------------------------
    # Voice
    # -----------------------------------------------------

    voice = st.audio_input(
        "🎙️ Voice",
        key="chat_voice"
    )

    # -----------------------------------------------------
    # Chat input
    # -----------------------------------------------------

    prompt = st.chat_input(
        "Diva से कुछ भी पूछें..."
    )

    # -----------------------------------------------------
    # PROCESS
    # -----------------------------------------------------

    if prompt or voice:

        user_text = (
            prompt
            if prompt
            else "🎙️ Voice message"
        )

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

            if attached_image:

                st.image(
                    Image.open(attached_image),
                    width=260
                )

        # -------------------------------------------------
        # Prepare current request
        # -------------------------------------------------

        parts = []

        if prompt:

            parts.append(
                types.Part.from_text(
                    text=prompt
                )
            )

        # Image

        if attached_image:

            image_bytes = attached_image.getvalue()

            parts.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=attached_image.type
                )
            )

        # Voice

        if voice:

            audio_bytes = voice.getvalue()

            parts.append(
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=(
                        voice.type
                        or "audio/wav"
                    )
                )
            )

            parts.append(
                types.Part.from_text(
                    text=(
                        "इस voice message को समझकर "
                        "उपयुक्त उत्तर दें।"
                    )
                )
            )

        if not parts:

            parts.append(
                types.Part.from_text(
                    text=user_text
                )
            )

        # -------------------------------------------------
        # AI
        # -------------------------------------------------

        with st.chat_message(
            "assistant",
            avatar="✨"
        ):

            try:

                # Build previous conversation

                contents = []

                for message in (
                    st.session_state.messages[:-1]
                ):

                    role = (
                        "user"
                        if message["role"] == "user"
                        else "model"
                    )

                    contents.append(
                        types.Content(
                            role=role,
                            parts=[
                                types.Part.from_text(
                                    text=message["content"]
                                )
                            ]
                        )
                    )

                # Current request

                contents.append(
                    types.Content(
                        role="user",
                        parts=parts
                    )
                )

                # Generate

                response = client.models.generate_content(
                    model=st.session_state.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.7,
                        tools=[
                            types.Tool(
                                google_search=types.GoogleSearch()
                            )
                        ]
                    )
                )

                answer = ""

                if response.text:

                    answer = response.text

                if not answer:

                    answer = (
                        "मुझे इस बार कोई उत्तर नहीं मिला। "
                        "कृपया दोबारा कोशिश करें।"
                    )

                st.markdown(answer)

                # Save assistant

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                error = str(e)

                if "404" in error:

                    st.error(
                        "❌ चुना हुआ Gemini model उपलब्ध नहीं है। "
                        "Google AI Studio में उपलब्ध model check करें।"
                    )

                elif "429" in error:

                    st.error(
                        "⏳ Gemini API quota/limit पूरी हो गई है। "
                        "कुछ देर बाद फिर कोशिश करें।"
                    )

                elif (
                    "401" in error
                    or "403" in error
                    or "API key" in error
                ):

                    st.error(
                        "🔑 Gemini API key में समस्या है। "
                        "Streamlit Secrets में key check करें।"
                    )

                else:

                    st.error(
                        "⚠️ Diva AI में समस्या आई:\n\n"
                        + error
                    )

# =========================================================
# PHOTO STUDIO
# =========================================================

with photo_tab:

    st.markdown(
        "## 🎨 Diva Photo Studio"
    )

    st.caption(
        "Photo का background remove करके नया background लगाएँ।"
    )

    photo = st.file_uploader(
        "📸 Photo upload करें",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        key="photo_editor"
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

        bg = st.selectbox(
            "🎨 नया Background",
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
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "Background remove हो रहा है..."
            ):

                try:

                    from rembg import remove

                    buffer = io.BytesIO()

                    original.save(
                        buffer,
                        format="PNG"
                    )

                    result_bytes = remove(
                        buffer.getvalue()
                    )

                    foreground = Image.open(
                        io.BytesIO(result_bytes)
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

                    if bg == "Transparent":

                        final = foreground
                        file_format = "PNG"
                        mime = "image/png"

                    else:

                        background = Image.new(
                            "RGBA",
                            foreground.size,
                            colors[bg] + (255,)
                        )

                        background.paste(
                            foreground,
                            (0, 0),
                            foreground
                        )

                        final = background.convert(
                            "RGB"
                        )

                        file_format = "JPEG"
                        mime = "image/jpeg"

                    with right:

                        st.image(
                            final,
                            caption="Final Result",
                            use_container_width=True
                        )

                        output = io.BytesIO()

                        if file_format == "PNG":

                            final.save(
                                output,
                                format="PNG",
                                optimize=True
                            )

                        else:

                            final.save(
                                output,
                                format="JPEG",
                                quality=95,
                                optimize=True
                            )

                        st.download_button(
                            "📥 Download Photo",
                            data=output.getvalue(),
                            file_name=(
                                "diva_edited."
                                + file_format.lower()
                            ),
                            mime=mime,
                            use_container_width=True
                        )

                except ImportError:

                    st.error(
                        "❌ rembg install नहीं है। "
                        "requirements.txt check करें।"
                    )

                except Exception as e:

                    st.error(
                        "❌ Photo processing error:\n\n"
                        + str(e)
                    )

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#666b78;
        font-size:12px;
        padding:30px 0;
    ">
        ✨ Diva AI • Smart • Creative • Helpful
    </div>
    """,
    unsafe_allow_html=True
)
