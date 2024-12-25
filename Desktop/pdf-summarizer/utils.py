import fitz 
from docx import Document
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

def extract_pdf(filepath):
    text = ""
    try:
        pdf_document = fitz.open(filepath)
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            text += page.get_text()
        pdf_document.close()
    except Exception as e:
        return f"An error occurred: {e}"
    return text

def extract_docx(filepath):    
    text = ""
    try:
        doc = Document(filepath)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"  
    except Exception as e:
        return f"An error occurred: {e}"
    return text

def create_prompt(extracted_text):
    template = """
    You are a highly skilled document analysis assistant. Your task is to interpret and summarize the provided document text.
    
    Context:
    {document_text}
    
    Instructions:
    1. Provide a brief summary of the document.
    2. Identify the main topics or themes discussed.
    3. Highlight any specific sections or information requiring special attention.
    4. Suggest actionable insights or next steps based on the document content.

    Please respond in a structured and professional manner.
    """
    prompt = PromptTemplate(
        input_variables=["text"],
        template=template
    )
    final_prompt = prompt.format(document_text=extracted_text)
    return final_prompt

def generate_response(text):
    prompt = create_prompt(text)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
