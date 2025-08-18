import streamlit as st
import requests
from googletrans import Translator

# --- Config ---
UNHCR_LOGO = "https://www.unhcr.org/themes/custom/project/logo.svg"
GROQ_API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"
DOVE_EMOJI = "🕊️"

# Translator
translator = Translator()

# --- Page setup ---
st.set_page_config(page_title="Ombuds AI Support Assistant", layout="centered", page_icon=DOVE_EMOJI)

# --- Sidebar ---
st.sidebar.image(UNHCR_LOGO, use_container_width=True)

# Your trusted guide for:
# - Asylum paperwork 📄
# - Local services 📍
# - Emotional support 💖
st.sidebar.markdown("""
### 🌍 Ombudsman and Mediator AI Support Assistant
           
Your neutral guide for:
- Conflict resolution ⚖️
- Workplace fairness 🏢
- Support and guidance 💬

[Visit UNHCR Website →](https://www.unhcr.org/)
                    
[Visit Office of Ombudsman and Mediator →](https://intranet.unhcr.org/en/about/office-of-the-ombudsman.html)
""")

# --- Language Picker ---
language_options = {
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Ukrainian": "uk",
    "Pashto": "ps",
    "Dari": "fa"
}
selected_language = st.selectbox("Select your preferred language:", list(language_options.keys()))
target_lang = language_options[selected_language]

# --- Title ---
# <p style='text-align: center;'>Welcome! I'm here to support you with asylum help, local services, and a listening ear.</p> ---
st.markdown("""
<h1 style='text-align: center; color: #005baa;'>🌟 Ombuds Support Assistant</h1>

<p style='text-align: center;'>Welcome! I'm here to help prevent, reduce, and resolve workplace grievances within the UNHCR community.</p>

""", unsafe_allow_html=True)

# --- Initialize chat history ---
# UNHCR AI Assistant
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "system", "content": "You are a compassionate UNHCR support assistant named Yiyang. Offer helpful, kind and clear information about asylum, services, and emotional support."}
#     ]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a neutral and compassionate assistant for the Ombudsman and Mediator Office of UNHCR. Your goal is to provide clear, impartial, and helpful guidance on conflict resolution, workplace fairness, and support."}
    ]

# --- Quick Questions ---
# quick_questions = {
#     "🏠 Where can I find shelter?": "Where can I find shelter?",
#     "📝 How to apply for asylum?": "How to apply for asylum?",
#     "🍽️ Where can I get food and water?": "Where can I get food and water?",
#     "⚕️ Where can I get medical help?": "Where can I get medical help?",
#     "📞 Who can I talk to for support?": "Who can I talk to for support?"
# }

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

# --- Display chat history ---
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# --- Chat Input ---
user_input = st.chat_input("How can I help you today?")

# Use quick question if available
if "prompt" in st.session_state:
    prompt = st.session_state.prompt
    del st.session_state["prompt"]
elif user_input:
    prompt = user_input
else:
    prompt = None

# --- Handle Response ---
if prompt:
    translated_input = translator.translate(prompt, dest="en").text
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }, json={
                "model": MODEL,
                "messages": st.session_state.messages
            })
            result = response.json()
            if "choices" in result:
                reply = result["choices"][0]["message"]["content"]
                translated_reply = translator.translate(reply, dest=target_lang).text
                st.session_state.messages.append({"role": "assistant", "content": translated_reply})
                st.chat_message("assistant").markdown(translated_reply)
            else:
                st.error("Something went wrong. Please try again later.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
