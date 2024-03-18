import os

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = 'gcp_starter'
CHUNK_SIZE = 300
CHUNK_OVERLAP = 20
PINECONE_INDEX_NAME = "langchainlectures"
PINECONE_DIMENSION = 1536
PINECONE_METRIC = 'cosine'
PINECONE_SPEC = {'cloud': 'aws', 'region': 'us-west-2'}
QA_CHAIN_TYPE = "stuff"
NUM_QUERY_RETRIEVE = 5

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

DOCUMENTS_DIRECTORY = 'data/'

TICKET_SAVE_DIR = 'tickets.json'

