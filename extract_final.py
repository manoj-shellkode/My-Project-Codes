from langchain_community.document_loaders import AmazonTextractPDFLoader
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

textract_client = boto3.client("textract", region_name="us-west-2")
textract_features=["LAYOUT"]
file_path = input("Enter S3 URI")
print("Extraction in Progress...")
loader = AmazonTextractPDFLoader(file_path,textract_features,client=textract_client)
docs = loader.load()
all_page_content = ""

for doc in docs:
    all_page_content += doc.page_content
print("Extraction Done")

print("JSON Creation in Progress...")

template = """
    Must convert datas into JSON format
    Example format:
        I need exactly like this below format(Expected format)
        
            "Customs_Station": "",
                "CHA_Details": 
                    "CHA_Code": "", 
                    "CHA_Name": "",
                "BE_Details": 
                    "BE_Number": "", 
                    "BE_Date": "", 
                    "BE_Type": "",( print only the last letter for example if 'N/H' print as 'H')
                "Importer_Details": 
                    "Importer_ID": "", 
                    "PAN": "",
                    "AD_Code": "",
                    "Name": "",
                    "Address": "",
                    "Payment_Method": "",
                "IGM_Details": 
                    "IGM_No": "", 
                    "IGM_Date": "", 
                    "Port_of_Loading": "", 
                    "Country_of_Origin": "", 
                    "Country_of_Consignment": "", 
                    "MBL_Details": 
                        "MBL_No": "", 
                        "MBL_Date": ""

                    "HBL_Details": 
                        "HBL_No": "", 
                        "HBL_Date": ""
                        
                    "Pkgs_Details": 
                        "No_of_Packages": "", (print only the number of packages)
                        "Package_Type": "" (print only the package type, identify the package type in the 'No_of_Packages')

                    "Gross_weight": 
                        "Gross_Wt": "", 
                        "Units": ""

                    "Marks&Nos": ""(only need to be printed in this line ,above to the Invoice_Details, take data from 'Marks&Nos')
                "Invoice_Details": 
                    "Invoice_No": "", 
                    "Invoice_Date": "", 
                    "Supplier_Name": "", (identify and print the supplier name)
                    "Supplier_Address": "", (identify and print the supplier address)
                    "POL_Customs_House": "", (take data only from 'Cust. House')
                    "Incoterms": "", (take datas from 'TOI')
                    "Invoice_Amount": 
                        "Value": "", 
                        "Currency": "", 
                    "Freight_Amount": 
                        "Value": "", 
                        "Currency": "", 
                    "Insurance_Amount": 
                        "Value": "", 
                        "Currency": ""

                "USD to INR Exchange Value": "",(mention only the INR value)
                "Item_Details": 
                    "Item_No":, (must mention the item number like 1,2..., take from item details)
                    "RITC": "", (take datas only from 'RITC' contains only number)
                    "Description": "", (take datas only from 'Description' , print fully)
                    "Quantity": "", 
                    "Unit_Price": "", 
                    "CTH": "", 
                    "Customs_Duty_Rate": "", 
                    "BCD_amount": "", 
                    "Unit": "", (take datas from 'Unit' it consists like KGS)
                    "Assessable_Value": "", 
                    "CETH": "", (take datas from 'CETH')
                    "Excise Duty Rate": "",
                    "Countervailing Duty Amount": "", 
                    "Educational Cess on CVDs": 
                        "% Rate": "",
                        "Amount": "",
                    "Sec & Higher Edu. Cess on CVD": 
                        "% Rate": "", 
                        "Amount": "",
                    "Customs Educational Cess": 
                        "% Rate": "", 
                        "Amount": "",
                    "Customs Sec & Higher Edu. Cess": 
                        "% Rate": "", 
                        "Amount": "",
                    "Social Welfare Surcharge": 
                        "% Rate": "", 
                        "Amount": "",
                    "IGST": 
                        "% Rate": "", 
                        "Amount": "",
                    "GST Cess": 
                        "% Rate": "", 
                        "Amount": ""

                "Duties": 
                    "TOTAL ASSESSABLE VALUE": "",(take value from 'Ass Val' in 'Item Details')
                    "Inv. Gross Total": "", 
                    "BE Gross Total": "", 
                    "Total Basic Customs Duty": "", 
                    "NCD Duty": "", 
                    "ANTID": "", 
                    "SAFEGUARD DUTY": "", 
                    "CVD": "", 
                    "Sch 2 Spl Excise Duty": "", 
                    "Cess": "", 
                    "GSIA": "", 
                    "TTA": "", 
                    "Edu. Cess CVD": "", 
                    "Customs Edu. Cess": "", 
                    "Health CVD": "", 
                    "Addl Duty - (Imports)": "", 
                    "SHE. Cess CVD": "", 
                    "SH Cust Edu. Cess": "", 
                    "Total_Duty_Payable": ""

                "Container_Details": 
                    "Seal_No": "", (contains only numbers)
                    "FCL/LCL": "", (contains only letters)
                    "Container_No": ""

                "GSTIN_Details": 
                    "Document_No": "", 
                    "Document_Type": "", 
                    "State_Code": "", 
                    "State_Name": "", 
                    "IGST_Assessable_Value": "", 
                    "IGST_Amount": "", 
                    "GST_Cess_Amount": ""

                "Licence_Details": 
                    "Invoice_No": "", (print data from 'Inv' from 'Licence Details' for example, 1,2... etc)
                    "Item_No": "", 
                    "Licence_No": "", 
                    "Licence_Date": "",(take from Licence Dt)
                    "Reg_No": "", 
                    "Reg_Date": "", (take from Reg.No Dt)
                    "Debit_Value": "", 
                    "Debit_Duty": "", 
                    "Debit_Date": "", 
                    "Debit_Quantity": ""


    Instructions:
        - Do not skip any datas while converting into JSON
        - Understand and create a JSON accurately
        - Strictly provide the results in above format only ,ensure that not to change the Expected format
        - Strictly Avoid mismatching of the datas
        - Mention all the dates accurately
        - Provide results with the exact above format only

    
{datas}
"""

qa_prompt = PromptTemplate(template=template, input_variables=["datas"])
llm = Bedrock(model_id="anthropic.claude-v2:1",client=bedrock_client,model_kwargs = {"temperature":1e-10,"max_tokens_to_sample": 40000})
llm_chain = LLMChain(prompt=qa_prompt, llm=llm, verbose= False)
result = llm_chain.run(datas= all_page_content)
print("JSON Result: ")
print(result)