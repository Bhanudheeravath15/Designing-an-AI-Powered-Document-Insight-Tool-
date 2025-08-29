from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF for PDF text extraction
import json
import os
from collections import Counter

app = FastAPI()

# Allow frontend or other clients to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
HISTORY_FILE = "data.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
else:
    history = []

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def summarize_text(text):
    # Placeholder for Sarvam AI integration
    try:
        # Example: call Sarvam AI API here
        # response = requests.post("SARVAM_API_URL", json={"text": text})
        # return response.json()["summary"]
        raise Exception("Simulate Sarvam down")  # Force fallback
    except:
        # Fallback: top 5 words
        words = [w.lower() for w in text.split() if w.isalpha()]
        most_common = Counter(words).most_common(5)
        return "Fallback Top Words: " + ", ".join([w[0] for w in most_common])

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDFs allowed")
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    text = extract_text_from_pdf(file_path)
    summary = summarize_text(text)

    entry = {
        "filename": file.filename,
        "summary": summary
    }
    history.append(entry)
    save_history()

    return {"filename": file.filename, "summary": summary}

@app.get("/insights")
def get_insights(filename: str = None):
    if filename:
        for entry in history:
            if entry["filename"] == filename:
                return entry
        raise HTTPException(status_code=404, detail="File not found")
    return history

