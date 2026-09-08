import streamlit as st
from google import genai
from PIL import Image
import io
import base64

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Diva AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS — FULL SCREEN GEMINI / CHATGPT STYLE
# ============================================================

st.markdown("""
<style>

/* ================= APP ================= */

.stApp {
    background: #0b0d12;
    color: #f5f5f5;
}

/* Remove top empty space */

.block-container {
    max-width: 1500px !important;
    padding-top: 1rem !important;
    padding-bottom: 5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: #111318;
    border-right: 1px solid #272a31;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

/* Sidebar buttons */

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 12px;
    background: transparent;
    border: 1px solid transparent;
    color: #e5e7eb;
    text-align: left;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1c1f26;
    border-color: #30343d;
}

/* ================= LOGO ================= */

.diva-logo {
    font-size: 27px;
    font-weight: 800;
    padding: 5px 0 18px 0;
    background: linear-gradient(
        90deg,
        #ff4f9a,
        #9b6cff,
        #4cc9f0
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ================= HEADER ================= */

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 5px 18px 5px;
    border-bottom: 1px solid #20232b;
    margin-bottom: 15px;
}

.top-title {
    font-size: 20px;
    font-weight: 700;
}

.online {
    color: #55e69b;
    font-size: 13px;
}

/* ================= WELCOME ================= */

.welcome {
    text-align: center;
    padding-top: 13vh;
}

.welcome-logo {
    font-size: 60px;
    margin-bottom: 10px;
}

.welcome-title {
    font-size: 40px;
    font-weight: 800;
    background: linear-gradient(
        90deg,
        #ff4f9a,
        #a36cff,
        #4cc9f0
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-subtitle {
    color: #8d94a3;
    font-size: 16px;
    margin-top: 10px;
}

/* ================= SUGGESTIONS ================= */

.suggestion {
    background: #15181e;
    border: 1px solid #292d35;
    border-radius: 15px;
    padding: 16px;
    color: #d5d8de;
    min-height: 85px;
}

.suggestion:hover {
    border-color: #ff4f9a;
}

/* ================= CHAT ================= */

[data-testid="stChatMessage"] {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    border-radius: 18px;
    padding: 8px 12px;
}

[data-testid="stChatMessageContent"] {
    font-size: 16px;
    line-height: 1.65;
}

/* ================= INPUT ================= */

[data-testid="stChatInput"] {
    max-width: 950px;
    margin-left: auto;
    margin-right: auto;
}

[data-testid="stChatInput"] textarea {
    background: #181b22 !important;
    color: white !important;
    border: 1px solid #30343d !important;
    border-radius: 18px !important;
}

/* ================= BUTTONS ================= */

.stButton > button {
    border-radius: 12px;
    background: #171a21;
    color: white;
    border: 1px solid #2c3038;
}

.stButton > button:hover {
    border-color: #ff4f9a;
    color: #ff72ad;
}

/* ================= TABS ================= */

.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #15181e;
    border-radius: 10px;
    padding: 8px 15px;
}

/* ================= MOBILE ================= */

@media (max-width: 700px) {

    .block-container {
        padding-left: 0.7rem !important;
        padding-right: 0.7rem !important;
    }

    .welcome {
        padding-top: 8vh;
    }

    .welcome-title {
        font-size: 32px;
    }

    .welcome-logo {
        font-size: 45px;
    }

    [data-testid="stChatMessage"] {
        padding: 5px;
    }
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# GEMINI
# ============================================================

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY नहीं मिली। "
        "`.streamlit/secrets.toml` check करें।"
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

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "नई चैट"

if "model" not in st.session_state:
    st.session_state.model = "gemini-3.6-flash"

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Diva AI Pro.

You are a highly intelligent, friendly and helpful AI assistant.

You understand Hindi, Hinglish and English.

Always answer in the language the user uses.

For simple questions, be concise.

For complex questions, give structured and detailed answers.

For coding questions:
- Give complete working code.
- Explain where to put the code.
- Mention required packages when necessary.

Use Markdown, headings, lists and code blocks when useful.

Never claim that you performed an action you cannot actually perform.
"""

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="diva-logo">✨ Diva AI</div>',
        unsafe_allow_html=True
    )

    # New chat
    if st.button(
        "＋  नई चैट",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.interaction_id = None
        st.session_state.chat_title = "नई चैट"

        st.rerun()

    st.divider()

    st.markdown("### 💬 चैट")

    if st.session_state.messages:

        # Show current chat
        first_user_message = next(
            (
                x["content"]
                for x in st.session_state.messages
                if x["role"] == "user"
            ),
            "नई चैट"
        )

        title = first_user_message[:35]

        if len(first_user_message) > 35:
            title += "..."

        st.button(
            f"💬 {title}",
            use_container_width=True
        )

    else:

        st.caption("अभी कोई conversation नहीं है।")

    st.divider()

    st.markdown("### ⚙️ Settings")

    model = st.selectbox(
        "Model",
        [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.7-flash"
        ]
    )

    st.session_state.model = model

    st.divider()

    st.caption("✨ Diva AI Pro")
    st.caption("Smart • Fast • Creative")

# ============================================================
# TOP BAR
# ============================================================

st.markdown(
    """
    <div class="topbar">
        <div class="top-title">Diva AI</div>
        <div class="online">● Online</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# MAIN TABS
# ============================================================

chat_tab, photo_tab = st.tabs(
    [
        "💬 Chat",
        "🎨 Photo Studio"
    ]
)

# ============================================================
# CHAT
# ============================================================

with chat_tab:

    # ========================================================
    # WELCOME
    # ========================================================

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome">

                <div class="welcome-logo">
                    ✨
                </div>

                <div class="welcome-title">
                    Hello, I'm Diva
                </div>

                <div class="welcome-subtitle">
                    आपका AI assistant — पूछिए कुछ भी।
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(
                """
                <div class="suggestion">
                💻<br>
                <b>कोड लिखो</b><br>
                <small>Python app बनाओ</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                """
                <div class="suggestion">
                🧠<br>
                <b>Ideas दो</b><br>
                <small>Business ideas बताओ</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                """
                <div class="suggestion">
                📸<br>
                <b>Image समझो</b><br>
                <small>Photo analyze करो</small>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ========================================================
    # HISTORY
    # ========================================================

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

    # ========================================================
    # ATTACHMENT AREA
    # ========================================================

    attach_col, voice_col = st.columns(
        [3, 1]
    )

    with attach_col:

        uploaded_image = st.file_uploader(
            "📎 Image",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            label_visibility="collapsed",
            key="chat_image"
        )

    with voice_col:

        voice_file = st.audio_input(
            "🎙️ Voice",
            key="voice_input"
        )

    # ========================================================
    # PREVIEW
    # ========================================================

    if uploaded_image:

        preview = Image.open(
            uploaded_image
        )

        st.image(
            preview,
            width=260,
            caption="Attached image"
        )

    # ========================================================
    # CHAT INPUT
    # ========================================================

    prompt = st.chat_input(
        "Diva से कुछ भी पूछें..."
    )

    # ========================================================
    # PROCESS
    # ========================================================

    if prompt or voice_file:

        user_text = (
            prompt
            if prompt
            else "🎙️ Voice message"
        )

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

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

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        # ----------------------------------------------------
        # INPUT DATA
        # ----------------------------------------------------

        input_data = []

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

            image_b64 = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            input_data.append(
                {
                    "type": "image",
                    "data": image_b64,
                    "mime_type": uploaded_image.type
                }
            )

        # Voice
        if voice_file:

            audio_bytes = voice_file.getvalue()

            audio_b64 = base64.b64encode(
                audio_bytes
            ).decode("utf-8")

            input_data.append(
                {
                    "type": "audio",
                    "data": audio_b64,
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

        if not input_data:

            input_data.append(
                {
                    "type": "text",
                    "text": user_text
                }
            )

        # ----------------------------------------------------
        # AI
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
                        SYSTEM_PROMPT
                }

                # Conversation memory
                if st.session_state.interaction_id:

                    request[
                        "previous_interaction_id"
                    ] = st.session_state.interaction_id

                # Create interaction
                interaction = client.interactions.create(
                    **request
                )

                # Save interaction
                if getattr(
                    interaction,
                    "id",
                    None
                ):

                    st.session_state.interaction_id = (
                        interaction.id
                    )

                # Response
                answer = getattr(
                    interaction,
                    "output_text",
                    None
                )

                if not answer:

                    answer = ""

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

                            if getattr(
                                content,
                                "type",
                                ""
                            ) == "text":

                                answer += (
                                    content.text
                                )

                if not answer:

                    answer = (
                        "मुझे कोई उत्तर नहीं मिला। "
                        "कृपया दोबारा पूछें।"
                    )

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                error = str(e)

                if "429" in error:

                    st.error(
                        "⏳ API limit पूरी हो गई है। "
                        "थोड़ी देर बाद कोशिश करें।"
                    )

                elif (
                    "401" in error
                    or "403" in error
                    or "API key" in error
                ):

                    st.error(
                        "🔑 Gemini API key गलत है "
                        "या access नहीं मिला।"
                    )

                elif "404" in error:

                    st.error(
                        "❌ चुना हुआ model उपलब्ध नहीं है। "
                        "दूसरा model चुनकर देखें।"
                    )

                else:

                    st.error(
                        "⚠️ Error:\n\n"
                        + error
                    )

# ============================================================
# PHOTO STUDIO
# ============================================================

with photo_tab:

    st.subheader("🎨 Diva Photo Studio")

    st.caption(
        "Background हटाएँ और नया background लगाएँ।"
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

        background_choice = st.selectbox(
            "🎨 Background चुनें",
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
            "✨ Background Remove & Change",
            type="primary",
            use_container_width=True
        ):

            try:

                from rembg import remove

                buffer = io.BytesIO()

                original.save(
                    buffer,
                    format="PNG"
                )

                result = remove(
                    buffer.getvalue()
                )

                foreground = Image.open(
                    io.BytesIO(result)
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

                if background_choice == "Transparent":

                    final = foreground

                    fmt = "PNG"
                    mime = "image/png"

                else:

                    bg = Image.new(
                        "RGBA",
                        foreground.size,
                        colors[
                            background_choice
                        ] + (255,)
                    )

                    bg.paste(
                        foreground,
                        (0, 0),
                        foreground
                    )

                    final = bg.convert(
                        "RGB"
                    )

                    fmt = "JPEG"
                    mime = "image/jpeg"

                with right:

                    st.image(
                        final,
                        caption="Final",
                        use_container_width=True
                    )

                    output = io.BytesIO()

                    final.save(
                        output,
                        format=fmt,
                        quality=95
                    )

                    st.download_button(
                        "📥 Download",
                        output.getvalue(),
                        file_name=(
                            "diva_photo."
                            + fmt.lower()
                        ),
                        mime=mime,
                        use_container_width=True
                    )

            except Exception as e:

                st.error(
                    f"Photo processing error: {e}"
                )
