import streamlit as st
import boto3
import botocore
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.pgvector import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize Boto3 client
config = botocore.config.Config(
    read_timeout=900,
    connect_timeout=900,
    retries={"max_attempts": 3}
)

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    config=config,
)

# Load PDF documents
loader = PyPDFLoader(
    r"C:\Users\Lenovo\Documents\Project-vs code\Amazon Transcribe\mahendhra\MAN01074RepairManualXUV700DieselATRev1.pdf"
)
docs = loader.load()

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=0)
texts = text_splitter.split_documents(docs)

# Initialize HuggingFace embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize PostgreSQL vector store
CONNECTION_STRING = "postgresql+psycopg2://postgres:serverless123@database-1-instance-1.cxbpo87iqdgv.us-east-1.rds.amazonaws.com:5432/database1"
COLLECTION_NAME = "mahendhra"
db = PGVector.from_documents(
    embedding=embeddings,
    documents=texts,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    pre_delete_collection=False
)

# Define the template for question answering
template = """
Answer truthfully based on the given text
Instruction:
1. Must identify the language of the user's question
2. Must give the response only in the identified user's language in question
3. Provide an answer only within the text provided, don't generate answers from your own

For example:
1. If the asked question is in Tamil, you should give the response in Tamil only.

{context}
{question}
"""

# Initialize the QA system
retriever = db.as_retriever(search_type='similarity', search_kwargs={"k": 3})
llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client, model_kwargs={"temperature": 1e-10, "max_tokens_to_sample": 20000})
qa_prompt = PromptTemplate(template=template, input_variables=["context", "question"])
chain_type_kwargs = {"prompt": qa_prompt, "verbose": False}
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs=chain_type_kwargs,
    verbose=False
)

# Create Streamlit app
st.title("Question Answering System")

# Define Streamlit input field for user question
question = st.text_input("Enter your question")

# Execute QA system and display result
if st.button("Ask") and question:
    result = qa.run(question)
    st.write(result)
