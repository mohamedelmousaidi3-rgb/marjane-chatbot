# Marjane Knowledge Chatbot

A simple Streamlit chatbot that answers questions with Groq and information stored in `knowledge.json`. The included knowledge base answers in Moroccan Darija and remembers the conversation while the current Streamlit session is open.

## What you need

- Python 3.9 or newer
- A free Groq API key from [Groq Console](https://console.groq.com/keys)

## Installation

1. Open a terminal in this project folder.
2. Create and activate a virtual environment (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the libraries:

   ```powershell
   pip install -r requirements.txt
   ```

## Configure the API key

1. Create a Groq API key at [Groq Console](https://console.groq.com/keys).
2. Open `.env` and replace `your_groq_api_key_here` with your key:

   ```env
   GROQ_API_KEY=your_real_key_goes_here
   ```

`.env` is listed in `.gitignore`, so your key will not be committed to Git.

## Deploy on Streamlit Community Cloud

Keep `.env` on your computer; never upload it to GitHub. During deployment, add this in **Advanced settings → Secrets**:

```toml
GROQ_API_KEY = "your_real_key_goes_here"
```

The app can read the secret securely after deployment.

## Run the app

```powershell
streamlit run app.py
```

Streamlit will open the chatbot in your browser.

## Customize the chatbot

Edit `knowledge.json` to change the chatbot's personality, rules, language, or source-backed information. Restart the app after changing it.

## How it works

- `st.chat_message()` displays each message.
- `st.chat_input()` collects the next question.
- The sidebar includes a selectable FAQ list for common questions.
- `st.session_state.messages` stores the current conversation in memory. The
  eight latest messages are sent to the model to keep requests within the
  free-tier token limit.
- The **Clear conversation** button starts a fresh conversation.
- The app uses Groq's `openai/gpt-oss-20b` model and displays a friendly error if the API is unavailable.
