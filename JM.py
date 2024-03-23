import streamlit as st
import tempfile
import os
import re
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains import LLMChain
import boto3
import botocore

# Configure AWS credentials if necessary
# boto3.setup_default_session(profile_name='your-profile-name')

# AWS configuration
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


st.title("Jupiter Money")

# PDF upload
pdf_file = st.file_uploader("Upload PDF", type=['pdf'])

if pdf_file is not None:
    # Save the uploaded PDF to a temporary location
    temp_pdf_path = os.path.join(tempfile.gettempdir(), "uploaded_pdf.pdf")
    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_file.read())

    # Load PDF and extract text
    loader = PDFPlumberLoader(temp_pdf_path)
    docs = loader.load()

    # Prompt template for transaction extraction
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
                bank: Name of the bank (don't include 'card' in bank name instead mention only the bank name, if sbi bank means 'sbi', if icici bank means 'icici' don't include like 'icici card' or 'sbi card' )
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
{datas}
"""

    qa_prompt = PromptTemplate(template=template, input_variables=["datas"])
    llm = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock_client,
                  model_kwargs={"temperature": 1e-10, "max_tokens_to_sample": 40000})
    llm_chain = LLMChain(prompt=qa_prompt, llm=llm, verbose=False)
    

    result = llm_chain.run(datas=docs)

    st.subheader("JSON:")

    provided_text = result

    start_index = provided_text.find('{')
    end_index = provided_text.rfind('}') + 1
    json_data = provided_text[start_index:end_index]

    st.json(json_data)
