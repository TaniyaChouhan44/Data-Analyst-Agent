from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("API_KEY"))

# Model
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

PROMPT_TEMPLATE = """
Role: You are an AI assistant that specializes in breaking down complex questions into programmable 
Python code and extracting parameters from the question for implementation.

Task: Given a specific question regarding data scraping and analysis, break it down to accomplish the 
following:

1. Scrapes data from the provided text or URL.
2. Derives parameters necessary for the analysis from the question.
3. Outputs answers to the specified sub-questions in a structured format.

Output Format:
- The response should include:
  - Clearly defined variables for parameters extracted from the question.
  - The expected output type (e.g., JSON array, image data URI).

Tone: Formal and technical.
"""

def clean_code(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        lines = code.splitlines()
        if lines[0].startswith("```python") or lines[0].startswith("```json") or lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        code = "\n".join(lines)
    return code

@app.post("/analyze/")
async def analyze_file(file: UploadFile = File(...), question: str = Form(...)):
    if not file.filename.endswith(".txt"):
        return JSONResponse(status_code=400, content={"error": "Only .txt files are supported."})

    contents = await file.read()
    text_data = contents.decode("utf-8")

    full_prompt = f"{PROMPT_TEMPLATE}\n\nData:\n{text_data}\n\nQuestion:\n{question}"

    try:
        response = model.generate_content(full_prompt)
        cleaned = clean_code(response.text)

        # Try parsing JSON if it exists
        import json
        try:
            parsed = json.loads(cleaned)
            return {"result": parsed}
        except json.JSONDecodeError:
            return {"result": cleaned}

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "TDS Data Analyst Agent is live."}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=int(os.getenv("PORT", 8000)), reload=True)
