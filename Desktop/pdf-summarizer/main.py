from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from utils import extract_pdf, extract_docx, store_text_in_faiss, process_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

uploaded_text_id = None

app.mount("/styles", StaticFiles(directory="styles"), name="styles")
app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_and_open_chatbot(file: UploadFile = File(...)):
    global uploaded_text_id

    try:
        if file.filename.endswith(".pdf"):
            text_content = extract_pdf(file.file)
        elif file.filename.endswith(".docx"):
            text_content = extract_docx(file.file)
        else:
            return {"error": "Unsupported file format. Please upload PDF or DOCX files."}

        if "An error occurred" in text_content:
            return {"error": text_content}

        uploaded_text_id = store_text_in_faiss(text_content)
        return {"message": "File uploaded and processed successfully.", "text_id": uploaded_text_id}

    except Exception as e:
        return {"error": f"An error occurred while processing the file: {e}"}


@app.post("/chat/")
async def chat_with_bot(message: str = Form(...)):
    try:
        if not uploaded_text_id:
            return {"error": "No document uploaded. Please upload a document first."}

        response, retrieved_docs = process_query(message)
        return {
            "response": response,
            "source_documents": [
                {"content": doc[0], "metadata": doc[1], "score": doc[2]}
                for doc in retrieved_docs
            ],
        }
    except Exception as e:
        return {"error": f"An error occurred while processing the query: {e}"}
