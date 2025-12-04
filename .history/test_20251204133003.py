import streamlit as st
from deep_translator import GoogleTranslator
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# ----------------------------
# Load API Key
# ----------------------------
load_dotenv('.env.txt')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="Ombuds AI Support Assistant", layout="centered", page_icon="🕊️")

UNHCR_LOGO = "https://www.unhcr.org/themes/custom/project/logo.svg"

# ----------------------------
# Language Translator
# ----------------------------
def translate(text, target_lang):
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except:
        return text  # fallback

language_options = {
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh",
    "Ukrainian": "uk"
}

selected_language = st.selectbox("Select your preferred language:", list(language_options.keys()))
target_lang = language_options[selected_language]

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.image(UNHCR_LOGO, use_container_width=True)
st.sidebar.markdown("""
### 🌍 Ombudsman and Mediator
Your neutral guide for:
- Conflict resolution ⚖️  
- Workplace fairness 🏢  
- Support and guidance 💬  
""")

# ----------------------------
# Header
# ----------------------------
st.markdown("""
<h1 style='text-align:center;color:#005baa;'>🌟 Ombuds AI Support Assistant</h1>
<p style='text-align:center;'>Welcome! I'm here to help prevent, reduce, and resolve workplace grievances within the UNHCR community.</p>
""", unsafe_allow_html=True)

st.markdown(
    """
    <iframe width="100%" height="315"
    src="https://www.youtube.com/embed/n0jQjX3WMNA"
    frameborder="0"
    allowfullscreen></iframe>
    """,
    unsafe_allow_html=True,
)


# ----------------------------
# Initialize Chat History
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a neutral and compassionate assistant named Yiyang for the "
                "Ombudsman and Mediator Office of UNHCR. Your goal is to provide clear, "
                "impartial, and helpful guidance on conflict resolution, workplace fairness, "
                "and emotional support."
            )
        }
    ]

# ----------------------------
# Quick Questions
# ----------------------------
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

# ----------------------------
# Display Chat History
# ----------------------------
for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).markdown(msg["content"])

# ----------------------------
# User Input
# ----------------------------
user_input = st.chat_input("How can I help you today?")

if "prompt" in st.session_state:
    prompt = st.session_state.prompt
    del st.session_state["prompt"]
elif user_input:
    prompt = user_input
else:
    prompt = None

# ----------------------------
# Convert Chat History → Prompt
# ----------------------------
def convert_history_to_prompt(messages):
    system_instruction = None
    dialogue = ""

    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
        elif msg["role"] == "user":
            dialogue += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            dialogue += f"Assistant: {msg['content']}\n"

    return system_instruction, dialogue

# ----------------------------
# Chat Generation with Gemini
# ----------------------------
if prompt:
    translated_input = translate(prompt, "en")

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        full_reply = ""

        try:
            system_instruction, history_prompt = convert_history_to_prompt(st.session_state.messages)

            # Gemini request
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(system_instruction=system_instruction),
                contents=[history_prompt]  # MUST be a string, not dict/list
            )

            for chunk in response_stream:
                if chunk.text:
                    full_reply += chunk.text
                    msg_placeholder.markdown(full_reply)

            translated_reply = translate(full_reply, target_lang)

            st.session_state.messages.append({"role": "assistant", "content": translated_reply})
            msg_placeholder.markdown(translated_reply)

        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
