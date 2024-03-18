import os
import json
from typing import Any, Dict, List, Tuple, Union
from langchain_community.llms import OpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as langpinecone
from pinecone import Pinecone, ServerlessSpec
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import config as config


def init_pinecone() -> Pinecone:
    """
    Initializes Pinecone.

    Returns:
        Pinecone: Initialized Pinecone instance.
    """
    return Pinecone(
        api_key=config.PINECONE_API_KEY, #os.getenv('PINECONE_API_KEY'),
        environment=config.PINECONE_ENV
    )

def read_doc(directory: str) -> List[str]:
    """
    Reads documents from the specified directory.

    Args:
        directory (str): Directory path containing documents.

    Returns:
        List[str]: List of documents.
    """
    file_loader = PyPDFDirectoryLoader(directory)
    documents = file_loader.load()
    return documents

def chunk_data(docs: List[str], chunk_size: int = config.CHUNK_SIZE, chunk_overlap: int = config.CHUNK_OVERLAP) -> List[str]:
    """
    Chunks the documents into smaller parts.

    Args:
        docs (List[str]): List of documents.
        chunk_size (int, optional): Size of each chunk. Defaults to 300.
        chunk_overlap (int, optional): Overlap between chunks. Defaults to 20.

    Returns:
        List[str]: List of chunked documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(docs)

def init_components() -> Tuple[Any, Any]:
    """
    Initializes components including documents, embeddings, Pinecone, and LLM.

    Returns:
        Tuple[Any, Any]: Tuple containing initialized Pinecone index and loaded QA chain.
    """
    documents = read_doc(config.DOCUMENTS_DIRECTORY)
    documents = chunk_data(documents)
    embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
    pc = init_pinecone()
    index_name = config.PINECONE_INDEX_NAME
    index = ensure_pinecone_index(pc, index_name, documents, embeddings)
    llm = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0.6)
    chain = load_qa_chain(llm, chain_type="stuff") 
    return index, chain

def ensure_pinecone_index(pc: Pinecone, index_name: str, documents: List[str], embeddings: Any) -> langpinecone:
    """
    Ensures Pinecone index exists.

    Args:
        pc (Pinecone): Pinecone instance.
        index_name (str): Name of the index.
        documents (List[str]): List of documents.
        embeddings (Any): Embeddings.

    Returns:
        langpinecone: Pinecone index.
    """
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name, 
            dimension=config.PINECONE_DIMENSION,
            metric=config.PINECONE_METRIC,
            spec=ServerlessSpec(cloud='aws', region='us-west-2')
        )
    return langpinecone.from_documents(documents, embeddings, index_name=index_name)

def retrieve_query(index: langpinecone, query: str, k: int = config.NUM_QUERY_RETRIEVE) -> Any:
    """
    Retrieves query from Pinecone index.

    Args:
        index (langpinecone): Pinecone index.
        query (str): Query string.
        k (int, optional): Number of results to retrieve. Defaults to 5.

    Returns:
        Any: Query results.
    """
    return index.similarity_search(query, k=k)

def retrieve_answer(chain: Any, index: langpinecone, query: str) -> Tuple[str, Any]:
    """
    Retrieves answer using QA chain.

    Args:
        chain (Any): Loaded QA chain.
        index (langpinecone): Pinecone index.
        query (str): Query string.

    Returns:
        Tuple[str, Any]: Retrieved answer and document reference.
    """
    doc_search = retrieve_query(index, query)
    try:
        initial_query = f"""Using only the information from the provided document {query}.If the answer is not available in the document and you are not confident about the output,
                        please say "Information not available" """
        response = chain.invoke(input={"input_documents": doc_search, "question": initial_query})
        doc_ref = response
        answer = response['output_text']
        return answer, doc_ref
    except Exception as e:
        print(f"An error occurred: {e}") 
        return f"An error occurred: {e}"

def collect_and_store_ticket_info(original_query: str, answer: str) -> None:
    """
    Collects and stores ticket information.

    Args:
        original_query (str): Original query.
        answer (str): Answer obtained from LLM.
    """
    user_query = original_query
    additional_info_for_query = input("Please enter additional info in support of your query: ").strip()
    user_email = input("Please enter your email address for the support ticket: ").strip()
    ticket_info = {'query': user_query, 'additional_info_query' : additional_info_for_query,'LLM_answer' : answer, 'email': user_email}
    store_ticket_info(ticket_info)

def prompt_for_ticket(original_query: str, answer: str) -> None:
    """
    Prompts the user for generating a ticket.

    Args:
        original_query (str): Original query.
        answer (str): Answer obtained from LLM.
    """
    print("If this answer does not meet your expectations, would you like to generate a ticket? (yes/no)")
    if input().strip().lower() == 'yes':
        collect_and_store_ticket_info(original_query, answer)

def store_ticket_info(ticket_info: Dict[str, Union[str, int]]) -> None:
    """
    Stores ticket information in JSON format.

    Args:
        ticket_info (Dict[str, Union[str, int]]): Ticket information.
    """
    with open(config.TICKET_SAVE_DIR, 'a') as file:
        json.dump(ticket_info, file)
        file.write('\n')
