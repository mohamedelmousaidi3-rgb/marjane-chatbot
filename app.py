"""A small Streamlit chatbot powered by Groq and a local JSON knowledge file."""

import json
import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# Load GROQ_API_KEY from .env when the app starts.
load_dotenv()


def load_knowledge() -> dict:
    """Read the chatbot's instructions and Academy information."""
    with open("knowledge.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_api_key():
    """Read the local .env key or the secret saved in Streamlit Cloud."""
    return os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")


knowledge = load_knowledge()
company_name = knowledge.get("company", {}).get("name", "Assistant")
assistant_name = knowledge.get("assistant", {}).get("name", f"{company_name} Assistant")

st.set_page_config(page_title=assistant_name, page_icon="💬")
st.title(f"💬 {assistant_name}")
st.caption("سولني على المعلومات الموجودة فـ knowledge.json.")

# Keep this list only for the current browser session.
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()

# Let visitors select a common question without having to type it.
faq_questions = [item["question"] for item in knowledge.get("faq", []) if item.get("question")]
with st.sidebar:
    st.header("أسئلة كتعاود بزاف")
    st.caption("اختار سؤال، والجواب غيكون بالدارجة.")
    selected_faq = st.selectbox(
        "شنو بغيتي تعرف؟",
        faq_questions,
        index=None,
        placeholder="اختار سؤال...",
    )
    if st.button("سول على هاد السؤال", disabled=selected_faq is None):
        st.session_state.pending_prompt = selected_faq

# Show earlier messages before accepting a new one.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# A selected FAQ has priority; otherwise use the text the visitor typed.
prompt = st.session_state.pop("pending_prompt", None) or st.chat_input("كتب السؤال ديالك...")

if prompt:
    # Show and save the user's message.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = get_api_key()
    if not api_key or api_key == "your_groq_api_key_here":
        st.error("Add your Groq API key to the .env file, then restart the app.")
        st.stop()

    # The JSON file supplies the rules, facts, limits, and source links.
    instructions = knowledge.get("system_instructions", [])
    if isinstance(instructions, list):
        instructions = "\n".join(f"- {item}" for item in instructions)

    system_prompt = f"""{instructions}

Assistant profile:
{json.dumps(knowledge.get('assistant', {}), ensure_ascii=False, indent=2)}

Knowledge base (facts, FAQ guidance, limitations, and sources):
{json.dumps(knowledge, ensure_ascii=False, indent=2)}
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.messages)

    try:
        client = Groq(api_key=api_key)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    # A fast Groq model suitable for a simple free-tier chatbot.
                    model="openai/gpt-oss-20b",
                    messages=messages,
                    temperature=0.4,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)

        # Save the answer so it is included in the next request.
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as error:
        # Do not expose a traceback or stop the existing conversation on an API error.
        st.error(f"Sorry, the chatbot could not respond right now: {error}")
