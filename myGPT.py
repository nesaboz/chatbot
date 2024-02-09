# DO NOT RENAME OR MOVE THIS FILE. 
# Must update GitHub action workflow and documentation in README if you do.

import streamlit as st
import requests
import json

TEXT_INPUT_KEY = "user_input"

# Function to send requests to your GPT model
def query_mygpt(chat):
    """
    Call lambda function with the provided chat. This chat will have system role as a first item, 
    then questions and answers in pairs.

    Args:
        chat (list(dict)): List of dictionaries with keys 'role' and 'content'. 
            Length is 2N where N is the number of questions asked (1 for system role, and 1 for a question)

    Returns:
        list(dict): new chat that includes the response from the GPT model. Length is 2N + 1 (role + N Q&A pairs)
    """

    lambda_url = "https://5faukxw75uazcs2zdl4zbvyg2e0lebie.lambda-url.us-west-1.on.aws/"
    # print("Please wait while GPT is done ...")
    headers = {'Content-Type': 'application/json'}

    r = requests.post(headers=headers, url=lambda_url, json=json.dumps(chat))
    try:
        new_chat = json.loads(r.content.decode('utf-8'))
        if new_chat[-1]['role'] in ['assistant', 'system']:
            st.session_state['number_of_trials'] -= 1
            st.session_state['error'] = None
        else:
            raise Exception("The last message was not from the assistant or system.")
        return False, new_chat
    except Exception as e:
        st.session_state['error'] = e
        return True, chat


# Function to handle sending the message
def send_message(question):
    
    st.session_state['input_text'] = question
    
    possible_new_chat = st.session_state['chat'].copy()
    possible_new_chat.append({'role': 'user', 'content': question})
    error, new_chat = query_mygpt(possible_new_chat)
    
    st.session_state['chat'] = new_chat
    
    if not error:
        st.session_state[TEXT_INPUT_KEY] = ''
        st.session_state['input_text'] = ''
    else:
        # will have to show the same question again
        st.session_state[TEXT_INPUT_KEY] = question
        st.session_state['input_text'] = question
    

def show_previous_q_and_a(chat_history):
    # show all previous Q&A
    for i in range(1, len(chat_history), 2):
        # writes previous question
        question = chat_history[i]['content']
        a1 = st.write(question)
        # writes previous answer
        answer = chat_history[i+1]['content']
        a2 = st.markdown(f'<div style="color: gray;">{answer}</div>', unsafe_allow_html=True) 
        st.text("\n" * 10)
        
        
def show_input_prompt_and_send_button():
    # show a new inout prompt and a send button, as well as error if it was there previously

    if st.session_state['number_of_trials'] > 0:
        # Using columns to organize the layout
        col1, col2 = st.columns([4, 1])

        with col1:
            user_input = st.text_input(
                label="user input", 
                value=st.session_state['input_text'], 
                key=TEXT_INPUT_KEY, 
                placeholder="Enter a question", 
                label_visibility="collapsed"
                )
            
        # Send button in the second column
        with col2:
            send_button = st.button("Send", on_click=send_message, args=(user_input,))
        
    else:
        st.info(f"This demo allows only 3 API calls. Thanks for trying it out. No chats are stored.")

        
# def show_with_background_color(some_text):
#     """
#     Not used anymore. The ideas was to have custom background color,
#     but it is easier to just have chatbot reply in gray color,
#     that way it works on both dark and light mode. 
#     """

#     st.markdown("""
#         <style>
#         .content {
#             background-color: #f0f0f0;  /* Light gray background */
#             padding: 10px;             /* Padding around the text */
#         }
#         </style>
#         """, unsafe_allow_html=True)
#     # Display the content with custom style
#     st.markdown(f'<div class="content">{some_text}</div>', unsafe_allow_html=True)


if 'first time' not in st.session_state:
    st.session_state['number_of_trials'] = 3
    st.session_state['first time'] = False
    st.session_state['input_text'] = ''
    st.session_state['error'] = None
    st.session_state['chat'] = [
    {'role': 'system', 'content': 'You are a software engineer'}
    ]
# Streamlit app layout
st.title("MyGPT Demo")

st.info(f"Welcome to MyGPT, a simple OpenAI ChatGPT-3 based chatbot (for now).\nNo chats are stored. Responses are limited to about 300 words. ")

"debug", st.session_state['chat']
"error", st.session_state['error']

# if no_errors(st.session_state['chat']):
#     # show all previous Q&A
#     show_previous_q_and_a(st.session_state['chat'])
#     # show a new input prompt and a send button
#     show_input_prompt_and_send_button()
# else: # there was some error so show the previous Q&A and the same question again
#     # show n-1 previous Q&A
#     show_previous_q_and_a(st.session_state['chat'], offset=2)
    
#     # show the same question again and a send button
#     previous_question = st.session_state['chat'][-1]['content']
#     show_input_prompt_and_send_button(previous_question)
#     # show an extra field saying it failed so the user should retry
    
#     st.error(f"Try again, there was some issue with API (it happens sometimes)")  

# show all previous Q&A 
show_previous_q_and_a(st.session_state['chat'])

# show an input prompt and a send button
show_input_prompt_and_send_button()
    
if st.session_state['error'] is not None:
    # show an extra field saying it failed so the user should retry
    st.error(f"Try again, there was some issue with API (it happens sometimes)")  
    