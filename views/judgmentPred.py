import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from PIL import Image
import google.generativeai as genai

load_dotenv()

# Initialize Gemini
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model_gemini = genai.GenerativeModel("gemini-2.0-flash-exp")
except Exception as e:
    print(f"Gemini init error: {e}")
    model_gemini = None

def extract_text_from_file(file_path, file_type):
    """Extract text from various file types."""
    text = ""
    try:
        if file_type == "pdf":
            pdf_reader = PdfReader(file_path)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif file_type == "docx":
            doc = DocxDocument(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
        elif file_type == "image":
            # For now, just return a message
            text = "Image analysis requires OCR setup. Please use PDF or DOCX."
        else:
            text = "Unsupported file type."
    except Exception as e:
        print(f"Extract error: {e}")
        text = f"Error reading file: {str(e)}"
    
    return text[:5000] if text else "No text extracted"  # Limit text length

def predict_verdict(case_details):
    """Predict verdict using Gemini."""
    if not model_gemini:
        return {
            "verdict": "Unable to predict",
            "analysis": "AI service unavailable. Please check configuration."
        }
    
    if len(case_details) < 50:
        return {
            "verdict": "Insufficient Data",
            "analysis": "Please provide more case details for analysis."
        }
    
    prompt = f"""
    You are a legal AI assistant. Analyze this case and predict the likely verdict.
    
    Case Details:
    {case_details[:3000]}
    
    Provide:
    1. Predicted Verdict: (Guilty/Not Guilty/Requires More Information)
    2. Brief Analysis: Key factors that influence this prediction
    3. Relevant Laws: Applicable IPC sections
    
    Keep response concise and professional.
    """
    
    try:
        response = model_gemini.generate_content(prompt)
        analysis = response.text.strip()
        
        # Simple verdict extraction
        verdict = "Requires Analysis"
        if "guilty" in analysis.lower() and "not guilty" not in analysis.lower():
            verdict = "Likely Guilty"
        elif "not guilty" in analysis.lower():
            verdict = "Likely Not Guilty"
        
        return {
            "verdict": verdict,
            "analysis": analysis
        }
    except Exception as e:
        print(f"Predict error: {e}")
        return {
            "verdict": "Error",
            "analysis": f"Unable to analyze: {str(e)}"
        }