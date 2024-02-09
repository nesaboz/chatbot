
"""
DO NOT RENAME OR MOVE THIS FILE. 
Must update GitHub action workflow and documentation in README if you do.

The key variable below st.session_state['chat'], or simply chat, which is list of dictionaries with keys 'role' and 'content'. 
First item is system role, then 2N pairs of question and answers.
"""

import streamlit as st
import requests
import json

TEXT_INPUT_KEY = "user_input"

# Function to send requests to your GPT model
def send_message(question):
    """
    Tries to send a chat to lambda f-on (where question is added to a chat first). 
    If error occurs, reverts back to the old chat history and leave the question in the text input.

    Args:
        question (str): user's question
    """
    
    old_chat = st.session_state['chat']
    
    try:
        lambda_url = "https://5faukxw75uazcs2zdl4zbvyg2e0lebie.lambda-url.us-west-1.on.aws/"
        headers = {'Content-Type': 'application/json'}
        possible_new_chat = old_chat.copy()
        possible_new_chat.append({'role': 'user', 'content': question})
        # # for testing only, throwing an error on the second trial
        # if st.session_state['number_of_trials'] == 2:
        #     raise Exception("This is a test error")
        
        r = requests.post(headers=headers, url=lambda_url, json=json.dumps(possible_new_chat))
        new_chat = json.loads(r.content.decode('utf-8'))
            
        # catches some weird error in case last response was not from the assistant or system
        if new_chat[-1]['role'] in ['assistant', 'system']:
            st.session_state['number_of_trials'] -= 1
            st.session_state['error'] = None
        else:
            raise Exception("The last message was not from the assistant or system.")
        
        # stores new chat, removes the old input
        st.session_state['chat'] = new_chat
        st.session_state[TEXT_INPUT_KEY] = ''
        
    except Exception as e:
        st.session_state['error'] = e
        # will have to show the same chat old again and will leave old input as is
        st.session_state['chat'] = old_chat


def show_previous_q_and_a():
    """
    Show all previous Q&A
    """
    # filter out all system roles
    
    temp_chat = st.session_state['chat'].copy()
    temp_chat = [x for x in temp_chat if x['role'] in ['user', 'assistant']]
    
    for i in range(0, len(temp_chat), 2):
        question = temp_chat[i]['content']
        answer = temp_chat[i+1]['content']
        
        st.write(question)
        st.markdown(f'<div style="color: gray;">{answer}</div>', unsafe_allow_html=True) 
        st.text("\n" * 10)
        
        
def show_input_prompt_and_send_button():
    """
    Show a new input prompt and a send button.
    """

    if st.session_state['number_of_trials'] > 0:
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                label="user input",
                key=TEXT_INPUT_KEY, 
                placeholder="Ask why did the chicken cross the road or anything else ...", 
                label_visibility="collapsed"
                )
        with col2:
            st.button("Send", on_click=send_message, args=(user_input,))
        
    else:
        st.info(f"This demo allows only 3 API calls. Thanks for trying it out. No chats are stored.")


def assign_role():
    st.session_state['chat'].append({'role': 'system', 'content': f"You are now a {st.session_state['assistant_choice']} and no one else, do not give any other response other than role assigned to you."})


def assign_question():
    st.session_state[TEXT_INPUT_KEY] = st.session_state['question_choice']


if __name__ == "__main__":

    st.title("MyGPT Demo")

    st.info("""
            Welcome to MyGPT, a simple OpenAI ChatGPT-3 based chatbot (for time being). Please note:
            - no chats are stored,
            - responses are limited to about 300 words and 3 API calls per session,  
            - please allow up to 10 seconds for response. 
    """)
    
    # Define the options for the radio button
    options_for_assistant = ['Helpful assistant', 'Software Engineer', 'Philosopher', 'Comedian']
    
    # Create the radio button with the options
    assistant_choice = st.radio("Choose an option:", options_for_assistant, on_change=assign_role, key="assistant_choice")
    
    # Define the options for the radio button
    options_for_question = ['', 'Why did the chicken cross the road?', 'Write A* algorithm', 'What is the meaning of life?']
    
    question_choice = st.radio("Choose an option:", options_for_question, on_change=assign_question, key="question_choice")
    
    if 'first time' not in st.session_state:
        st.session_state['number_of_trials'] = 3
        st.session_state['input_text'] = ''
        st.session_state['error'] = None
        st.session_state['chat'] = []
        assign_role()
        st.session_state['first time'] = False
        
    # "debug", st.session_state['chat']
    # "error", st.session_state['error']

    show_previous_q_and_a()  
    show_input_prompt_and_send_button()
    if st.session_state['error'] is not None:
        st.error(f"Try again, there was some issue with API (it happens sometimes)")  
