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

# Initialize Boto3 client with configuration
config = botocore.config.Config(
    read_timeout=900,
    connect_timeout=900,
    retries={"max_attempts": 0}
)
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    config=config,
)

# Load PDF document
loader = PyPDFLoader("C:/Users/Lenovo/Documents/Project-vs code/Amazon Transcribe/2-Cloumn page/MAN01074RepairManualXUV700DieselATRev1.pdf")
docs = loader.load()

# Split document into smaller chunks of text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
texts = text_splitter.split_documents(docs)

# Initialize Hugging Face embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# PostgreSQL connection details
CONNECTION_STRING = "postgresql+psycopg2://postgres:serverless123@database-1-instance-1.cxbpo87iqdgv.us-east-1.rds.amazonaws.com:5432/database1"
COLLECTION_NAME = "mahendhra_rise"

# Store document embeddings in PostgreSQL
db = PGVector.from_documents(
    embedding=embeddings,
    documents=texts,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    pre_delete_collection=False
)

# Template for generating answers
template = """
   Generate answers truthfully based only on the given document

    Instruction:
    - Analyse all the text datas and generate accurate answers

{context}
{question}
"""

# Initialize retriever and language model
retriever = db.as_retriever(search_type='similarity', search_kwargs={"k": 3})
llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client, model_kwargs={"temperature": 1e-10, "max_tokens_to_sample": 20000})
qa_prompt = PromptTemplate(template=template, input_variables=["context", "question"])
chain_type_kwargs = {"prompt": qa_prompt, "verbose": False}
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, chain_type_kwargs=chain_type_kwargs, verbose=False)

# Streamlit web app
st.title("Document QA System")

# User input: question
question = st.text_input("Enter your question")

# Process question and display answer
if st.button("Get Answer"):
    result = qa.run(question)
    st.write(result)
