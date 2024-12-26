from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils import extract_pdf, extract_docx, create_prompt_template, generate_response

# Create FastAPI app
app = FastAPI()

# Allow CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving CSS and JavaScript
app.mount("/styles", StaticFiles(directory="styles"), name="styles")
app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")

# Set up the templates directory
templates = Jinja2Templates(directory="templates")

# Variable to store extracted text
uploaded_text = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the homepage with the index.html template.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file, extract its content, and store it in the global variable.
    """
    global uploaded_text
    content = ""

    try:
        # Process the file based on its type
        if file.filename.endswith(".pdf"):
            content = extract_pdf(filepath=file.file)  # Call the `extract_pdf` function
        elif file.filename.endswith(".docx"):
            content = extract_docx(filepath=file.file)  # Call the `extract_docx` function
        else:
            content = (await file.read()).decode("utf-8")

        # Store the extracted text in a variable
        uploaded_text[file.filename] = content

    except Exception as e:
        return {"error": f"An error occurred while processing the file: {e}"}

    return {"filename": file.filename, "content": content}


@app.post("/chat/")
async def chat_with_bot(message: str = Form(...)):
    """
    Process user message and generate a chatbot response.
    """
    # Combine uploaded text as context (if any)
    context = "\n".join(uploaded_text.values())
    response = generate_response(query=message, context=context)
    return {"response": response}
  
        
