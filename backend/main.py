from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Document Insight Tool Backend Running"}
