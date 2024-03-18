import os
import json
from dotenv import load_dotenv
import streamlit as st
from utils import (
    init_components,
    retrieve_answer,
    store_ticket_info
)


if __name__ == "__main__":
    st.title("AI Agent")
    st.info("The objective of this project is to develop an AI agent specialized in a single domain, designed to efficiently address user queries by consulting its extensive database for solutions. In cases where the AI agent is unable to locate a suitable answer, it will guide the user to submit a ticket request. This mechanism ensures that all queries receive timely and accurate responses, leveraging AI capabilities for immediate assistance and escalating to human support when necessary.")
    load_dotenv()
    index, chain = init_components() 

    user_query = st.text_input("Please enter your question:", key="user_query")

    if user_query:
        if 'last_query' not in st.session_state or user_query != st.session_state.last_query:
            answer, doc_ref= retrieve_answer(chain, index, user_query)
            st.session_state['last_query'] = user_query
            st.session_state['last_answer'] = answer
            st.session_state['last_doc_ref'] = doc_ref
            st.session_state['feedback_submitted'] = False
            # Ensure the ticket form is not displayed for a new query until needed
            st.session_state['display_ticket_form'] = False

        if not st.session_state.get('feedback_submitted', False):
            st.text_area("doc_ref:", value=st.session_state.last_doc_ref, height=250, help="The response from the LLM.")
            st.text_area("Answer:", value=st.session_state.last_answer, height=250, help="The response from the LLM.")
            st.write("Was this answer helpful?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes", key="yes_feedback"):
                    feedback_info = {
                        'query': user_query, 
                        'LLM_answer': st.session_state.last_answer,
                        'feedback': "Yes"
                    }
                    store_ticket_info(feedback_info)
                    st.success("Thank you for your feedback! Your response has been recorded.")
            with col2:
                if st.button("No", key="no_feedback"):
                    st.session_state['feedback_submitted'] = True
                    st.session_state['display_ticket_form'] = True  # Show the form for negative feedback

        # Display the ticket generation form if the condition is met
        if st.session_state.get('display_ticket_form', False):
            with st.form(key='ticket_form'):
                additional_info_for_query = st.text_input("Please enter additional info in support of your query:")
                user_email = st.text_input("Please enter your email address for the support ticket:")
                
                submit_button = st.form_submit_button("Submit Ticket")
                if submit_button:
                    # Process and save ticket information
                    ticket_info = {
                        'query': user_query, 
                        'additional_info_query': additional_info_for_query, 
                        'LLM_answer': st.session_state.last_answer, 
                        'email': user_email,
                        'feedback':'No'
                    }
                    st.text(ticket_info)
                    store_ticket_info(ticket_info)
                    st.success("Your ticket has been generated successfully.")
                    # Optionally reset form visibility and other states as needed
                    st.session_state['display_ticket_form'] = False
                    # Clear form fields here if needed
    else:
        # If there is no query, ensure the form and feedback submission state are reset
        st.session_state['feedback_submitted'] = False
        st.session_state['display_ticket_form'] = False