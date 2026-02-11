import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize your variables
CLIENT = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = 'gemini-2.5-flash'
INSTRUCTIONS = """You are a friendly chatbot for Polytechnic University of the Philippines. 
Provide detailed info on admissions, academics, campus life, document requests, and student services.
For document requests, students typically need to fill out a form from the Registrar's Office, submit valid ID, and pay the processing fee. 
If unsure, direct them to https://www.pup.edu.ph/registrar or student services.
Use the Google Search tool to find the latest announcements, news, or events from the official PUP Facebook page or other social media channels when asked about recent updates."""

TEMPERATURE = 0.25
TOP_P = 0.8
MAX_OUTPUT_TOKENS = 1024

# Bind your tools together
tools = types.Tool(
    google_search_retrieval=types.GoogleSearchRetrieval()
)

class ChatBot:
  def __init__(self):
    self.chat = CLIENT.chats.create(
        model=MODEL,
        history=[],
        config=types.GenerateContentConfig(
          tools=[tools],
          system_instruction=INSTRUCTIONS,
          temperature=TEMPERATURE,
          top_p=TOP_P,
          max_output_tokens=MAX_OUTPUT_TOKENS
        )
    )





  # Refactor the invoke function to support function result and return in a natural language tone
  def process_user_message(self, user_query):
      # Stream the response
      # With Google Search Grounding, the model handles the search server-side and returns the text directly.
      # We just need to stream the chunks.
      for chunk in self.chat.send_message_stream(user_query):
          if chunk.text:
              yield chunk.text


if 'chat_session' not in st.session_state:
      # Save session state for history
      st.session_state.chat_session = ChatBot()

# For streamlit chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []


# Build your own chatbot
st.title('Good morning, Iskolar!')
st.write("Get instant answers about admissions, academics, campus life, and more at Polytechnic University of the Philippines. Available 24/7 to help you succeed.")

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])




if prompt := st.chat_input('Ask me anything!'):

    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('assistant'):
        with st.spinner('Thinking...'):
            # Collect the full response to store in history
            full_response = ""
            response_container = st.empty()
            
            # Stream the response
            for chunk in st.session_state.chat_session.process_user_message(prompt):
                full_response += chunk
                response_container.markdown(full_response + "▌")
            
            response_container.markdown(full_response)

    st.session_state.messages.append({'role': 'assistant', 'content': full_response})