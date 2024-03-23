import streamlit as st
import os

import boto3
import botocore

from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.pgvector import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

#hashed_passwords = stauth.Hasher(['SKDemo@24']).generate()
#print('Hashed password: ', hashed_passwords)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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

llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client, model_kwargs={"temperature": 1e-10, "max_tokens_to_sample": 20000})

COLLECTION_NAME = "mahendhra"
CONNECTION_STRING = "postgresql+psycopg2://postgres:serverless123@database-1-instance-1.cxbpo87iqdgv.us-east-1.rds.amazonaws.com:5432/database1"

with open('access_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login('Login', 'main')
if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
    
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def data_ingestion(collection_name: str, connection_string: str, retain_existing_collection: bool = False):
    loader = PyPDFLoader(
        r"C:\Users\Lenovo\Documents\Project-vs code\Amazon Transcribe\2-Cloumn page\MAN01074RepairManualXUV700DieselATRev1.pdf"
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=0)
    texts = text_splitter.split_documents(docs)

    PGVector.from_documents(
        embedding=embeddings,
        documents=texts,
        collection_name=collection_name,
        connection_string=connection_string,
        pre_delete_collection=retain_existing_collection
    )

def data_query(collection_name: str, connection_string: str):
    return PGVector(
        collection_name=collection_name,
        connection_string=connection_string,
        embedding_function=embeddings
    )


def save_chat_message(question):
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    store = data_query(COLLECTION_NAME, CONNECTION_STRING)

    template = """
        Generate answers truthfully based only on the given document

        Instruction:
        - Analyse all the text datas and generate accurate answers

    {context}
    {question}
    """
        
    retriever = store.as_retriever(search_type='similarity', search_kwargs={"k": 3})
    qa_prompt = PromptTemplate(template=template, input_variables=["context","question"])
    chain_type_kwargs = { "prompt": qa_prompt, "verbose": True }
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs,
        verbose=False
    )
    
    result = qa.run(question)
    print('RESULT: ', result)

    with st.chat_message("user"):
        st.markdown(question)
    
    st.session_state.messages.append({"role": "user", "content": question})

    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)

def main():
    authenticator.logout('Logout', 'sidebar', key='auth_logout')

    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    os.environ['LANGCHAIN_API_KEY'] = "ls__fdf6b34054124890847791d04ef49b8a"
    os.environ['LANGCHAIN_PROJECT'] = 'negotiation'

    st.title("Demo - Mahindra")

    ## Call this function whenever it is needed to ingest the data
    data_ingestion(COLLECTION_NAME, CONNECTION_STRING,True)
    
    with st.sidebar:
        st.image("images/sk-logo-trans.png")
        if st.sidebar.button('Reset chat history'):
            st.session_state.messages = []
    
    if len(st.session_state.messages) <= 1:
        message = st.chat_message("assistant")
        message.write("How may I assist you?")
            
    if prompt := st.chat_input("Ask a question", key="primary_chat"):
        save_chat_message(prompt)
    
if st.session_state["authentication_status"]:
    #q1: What is the quantity of oil in the Transaxel
    main()