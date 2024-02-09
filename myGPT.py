# DO NOT RENAME OR MOVE THIS FILE. 
# Must update GitHub action workflow and documentation in README if you do.

import streamlit as st
import requests
import json

text_input_key = "user_input"

# Function to send requests to your GPT model
def query_mygpt(chat):

    lambda_url = "https://5faukxw75uazcs2zdl4zbvyg2e0lebie.lambda-url.us-west-1.on.aws/"
    # print("Please wait while GPT is done ...")
    headers = {'Content-Type': 'application/json'}
    r = requests.post(headers=headers, url=lambda_url, json=json.dumps(chat))
    new_chat = json.loads(r.content.decode('utf-8'))
    
    st.session_state['number_of_trials'] -= 1
    
    return new_chat

# Function to handle sending the message
def send_message():
    
    st.session_state['chat'].append({'role': 'user', 'content': user_input})
    st.session_state['chat'] = query_mygpt(st.session_state['chat'])
    
    st.session_state[text_input_key] = ''
    
    st.session_state['input_text'] = ''
    

def show_with_background_color(some_text):
    """
    Not used anymore. The ideas was to have custom background color,
    but it is easier to just have chatbot reply in gray color,
    that way it works on both dark and light mode. 
    """

    st.markdown("""
        <style>
        .content {
            background-color: #f0f0f0;  /* Light gray background */
            padding: 10px;             /* Padding around the text */
        }
        </style>
        """, unsafe_allow_html=True)
    # Display the content with custom style
    st.markdown(f'<div class="content">{some_text}</div>', unsafe_allow_html=True)

    

if 'first time' not in st.session_state:
    st.session_state['number_of_trials'] = 3
    st.session_state['first time'] = False
    st.session_state['input_text'] = ''
    st.session_state['chat'] = [
    {'role': 'system', 'content': 'You are a software engineer'}
    ]
# Streamlit app layout
st.title("MyGPT Demo")

st.info(f"Welcome to MyGPT, a simple OpenAI ChatGPT-3 based chatbot (soon GPT-4). No chats are stored. Responses are limited to about 300 words. ")

for i in range(1, len(st.session_state['chat'] ), 2):
    # writes previous question
    question = st.session_state['chat'][i]['content']
    a1 = st.write(question)
    # writes previous answer
    answer = st.session_state['chat'][i+1]['content']
    a2 = st.markdown(f'<div style="color: gray;">{answer}</div>', unsafe_allow_html=True)
    st.text("\n" * 10) 
    
    
if st.session_state['number_of_trials'] > 0:

    # Using columns to organize the layout
    col1, col2 = st.columns([4, 1]) 
    # 'content': 'What is most popular programming language today?'}]

    with col1:
        user_input = st.text_input(label="user input", value="", key=text_input_key, placeholder="Enter a question", label_visibility="collapsed")

    # Send button in the second column
    with col2:
        send_button = st.button("Send", on_click=send_message)
        
    # "debug", st.session_state['chat']
else:
    st.info(f"This demo allows only 3 API calls. Thanks for trying it out. No chats are stored.")
