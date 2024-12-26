import fitz
import os
import uuid
from docx import Document
from openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

FAISS_INDEX_DIR = "faiss_index"
PROMPT_TEMPLATE = """
    You are a highly skilled document analysis assistant. Your task is to interpret and summarize the provided document text, then use that to answer the user's question.

    Context:
    {context}
    
    Question:
    {question}

    Instructions:
    1. Provide a relevant answer to the user's question, based on the context given.
    2. Be concise.
    3. If you cannot answer the question based on the provided context, respond that you are unable to answer based on the given context.
    
    Response:
    """

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

def load_faiss_index():
    index_path = os.path.join(FAISS_INDEX_DIR, "index.faiss")
    if os.path.exists(index_path):
        return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    else:
        return FAISS.from_texts(["Initial"], embeddings, metadatas=[{'id': 'initial'}])

faiss_index = load_faiss_index()

def update_faiss_index(text_id: str, text_content: str):
    global faiss_index
    faiss_index.add_texts([text_content], metadatas=[{'id': text_id}])
    faiss_index.save_local(os.path.join(FAISS_INDEX_DIR, "index.faiss"))

def similarity_search(query: str):
    global faiss_index
    if not faiss_index:
        faiss_index = load_faiss_index()
    docs_and_scores = faiss_index.similarity_search_with_score(query, k=5)
    return [(doc.page_content, doc.metadata, score) for doc, score in docs_and_scores]

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

def create_prompt_template():
    return PromptTemplate.from_template(PROMPT_TEMPLATE)

def store_text_in_faiss(text_content: str):
    text_id = str(uuid.uuid4())
    update_faiss_index(text_id, text_content)
    return text_id

def generate_response(query, context):
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-thinking-exp:free",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(context=context, question=query)}
        ]
    )
    return response.choices[0].message.content

def process_query(query):
    retrieved_docs = similarity_search(query)
    context = "\n".join([doc[0] for doc in retrieved_docs])
    response = generate_response(query, context)
    return response, retrieved_docs

if __name__ == "_main_":
    while True:
        print("\nChoose an action:")
        print("1. Ingest PDF document")
        print("2. Ingest DOCX document")
        print("3. Ask a question")
        print("4. Perform similarity search")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            file_path = input("Enter the PDF file path: ")
            text_content = extract_pdf(file_path)
            if "An error occurred" in text_content:
                print(text_content)
            else:
                text_id = store_text_in_faiss(text_content)
                print(f"PDF text stored. id: {text_id}")
        elif choice == "2":
            file_path = input("Enter the DOCX file path: ")
            text_content = extract_docx(file_path)
            if "An error occurred" in text_content:
                print(text_content)
            else:
                text_id = store_text_in_faiss(text_content)
                print(f"DOCX text stored. id: {text_id}")
        elif choice == "3":
            query = input("Enter your question: ")
            response, source_docs = process_query(query)
            print(f"Response: \n{response}\n")
            print(f"Source Documents: {source_docs}")
        elif choice == "4":
            query = input("Enter the query to perform similarity search: ")
            results = similarity_search(query)
            if results:
                print("\nSimilarity Search Results:")
                for content, metadata, score in results:
                    print(f"\nContent: {content[:100]} ...")
                    print(f"Metadata: {metadata}")
                    print(f"Score: {score}")
            else:
                print("No text stored yet, please ingest a document.")
        elif choice == "5":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")
