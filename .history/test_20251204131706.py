import streamlit as st
# from googletrans import Translator
from dotenv import load_dotenv
from google import genai
from google.genai import types
from deep_translator import GoogleTranslator
import os


# Load environment variables
load_dotenv('.env.txt')

# ---- Gemini API ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")

client = genai.Client(api_key=GEMINI_API_KEY)

# --- Config ---
UNHCR_LOGO = "https://www.unhcr.org/themes/custom/project/logo.svg"
Ombudsman_LOGO = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSOqrrJNAbVD9KNBvf_C1nh7TVlUHhw8wZxdbFsGrv1moBnaaIbifNsXsEXlDbFXL9ANbI&usqp=CAU"
DOVE_EMOJI = "🕊️"

# Translator
translator = GoogleTranslator()

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Ombuds AI Support Assistant", layout="centered", page_icon=DOVE_EMOJI)
st.sidebar.image(UNHCR_LOGO, use_container_width=True)

st.sidebar.markdown("""
### 🌍 Ombudsman and Mediator
Your neutral guide for:
- Conflict resolution ⚖️
- Workplace fairness 🏢
- Support and guidance 💬
""")

# --- Language Picker ---
language_options = {
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Ukrainian": "uk",
    "Chinese": "zh"
}
selected_language = st.selectbox("Select your preferred language:", list(language_options.keys()))
target_lang = language_options[selected_language]

# --- Title ---
st.markdown("""
<h1 style='text-align: center; color: #005baa;'>🌟 Ombuds AI Support Assistant</h1>
<p style='text-align: center;'>Welcome! I'm here to help prevent, reduce, and resolve workplace grievances within the UNHCR community.</p>
""", unsafe_allow_html=True)

# --- Video ---
st.video("https://youtu.be/n0jQjX3WMNA")

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a neutral and compassionate assistant named Yiyang for the "
                "Ombudsman and Mediator Office of UNHCR. Your goal is to provide clear, "
                "impartial, and helpful guidance on conflict resolution, workplace fairness, "
                "and support."
            )
        }
    ]

# --- Quick Questions ---
quick_questions = {
    "⚖️ How can I resolve a workplace conflict?": "How can I resolve a workplace conflict?",
    "📝 What is the process for filing a grievance?": "What is the process for filing a grievance?",
    "🤝 How can I mediate a disagreement?": "How can I mediate a disagreement?",
    "📞 How can I access Ombudsman services?": "How can I access Ombudsman services?",
    "💬 How do I receive emotional support at work?": "How do I receive emotional support at work?"
}

st.markdown("**Quick Questions:**")
cols = st.columns(len(quick_questions))
for i, (label, value) in enumerate(quick_questions.items()):
    if cols[i].button(label):
        st.session_state.prompt = value

# --- Display Chat History ---
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# --- Chat Input ---
user_input = st.chat_input("How can I help you today?")

if "prompt" in st.session_state:
    prompt = st.session_state.prompt
    del st.session_state["prompt"]
elif user_input:
    prompt = user_input
else:
    prompt = None

# Convert message history into Gemini-compatible format
def convert_messages_for_gemini(history):
    """
    Convert messages into the list of "contents" expected by Gemini API.
    """
    contents = []
    system_instruction = None

    for msg in history:
        if msg["role"] == "system":
            system_instruction = msg["content"]
        else:
            contents.append({"role": msg["role"], "parts": [msg["content"]]})

    return system_instruction, contents

# --- Chat Completion with Streaming ---
if prompt:
    #translated_input = translator.translate(prompt, dest="en").text
    translated_input = GoogleTranslator(source='auto', target='en').translate(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()  
        full_reply = ""

        try:
            # Prepare messages for Gemini
            system_instruction, contents = convert_messages_for_gemini(st.session_state.messages)

            # Send streaming request
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                ),
                contents=contents,
            )

            # Read stream chunks
            for chunk in response_stream:
                if chunk.text:
                    full_reply += chunk.text
                    msg_placeholder.markdown(full_reply)

            #translated_reply = translator.translate(full_reply, dest=target_lang).text
            translated_reply = GoogleTranslator(source='auto', target=target_lang).translate(full_reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": translated_reply}
            )

            msg_placeholder.markdown(translated_reply)

        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
