import json
import os
from dotenv import load_dotenv
from langchain_community.llms import OpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as langpinecone
from pinecone import Pinecone, ServerlessSpec
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import streamlit as st

# Initialize components
# Initialize Pinecone
def init_pinecone():
    return Pinecone(
        api_key=os.getenv('PINECONE_API_KEY'),
        #api_key = '170713c4-ad2c-47e5-86b9-2c275df212a6',
        environment="gcp-starter"
    )
# api_key=os.environ.get('PINECONE_API_KEY'),
def init_components():
    # Load documents
    documents = read_doc('data/')
    documents = chunk_data(documents)
    
    # Initialize embeddings and Pinecone
    embeddings = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'))
    pc = init_pinecone()
    
    # Create or get Pinecone index
    index_name = "langchainlectures"
    index = ensure_pinecone_index(pc, index_name, documents, embeddings)
    
    # Initialize LLM
    llm = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0.5)
    chain = load_qa_chain(llm, chain_type="stuff") 
    return index, chain

# Read and chunk documents
def read_doc(directory):
    file_loader = PyPDFDirectoryLoader(directory)
    documents = file_loader.load()
    return documents

def chunk_data(docs, chunk_size=800, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(docs)

# Ensure Pinecone index exists
def ensure_pinecone_index(pc, index_name, documents, embeddings):
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name, 
            dimension=1536,  # Adjust as needed
            metric='cosine',
            spec=ServerlessSpec(cloud='gcp', region='us-west-2')
        )
    return langpinecone.from_documents(documents, embeddings, index_name=index_name)

# Retrieve query from Pinecone
def retrieve_query(index, query, k=2):
    return index.similarity_search(query, k=k)


def retrieve_answer(chain, index, query):
    doc_search = retrieve_query(index, query)
    try:
        # Attempt to invoke the chain with provided documents and question
        
        response = chain.invoke(input={"input_documents": doc_search, "question": query})
        # Extract the answer from the response
        answer = response['output_text']
        return answer  # Return the answer so it can be used outside the function
    except Exception as e:
        # If an error occurs, return the error message instead
        print(f"An error occurred: {e}") 
        return f"An error occurred: {e}"


# Collect and store ticket info
def collect_and_store_ticket_info(original_query, answer):
    user_query = original_query
    additional_info_for_query = input("Please enter additional info in support of your query: ").strip()
    user_email = input("Please enter your email address for the support ticket: ").strip()
    ticket_info = {'query': user_query, 'additional_info_query' : additional_info_for_query,'LLM_answer' : answer, 'email': user_email}
    store_ticket_info(ticket_info)

# Prompt for ticket generation
def prompt_for_ticket(original_query, answer):
    print("If this answer does not meet your expectations, would you like to generate a ticket? (yes/no)")
    if input().strip().lower() == 'yes':
        collect_and_store_ticket_info(original_query, answer)

# Store ticket information in JSON format
def store_ticket_info(ticket_info):
    with open('tickets.json', 'a') as file:
        json.dump(ticket_info, file)
        file.write('\n')


if __name__ == "__main__":
    RED = '\033[31m'
    # Initialize or load necessary components
    load_dotenv()
    index, chain = init_components() 

    st.title("AI Agent")

    user_query = st.text_input("Please enter your question:", "")

    # Trigger LLM processing only if the user question changes
    if 'last_query' not in st.session_state or st.session_state.last_query != user_query:
        if user_query:
            
            answer = retrieve_answer(chain, index, user_query)
            # Store the current query and its answer in the session state
            st.session_state.last_query = user_query
            st.session_state.last_answer = answer
    elif user_query:
        # If the query hasn't changed, use the stored answer
        answer = st.session_state.last_answer
    else:
        answer = ""

    if user_query:
        st.text_area("Answer:", value=answer, height=150, help="The response from the LLM.")
        
        st.write("If the above solution does not meet your expectations, would you like to generate a ticket for human support? If yes, then press 'Generate Support Ticket'.")
        if st.button("Generate Support Ticket"):
            # Display the ticket form without rerunning the LLM
            st.session_state.display_ticket_form = True

    if 'display_ticket_form' in st.session_state and st.session_state.display_ticket_form:
        with st.form(key='ticket_form'):
            additional_info_for_query = st.text_input("Please enter additional info in support of your query:")
            user_email = st.text_input("Please enter your email address for the support ticket ****:red[*]****:")
            
            submit_button = st.form_submit_button("Submit Ticket")
            if submit_button:
                if not user_email.strip():  # Check if the email field is empty or contains only whitespace
                    st.error("Please enter your email address to submit the ticket.")
                else:
                    ticket_info = {
                        'query': user_query, 
                        'additional_info_query': additional_info_for_query, 
                        'LLM_answer': answer, 
                        'email': user_email
                    }
                    store_ticket_info(ticket_info)
                    st.success("Your ticket has been generated successfully.")
                    
                    # Optionally reset or clear the form fields here
                    st.session_state.display_ticket_form = False
                    # Clear session state related to the query and answer to reset the app state
                    del st.session_state.last_query
                    del st.session_state.last_answer

# if __name__ == "__main__":
#     st.title("Question Answering System")
#     load_dotenv()
#     index, chain = init_components() 

#     user_query = st.text_input("Please enter your question:", key="user_query")

#     if user_query:
#         if 'last_query' not in st.session_state or user_query != st.session_state.last_query:
#             answer = retrieve_answer(chain, index, user_query)
#             st.session_state['last_query'] = user_query
#             st.session_state['last_answer'] = answer
#             st.session_state['feedback_submitted'] = False
#             # Ensure the ticket form is not displayed for a new query until needed
#             st.session_state['display_ticket_form'] = False

#         if not st.session_state.get('feedback_submitted', False):
#             st.text_area("Answer:", value=st.session_state.last_answer, height=250, help="The response from the LLM.")
#             st.write("Was this answer helpful?")
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Yes", key="yes_feedback"):
#                     feedback_info = {
#                         'query': user_query, 
#                         'LLM_answer': st.session_state.last_answer,
#                         'feedback': "Yes"
#                     }
#                     store_ticket_info(feedback_info)
#                     st.success("Thank you for your feedback! Your response has been recorded.")
#             with col2:
#                 if st.button("No", key="no_feedback"):
#                     st.session_state['feedback_submitted'] = True
#                     st.session_state['display_ticket_form'] = True  # Show the form for negative feedback

#         # Display the ticket generation form if the condition is met
#         if st.session_state.get('display_ticket_form', False):
#             with st.form(key='ticket_form'):
#                 additional_info_for_query = st.text_input("Please enter additional info in support of your query:")
#                 user_email = st.text_input("Please enter your email address for the support ticket:")
                
#                 submit_button = st.form_submit_button("Submit Ticket")
#                 if submit_button:
#                     # Process and save ticket information
#                     ticket_info = {
#                         'query': user_query, 
#                         'additional_info_query': additional_info_for_query, 
#                         'LLM_answer': st.session_state.last_answer, 
#                         'email': user_email,
#                         'feedback':'No'
#                     }
#                     store_ticket_info(ticket_info)
#                     st.success("Your ticket has been generated successfully.")
#                     # Optionally reset form visibility and other states as needed
#                     st.session_state['display_ticket_form'] = False
#                     # Clear form fields here if needed
#     else:
#         # If there is no query, ensure the form and feedback submission state are reset
#         st.session_state['feedback_submitted'] = False
#         st.session_state['display_ticket_form'] = False

    