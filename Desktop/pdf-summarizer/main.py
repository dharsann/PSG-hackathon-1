from fastapi import FastAPI,File,UploadFile,Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz,uvicorn
app=FastAPI()
# allow CORS for UI testing
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=['*'],allow_headers=["*"],)
# variable to store extracted text
uploaded_text={}
@app.post("/upload/")
async def upload_file(file:UploadFile = File(...)):
    global uploaded_text
    content=""
    if file.filename.endswith(".pdf"):
        with fitz.open(stream=await file.read(), filetype="pdf") as pdf:
            for page in pdf:
                content+=page.get_text()
    else:
        content=(await file.read()).decode('utf-8')
        # Store the extracted text in a variable
    uploaded_text[file.filename] = content
    return {"filename": file.filename, "content": content}   
@app.get("/get-text/")
async def get_text(filename: str = Form(...)):
    # Return text for a given filename
    return {"filename": filename, "content": uploaded_text.get(filename, "File not found.")}

@app.get("/")
async def home():
  
        