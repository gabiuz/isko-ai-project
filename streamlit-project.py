import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize your variables
CLIENT = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
<<<<<<< HEAD
MODEL = 'gemini-2.0-flash'
INSTRUCTIONS = 'You are a friendly chatbot'
=======
MODEL = 'gemini-2.5-flash'
INSTRUCTIONS = """You are a friendly chatbot for Polytechnic University of the Philippines. 
Provide detailed info on admissions, academics, campus life, document requests, and student services.
For document requests, students typically need to fill out a form from the Registrar's Office, submit valid ID, and pay the processing fee. 
If unsure, direct them to https://www.pup.edu.ph/registrar or student services.
Use the Google Search tool to find the latest announcements, news, or events from the official PUP Facebook page or other social media channels when asked about recent updates."""

>>>>>>> 2480bb1 (hehe)
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

<<<<<<< HEAD
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

  # Question tool will use this function to get up to date weather update
  def get_weather(self,location:str):
      """This is a publically available API that returns the weather for a given location."""
      try:
        location = location.replace(' ','+')
        response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=10&language=en&format=json"
        )
        data = response.json()

        latitude, longitude = data["results"][0]["latitude"], data["results"][0]["longitude"]
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )
        data = response.json()
        return data["current"]
      except:
        return "Invalid location"
=======



>>>>>>> 2480bb1 (hehe)

  # Refactor the invoke function to support function result and return in a natural language tone
  def process_user_message(self, user_query):
      # Stream the response
      # With Google Search Grounding, the model handles the search server-side and returns the text directly.
      # We just need to stream the chunks.
      for chunk in self.chat.send_message_stream(user_query):
<<<<<<< HEAD

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
=======
          if chunk.text:
              yield chunk.text
>>>>>>> 2480bb1 (hehe)


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