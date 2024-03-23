import streamlit as st
import re
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains import LLMChain
import boto3
import botocore

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

# Function to process PDF files
def process_files(file_paths):
    all_docs = []  # List to store all loaded documents

    for path in file_paths:
        loader = PDFPlumberLoader(path)
        docs = loader.load()
        all_docs.extend(docs)  # Append the loaded documents to the list
    
    template = """
    Extract the text from the bank transcation statement and print the results in the JSON format only

    for example:(make below JSON format as the reference and print exactly like the below format)
        
    "user_id":
    "statement_id":
    "identity": 
    "bank":
    "credit_card_number":
    "name":
    "address":
    "payment_due_date":
    "total_dues":
    "min_amt_due":
    "finance_charges":
    "credit_limit":
    "avl_credit_limit":
    "cash_limit":
    "avl_cash_limit":
    "opening_balance":
    "payment_or_credits":
    "purchase_or_debits":
    "statement_date": 
    "points_earned" : 
    "total_points": 

        "transactions":
            
                "amount": 
                "transaction_type":
                "date": 
                "transaction_narration":
                "transaction_details": 
                "transaction_ref_number":

the above all the details are to be in JSON

        Instruction and Description for the output format:
            
                statement_id: Unique statement id for each statement to be extracted
                user_id: Unique id for the user (if not present means simpley leave it blank)
                identity: Dictionary of user details present in the statement
                bank: Name of the bank
                credit_card_number: Credit Card number
                name: Customer name
                address: Address of the customer
                payment_due_date: Due date of the credit card bill
                total_dues: Total Amount Due
                min_amt_due: Minimum Due Amount
                finance_charges: Amount of interest charged on the amount of money borrowed
                cash_limit: take datas from Cash Limit
                credit_limit: Credit Limit including cash(take from 'Credit Limit')
                avl_credit_limit: Available credit limit (take datas only from 'Available Credit Limit' in the document)
                avl_cash_limit: Available cash limit (take datas only from 'Available Cash Limit' in the document)
                opening_balance: take datas only from 'Previous Balance' in the document
                payment_or_credits: take datas only from 'Payments, Reversals & other Credits' in the document
                purchase_or_debits: Total of the purchase and debits (take datas only from 'Purchases & Other Debits' in the document)
                statement_date: Date of the statement
                points_earned: Points earned in the statement cycle (take from 'Earned' in the document)
                total_points: Total points earned till now(take datas from 'Closing Balance' in the document)
                transactions: List of transactions
                amount: Transaction Amount
                transaction_type: Type of transaction (mention like Credit or Debit ,don't mention other than this)
                transaction_narration: The transaction narration present in the statement
                transaction_details: Any other details of the transaction if available
                transaction_ref_number: Transaction reference number if available

        - all the dates must be print in the formart like yyyy-MM-dd
                for example:
                       if the date is like "09 Jul 21" means it should print like "2021-07-09" 
                so format and print the date like this format only for all the datas 

so the i need to extract all the transcations and convert into JSON and print the accurate results for all the transcations for given document
        
        Instruction:
               - Convert all transaction data into JSON format, ensuring complete extraction and conversion without any omissions or data mismatches throughout the entire transaction process.
               - Must convert all the datas as JSON in the given text{datas} 
               - Give for all the transcations
               - transaction_type (strictly mention like Credit or Debit ,don't mention other than this)
               - For empty fields, must be "None"
               - Must create a json for all the uploaded documents as per the instructions, don't skip anyone
{datas}
"""

    qa_prompt = PromptTemplate(template=template, input_variables=["datas"])
    llm = Bedrock(model_id="anthropic.claude-v2:1",client=bedrock_client,model_kwargs = {"temperature":1e-10,"max_tokens_to_sample": 40000})
    llm_chain = LLMChain(prompt=qa_prompt, llm=llm, verbose= False)
    result = llm_chain.run(datas= all_docs)
    
    return result

# Function to extract JSON data from text
def extract_json(text):
    start_index = text.find('{')
    end_index = text.rfind('}') + 1
    
    if start_index != -1 and end_index != -1:
        json_data = text[start_index:end_index]
        return json_data
    else:
        return None

# Streamlit UI
st.title("Bank Transaction Statement Extractor")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if st.button("Process"):
    file_paths = []
    for uploaded_file in uploaded_files:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(uploaded_file.name)
    
    if file_paths:
        result = process_files(file_paths)
        
        # Extract JSON data from the result
        json_data = extract_json(result)
        
        if json_data:
            st.json(json_data)
        else:
            st.error("No JSON data found.")
    else:
        st.warning("Please upload PDF files to process.")
