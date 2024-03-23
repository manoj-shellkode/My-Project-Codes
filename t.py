import streamlit as st
import re
import json

st.subheader("JSON:")

provided_text = """ Here is the JSON output with all the transaction details extracted from the documents:

```json
{
    "user_id": "None",
    "statement_id": "B21073266361",
    "identity": {
        "name": "SUNIL KUMAR YADAV"
    },
    "bank": "SBI Card", 
    "credit_card_number": "XXXX XXXX XXXX XX24",
    "name": "SUNIL KUMAR YADAV",
    "address": "None",
    "payment_due_date": "2021-08-11",
    "total_dues": 33051.0,
    "min_amt_due": 5717.0,
    "finance_charges": 881.61,
    "credit_limit": 200000.0,
    "avl_credit_limit": 158903.54,
    "cash_limit": 60000.0,
    "avl_cash_limit": 60000.0,
    "opening_balance": 13396.71,
    "payment_or_credits": 13778.47,
    "purchase_or_debits": 39150.6,
    "statement_date": "2021-07-22",
    "points_earned": 2706,
    "total_points": 5037,
    "transactions": [
        {
            "amount": 39.0,
            "transaction_type": "Credit",
            "date": "2021-07-09",
            "transaction_narration": "PETROL TRXN FEE RVRSL EXCLUDING TAX",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 950.0,
            "transaction_type": "Debit",
            "date": "2021-07-15",
            "transaction_narration": "FEE - LATE PAYMENT (EXCL TAX 171.00)",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 38.99,
            "transaction_type": "Credit",
            "date": "2021-07-15",
            "transaction_narration": "PETROL TRXN FEE RVRSL EXCLUDING TAX",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 13397.0,
            "transaction_type": "Credit",
            "date": "2021-07-18",
            "transaction_narration": "PAYMENT RECEIVED 000000000VSBI0122352237",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 22.01,
            "transaction_type": "Credit",
            "date": "2021-07-20",
            "transaction_narration": "PETROL TRXN FEE RVRSL EXCLUDING TAX",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 4094.0,
            "transaction_type": "Debit",
            "date": "2021-07-22",
            "transaction_narration": "FP EMI 01/03(EXCL TAX 25.37)",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 140.95,
            "transaction_type": "Debit",
            "date": "2021-07-22",
            "transaction_narration": "INTEREST ON EMI",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 881.61,
            "transaction_type": "Debit",
            "date": "2021-07-22",
            "transaction_narration": "FIN CHARGE ON RETAIL (EXCL TAX 158.69)",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 355.06,
            "transaction_type": "Debit",
            "date": "2021-07-22",
            "transaction_narration": "IGST DB @ 18.00%",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 1099.0,
            "transaction_type": "Debit",
            "date": "2021-06-25",
            "transaction_narration": "FLIPKART PAYMENTS GURGAON IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },  
        {
            "amount": 399.0,
            "transaction_type": "Debit",
            "date": "2021-06-25",
            "transaction_narration": "FLIPKART PAYMENTS GURGAON IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 3088.88,
            "transaction_type": "Debit",
            "date": "2021-06-27",
            "transaction_narration": "NAYAN FILLING STATION LUCKNOW IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 234.82,
            "transaction_type": "Debit",
            "date": "2021-07-02",
            "transaction_narration": "AMAZON PAY INDIA PRIVA BANGALORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 44.58,
            "transaction_type": "Debit",
            "date": "2021-07-02",
            "transaction_narration": "AMAZON PAY INDIA PRIVA BANGALORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "None" 
        },
        {
            "amount": 306.36,
            "transaction_type": "Debit",
            "date": "2021-07-02",
            "transaction_narration": "AMAZON PAY INDIA PRIVA BANGALORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 281.47,
            "transaction_type": "Debit",
            "date": "2021-07-03",
            "transaction_narration": "IRCTC WWW.IRCTC.CO. IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 4799.0,
            "transaction_type": "Debit",
            "date": "2021-07-03",
            "transaction_narration": "FLIPKART PAYMENTS GURGAON IN (Pay in EMIs)",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 278.19,
            "transaction_type": "Credit",
            "date": "2021-07-06",
            "transaction_narration": "IRCTC WWW.IRCTC.CO. IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 3743.66,
            "transaction_type": "Debit",
            "date": "2021-07-06",
            "transaction_narration": "SUDHA FILLING STATION LUCKNOW IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 2224.66,
            "transaction_type": "Debit",
            "date": "2021-07-08",
            "transaction_narration": "PAYTM WWW.PAYTM.COM IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 3.28,
            "transaction_type": "Credit",
            "date": "2021-07-08",
            "transaction_narration": "IRCTC WWW.IRCTC.CO. IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 3947.39,
            "transaction_type": "Debit",
            "date": "2021-07-09",
            "transaction_narration": "GOKUL FILLING STATION UNNAO IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 11999.0,
            "transaction_type": "Debit",
            "date": "2021-07-15",
            "transaction_narration": "#FLIPKART PAYMENTS BANGALORE IN (Pay in EMIs)",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 3945.36,
            "transaction_type": "Debit",
            "date": "2021-07-15",
            "transaction_narration": "HIGHWAY TRUCK SERVICE UNNAO IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 11999.0,
            "transaction_type": "Debit",
            "date": "2021-07-17",
            "transaction_narration": "TRANSFER TO MERCHANT EMI",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        },
        {
            "amount": 3037.42,
            "transaction_type": "Debit",
            "date": "2021-07-20",
            "transaction_narration": "AMAR HIGHWAY SERVICE S UNNAO IN",
            "transaction_details": "None",
            "transaction_ref_number": "None"
        }
    ]
}
```

```json
{
    "user_id": "None",
    "statement_id": "None",
    "identity": {
        "name": "Mr Nirmal Velusamy"
    },
    "bank": "ICICI Bank",
    "credit_card_number": "4375 XXXX XXXX 3005",
    "name": "Mr Nirmal Velusamy",
    "address": "369(1),R G NAGAR,PALANI,,PUTHUR, CHINNAKALAYAMPUTHUR\nDINDIGUL 624615",
    "payment_due_date": "None",
    "total_dues": "None",
    "min_amt_due": "None",
    "finance_charges": "None",
    "credit_limit": "None",
    "avl_credit_limit": "None",
    "cash_limit": "None",
    "avl_cash_limit": "None",
    "opening_balance": "None",
    "payment_or_credits": "None",
    "purchase_or_debits": "None",
    "statement_date": "None",
    "points_earned": "None", 
    "total_points": "None",
    "transactions": [
        {
            "amount": 4506.0,
            "transaction_type": "Debit",
            "date": "2022-04-14",
            "transaction_narration": "DECATHLON SPORTS INDIA BANGALORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "74332742105210488701061"
        },
        {
            "amount": 3638.0,
            "transaction_type": "Debit", 
            "date": "2022-04-20",
            "transaction_narration": "MANZAR EXPERIENCE CURA BANGALORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "74391732111000120828047"
        },
        {
            "amount": 465.0,
            "transaction_type": "Debit",
            "date": "2022-04-22",
            "transaction_narration": "MAHALAKSHMI WINES BANGALORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "74332742113211279100489"
        },
        {
            "amount": -8609.0,
            "transaction_type": "Credit",
            "date": "2022-05-03",
            "transaction_narration": "UPI Payment Received",
            "transaction_details": "None",
            "transaction_ref_number": "212320033467"
        },
        {
            "amount": 3238.5,
            "transaction_type": "Debit",
            "date": "2022-05-22",
            "transaction_narration": "SHANTHI SOCIAL SERVICE COIMBATORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "74332742143214292161276"
        },
        {
            "amount": -3234.5,
            "transaction_type": "Credit",
            "date": "2022-06-14",
            "transaction_narration": "UPI Payment Received",
            "transaction_details": "None",
            "transaction_ref_number": "216509924251"
        },
        {
            "amount": 1260.0,
            "transaction_type": "Debit",
            "date": "2022-06-18",
            "transaction_narration": "PASSION HOTELS PRIVATE COIMBATORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "74375792171000475147622"
        },
        {
            "amount": 505.9,
            "transaction_type": "Debit",
            "date": "2022-06-19",
            "transaction_narration": "BPCL ACE PETROPRODUCTS COIMBATORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "24163252170044340389644"
        },
        {
            "amount": -1765.9,
            "transaction_type": "Credit",
            "date": "2022-07-13",
            "transaction_narration": "UPI Payment Received",
            "transaction_details": "None",
            "transaction_ref_number": "219472347268"
        },
        {
            "amount": 2020.0,
            "transaction_type": "Debit",
            "date": "2022-07-23",
            "transaction_narration": "AMMAN PETROL AGENCY DINDIGUL IN",
            "transaction_details": "None",
            "transaction_ref_number": "74332742206220407150652"
        },
        {
            "amount": 2055.0,
            "transaction_type": "Debit",
            "date": "2022-07-24",
            "transaction_narration": "HOTEL KANNAPPA TRICHY IN",
            "transaction_details": "None",
            "transaction_ref_number": "74332742206220529811553"
        },
        {
            "amount": 1649.0,
            "transaction_type": "Debit",
            "date": "2022-07-27",
            "transaction_narration": "AMAZON HTTP://WWW.AM IN",
            "transaction_details": "None",
            "transaction_ref_number": "74766512208229035863321"
        },
        {
            "amount": 617.0,
            "transaction_type": "Debit",
            "date": "2022-08-01",
            "transaction_narration": "MAKEMYTRIP INDIA PVT L NEW DELHI IN",
            "transaction_details": "None",
            "transaction_ref_number": "74332742214221340024137"
        },
        {
            "amount": -6341.0,
            "transaction_type": "Credit",
            "date": "2022-08-13",
            "transaction_narration": "UPI Payment Received",
            "transaction_details": "None",
            "transaction_ref_number": "222542839459"
        },
        {
            "amount": 980.0,
            "transaction_type": "Debit",
            "date": "2022-08-14",
            "transaction_narration": "TASMAC 440 CHENNAI IN",
            "transaction_details": "None",
            "transaction_ref_number": "74766512226232274612506"
        },
        {
            "amount": 1400.0,
            "transaction_type": "Debit",
            "date": "2022-08-20",
            "transaction_narration": "PASSION HOTELS PRIVATE COIMBATORE IN",
            "transaction_details": "None",
            "transaction_ref_number": "74375792234000494566435"
        }
    ]
}
```

I have extracted all the transaction details from both statements and converted them into the requested JSON format. For empty/missing fields I have put "None". For transaction_type I have mentioned "Credit" or "Debit" as per the instructions. Please let me know if you need any changes or have additional documents to extract transactions from.
 """

# Use regular expression to extract JSON data
json_data = re.findall(r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}', provided_text)

# Display extracted JSON data
# for data in json_data:
#     st.json(json.loads(data))
for data in json_data:
    # Remove invalid control characters
    cleaned_data = ''.join(char for char in data if 31 < ord(char) < 127)
    try:
        parsed_json = json.loads(cleaned_data)
        st.json(parsed_json)
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
