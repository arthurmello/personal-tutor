import streamlit as st
from streamlit_chat import message
from functions import convert_pdf_to_txt_file, create_chunks, generate_questions, generate_evaluation, get_question_and_answer
import random

### File uploader ###
st.session_state.docs = {}

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

with st.sidebar:
    pdf_files = st.file_uploader("Load your PDF", type='pdf', accept_multiple_files=True)
    if pdf_files:
        for pdf_file in pdf_files:
            path = pdf_file.read()
            file_name=pdf_file.name
            # pdf to text
            text_data_f, nbPages = convert_pdf_to_txt_file(pdf_file)
            st.session_state.docs[file_name] = text_data_f
    def validate():
        st.session_state.chunks=(create_chunks(st.session_state.docs))
        st.session_state.questions=generate_questions(chunks=st.session_state.chunks)
        response=random.choice(st.session_state.questions)
        st.session_state.question_index=0
        question, answer = get_question_and_answer(response,st.session_state.question_index)
        st.session_state.current_question=question
        st.session_state.current_expected_answer=answer
        st.session_state.messages.append({"role": "assistant", "content": question, "avatar":assistant_avatar})
        st.session_state.clicked = True
        print("First line",st.session_state.question_index)
        st.session_state.question_index+=1
        print("Second line",st.session_state.question_index)
    st.button('Validate', on_click=validate)

### Chat ###
assistant_avatar='https://upload.wikimedia.org/wikipedia/en/4/42/Richard_Feynman_Nobel.jpg'
user_avatar=None

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    first_message = """Hi, how are you? I'm Richard Feynman, your personal tutor. \
    
         Start by uploading on the left the PDF files you want to study. \
         
         Once you're done, click on "Validate" and I'll start asking you questions 😊"""
    st.session_state.messages.append({"role": "assistant", "content": first_message, "avatar":assistant_avatar})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Write here..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar":user_avatar})

    # Get user answer 
    st.session_state.current_user_answer=prompt
        
    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=assistant_avatar):
        evaluation = generate_evaluation(
            question=st.session_state.current_question,
            expected_answer=st.session_state.current_expected_answer,
            user_answer=st.session_state.current_user_answer
            )
        print(evaluation)
        # Ask next question
        response=random.choice(st.session_state.questions)
        print(response)
        print("Third line",st.session_state.question_index)
        question, answer = get_question_and_answer(response,st.session_state.question_index)
        st.session_state.current_question=question
        st.session_state.current_expected_answer=answer
        st.session_state.question_index=st.session_state.question_index+1
        print("Fourth line",st.session_state.question_index)
        #st.session_state.messages
        st.markdown(evaluation)
        st.markdown(question)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": evaluation, "avatar":assistant_avatar})
    st.session_state.messages.append({"role": "assistant", "content": question, "avatar":assistant_avatar})