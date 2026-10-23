"""A small Streamlit chatbot powered by Groq and a local JSON knowledge file."""

import json
import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# Load GROQ_API_KEY from .env when the app starts.
load_dotenv()


def load_knowledge() -> dict:
    """Read the chatbot's instructions and knowledge."""
    with open("knowledge.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_api_key():
    """Read the local .env key or the secret saved in Streamlit Cloud."""
    return os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")


def build_system_prompt(knowledge: dict) -> str:
    """Keep useful facts while avoiding an oversized API request."""
    instructions = knowledge.get("system_instructions", [])

    if isinstance(instructions, list):
        instructions = "\n".join(f"- {item}" for item in instructions)

    # The full file has metadata and test cases that are not needed for answers.
    facts = [
        {
            "fact": item.get("fact"),
            "status": item.get("status"),
            "source_ids": item.get("source_ids"),
        }
        for item in knowledge.get("knowledge", [])
    ]

    sources = {
        item.get("id"): item.get("url")
        for item in knowledge.get("sources", [])
        if item.get("id") and item.get("url")
    }

    context = {
        "company": knowledge.get("company", {}),
        "assistant": knowledge.get("assistant", {}),
        "facts": facts,
        "limitations": knowledge.get("limitations", []),
        "official_source_urls": sources,
    }

    return f"""{instructions}

Use this knowledge base:
{json.dumps(context, ensure_ascii=False, indent=2)}
"""


knowledge = load_knowledge()
company_name = knowledge.get("company", {}).get("name", "Assistant")
assistant_name = knowledge.get(
    "assistant", {}
).get("name", f"{company_name} Assistant")

st.set_page_config(page_title=assistant_name, page_icon="💬")
st.title(f"💬 {assistant_name}")
st.caption("سولني على المعلومات الموجودة فـ knowledge.json.")

# Keep messages for the current browser session.
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()

# FAQ section in the sidebar.
faq_questions = [
    item["question"]
    for item in knowledge.get("faq", [])
    if item.get("question")
]

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

# Display earlier messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Use a chosen FAQ or the typed message.
prompt = st.session_state.pop(
    "pending_prompt", None
) or st.chat_input("كتب السؤال ديالك...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = get_api_key()

    if not api_key or api_key == "your_groq_api_key_here":
        st.error("زيد Groq API key فـ Secrets ديال Streamlit أو فـ .env.")
        st.stop()

    system_prompt = build_system_prompt(knowledge)

    messages = [{"role": "system", "content": system_prompt}]

    # Only recent messages are sent to Groq to stay within the free-tier limit.
    messages.extend(st.session_state.messages[-8:])

    try:
        client = Groq(api_key=api_key)

        with st.chat_message("assistant"):
            with st.spinner("كنفكر..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=messages,
                    temperature=0.4,
                )

                answer = response.choices[0].message.content
                st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as error:
        st.error(f"سمح ليا، وقع مشكل: {error}")
