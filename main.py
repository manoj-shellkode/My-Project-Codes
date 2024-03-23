import boto3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.document_loaders import S3FileLoader
from bedrock import get_bedrock_client
import os
import time
import urllib
import json
bucket_name = 'my-s3-doc-loader'

def transcribe_and_create_pdf(language_code='en-US',
                               job_name_prefix='My-transcription', pdf_filename_prefix='Transcription_output'):
    transcribe_client = boto3.client('transcribe')

    def transcribe_file(job_name, file_uri, transcribe_client, media_format, language_code):
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat=media_format,
            LanguageCode=language_code
        )
        max_tries = 60
        while max_tries > 0:
            max_tries -= 1
            job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = job['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                print(f"Job {job_name} is {job_status}.")
                if job_status == 'COMPLETED':
                    response = urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                    data = json.loads(response.read())
                    text = data['results']['transcripts'][0]['transcript']
                break
            else:
                print(f"Waiting for {job_name}. Current status is {job_status}.")
            time.sleep(10)
        return text

    def process_media_format(media_format, s3_bucket_name):
        timestamp = str(int(time.time()))
        job_name = f'{job_name_prefix}_{media_format}_{timestamp}'

        s3_client = boto3.client('s3')
        s3_objects = s3_client.list_objects(Bucket=s3_bucket_name)

        file_uris = []
        for obj in s3_objects.get('Contents', []):
            if obj['Key'].lower().endswith(f'.{media_format}'):
                file_uris.append(f's3://{s3_bucket_name}/{obj["Key"]}')

        if not file_uris:
            return "", []

        transcribed_text = ""
        s3_uris = []
        for i, file_uri in enumerate(file_uris):
            text = transcribe_file(f"{job_name}_{i}", file_uri, transcribe_client, media_format, language_code)
            transcribed_text += f"Transcribed Text ({media_format.upper()}) - File {i + 1}:\n{text}\n\n"

            pdf_buffer = BytesIO()
            pdf = canvas.Canvas(pdf_buffer)
            pdf.setFont("Helvetica", 12)
            pdf.drawString(10, 800, f"Transcribed Text ({media_format.upper()}) - File {i + 1}:")
            text_lines = text.split('\n')
            for j, line in enumerate(text_lines):
                pdf.drawString(10, 780 - j * 15, line)
            pdf.save()

            pdf_filename = f'{pdf_filename_prefix}_{media_format}_{timestamp}_file_{i + 1}.pdf'
            s3_key = pdf_filename

            pdf_buffer.seek(0)

            s3_client.upload_fileobj(pdf_buffer, s3_bucket_name, s3_key)

            s3_uris.append(f's3://{s3_bucket_name}/{s3_key}')

        return transcribed_text, s3_uris

    s3_bucket_name = bucket_name

    transcribed_text_mp3, s3_uris_mp3 = process_media_format('mp3', s3_bucket_name)

    transcribed_text_mp4, s3_uris_mp4 = process_media_format('mp4', s3_bucket_name)

    return transcribed_text_mp3, s3_uris_mp3, transcribed_text_mp4, s3_uris_mp4




def process_images_and_create_pdf(bucket_name):
    bucket_name = bucket_name
s3 = boto3.client('s3')

response = s3.list_objects_v2(Bucket=bucket_name)
files_to_process = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].lower().endswith(('.png', '.jpeg'))]


for file_name in files_to_process:

    textract = boto3.client('textract')


    response = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': file_name
            }
        }
    )
    
    lines = []
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            lines.append(item["Text"])
    
    result = '\n'.join(lines)


    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    

    text_lines = result.split('\n')
    for j, line in enumerate(text_lines):
        pdf.drawString(10, 780 - j * 15, line)

    pdf.save()
    pdf_buffer.seek(0)

    pdf_key = f"{file_name.split('.')[0]}.pdf"
    s3.upload_fileobj(pdf_buffer, bucket_name, pdf_key)


    print(f"PDF created and uploaded for {file_name} as {pdf_key}")




s3_bucket_name = bucket_name
    
response = boto3.client('s3').list_objects_v2(Bucket=s3_bucket_name)
file_names = [obj['Key'] for obj in response.get('Contents', [])]

mp3_mp4_formats = any(file_name.lower().endswith(('.mp3', '.mp4')) for file_name in file_names)
image_formats = any(file_name.lower().endswith(('.png', '.jpeg')) for file_name in file_names)

if mp3_mp4_formats:
    transcribed_text_mp3, s3_uris_mp3, transcribed_text_mp4, s3_uris_mp4 = transcribe_and_create_pdf()

if image_formats:
    process_images_and_create_pdf(s3_bucket_name)


file_formats = ['.pdf', '.doc', '.txt', '.docx']
s3 = boto3.client('s3')
response = s3.list_objects(Bucket=s3_bucket_name)
file_keys = [obj['Key'] for obj in response.get('Contents', []) if any(obj['Key'].endswith(format) for format in file_formats)]

class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}



combined_content = ""

for key in file_keys:
    loader = S3FileLoader(bucket=s3_bucket_name, key=key)
    context_content = loader.load()
    context_content = [str(item) for item in context_content]
    combined_content += '\n'.join(context_content)

documents_list = [Document(page_content=combined_content)]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000)
context_texts = text_splitter.split_documents(documents_list)


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(documents=context_texts, embedding=embeddings)

retriever = db.as_retriever(search_type='mmr', search_kwargs={"k": 3})

template = """
Human: Answer truthfully based on the given question, fetch the answer only from the given text documents
Instruction:
1. If multiple files are there, read all the files each and every line accurately to generate the answer.
2. If there is no text found in the text document about the asked question, print "no result found." Do not print any results if the answer is not found, do not search the answers from outside.
3. Generate an answer whatever is available related to the question.
4. Must complete the sentence in the result fully, do not leave results incomplete format in the end.
5. If the question about a particular topic , give answer in simple about that topic only
text:{context}
question:{question}
Assistant:"""
bedrock_client = get_bedrock_client(region='us-east-1', runtime=True)
qa_prompt = PromptTemplate(template=template, input_variables=["context","question"])
chain_type_kwargs = {"prompt": qa_prompt}
llm = Bedrock(model_id="anthropic.claude-v2", client=bedrock_client)
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs=chain_type_kwargs,
    verbose=False
    )


question="what is LEO stands for"
result = qa.run(question)
print(result)