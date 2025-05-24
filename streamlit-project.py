import streamlit as st
from google import genai
from google.genai import types
import time
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
# Initialize your variables
CLIENT = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = 'gemini-2.0-flash'
INSTRUCTIONS = 'You are a friendly chatbot'
TEMPERATURE = 0.25
TOP_P = 0.8
MAX_OUTPUT_TOKENS = 1024

# Setup your tool schema
question_tool = {
    "name": "get_question",
    "description": "Useful when you want to get the question from the user",
    "parameters": {
        "type": "object",
        "properties":{
            "question": {
                "type": "string",
                "description": "Question from the user"
            }
        },
        "required":["question"]
    }
}

# Bind your tools together
tools = types.Tool(functionDeclarations=[question_tool])

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

  # Use to update configuration
  def update_chatbot_setting(self,
                             system_instruction=INSTRUCTIONS,
                             temperature=TEMPERATURE,
                             top_p=TOP_P,
                             max_output_tokens=MAX_OUTPUT_TOKENS):
    history = self.chat.get_history()
    new_config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction=system_instruction,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens
    )
    self.chat = CLIENT.chats.create(
        model=MODEL,
        history=history,
        config=new_config
    )

  # Weather tool will use this function to get up to date weather update
  def get_question(self,question:str):
      """Scrape data from PUP site"""
      try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MyChatBot/1.0; +https://yourdomain.com)"
        }
        response = requests.get(
            "https://www.pup.edu.ph/"
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')


        headlines = soup.find_all('div', class_='news')  # adjust class based on real site
        extracted = [item.get_text(strip=True) for item in headlines]

        return extracted or "No relevant info found."
      except Exception as e:
        return f"Error fetching data: {e}"

  # Refactor the invoke function to support function result and return in a natural language tone
  def process_user_message(self, user_query):

      # Call send_message (as a stream)
      for chunk in self.chat.send_message_stream(user_query):

          # Check if the model calls the function
          if chunk.candidates[0].content.parts[0].function_call:

              # Set the variable
              function_call = chunk.candidates[0].content.parts[0].function_call
              function_name = function_call.name
              function_args = function_call.args

              # Good practice: If you provide multiple tools, make a logic that routes them
              if function_name == 'get_weather':
                 function_result = self.get_weather(**function_args)


              # Parse the response like this
              function_response_part = types.Part(
                  function_response=types.FunctionResponse(
                      name=function_name,
                      response=function_result
                  )
              )

              # Using the result, send the message once again to create a natural language response. Slightly tweak the config to not use another tool to reduce redundancy
              for response_chunk in self.chat.send_message_stream(
                  message=[function_response_part],
                  config=types.GenerateContentConfig(
                  system_instruction=INSTRUCTIONS,      # Ideally, you have a different instructions here, but lets use the default one
                  temperature=TEMPERATURE,
                  top_p=TOP_P,
                  max_output_tokens=MAX_OUTPUT_TOKENS
                )
              ):

                  # Final check. Response in chunk of text
                  if hasattr(response_chunk, 'text'):
                      yield response_chunk.text

          # If the model didn't use the tool, Response in chunk of text (default response)
          else:
              if hasattr(chunk, 'text'):
                  yield chunk.text


if 'chat_session' not in st.session_state:
      # Save session state for history
      st.session_state.chat_session = ChatBot()

# For streamlit chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []


# Build your own chatbot
st.title('Goodmorning, iskolar!')
st.write("Get instant answers about admissions, academics, campus life, and more at Polytechnic University of the Philippines. Available 24/7 to help you succeed. ")

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

with st.sidebar:
    st.title('Settings')
    st.divider()

    instructions = st.text_input('Instructions',INSTRUCTIONS)
    temperature = st.slider('Temperature',0.0,2.0,TEMPERATURE,0.01)
    top_p = st.slider('Top P',0.0,1.0,TOP_P,0.01)
    max_output_tokens = st.slider('Max Output Tokens',-1,1024,MAX_OUTPUT_TOKENS,1)

    if st.button('Update Setting'):
      try:
        st.session_state.chat_session.update_chatbot_setting(
            system_instruction=instructions,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens
        )
        st.success('Setting Updated!')
      except Exception as e:
        st.error(f'Error: {e}')


if prompt := st.chat_input('Ask me anything!'):

    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('assistant'):
        with st.spinner('Thinking...'):
          response = st.write_stream(st.session_state.chat_session.process_user_message(prompt))      # The function is called here using our new and improved send message function

    st.session_state.messages.append({'role': 'assistant', 'content': response})