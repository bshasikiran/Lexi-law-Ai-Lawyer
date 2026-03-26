⚖️ LexiLaw.ai – Simple Explanation
🔍 What this project actually is

👉 It’s an AI Legal Assistant that:

Answers legal questions
Predicts court judgments
Generates legal documents

💡 Think of it like:

“ChatGPT + Indian Law Knowledge + Case Prediction System”

🧠 Core Idea (VERY IMPORTANT)

This project uses something called:

👉 RAG (Retrieval-Augmented Generation)

Meaning:

It searches legal data (IPC laws)
Then AI (Gemini) generates answers using that data

📌 So it’s NOT just guessing — it’s law-based answering

⚙️ How it Works (Step-by-Step Flow)
🧩 Step 1: User Input
Ask question OR upload case file
🧩 Step 2: Retrieval
Uses:
IPC dataset
Case documents
Stored using:
InLegalBERT embeddings
FAISS / Redis (fast search)
🧩 Step 3: AI Processing
Gemini generates response
Uses context from retrieved legal data
🧩 Step 4: Output
Legal answer
Judgment prediction
OR legal document
🚀 Key Features (Explained Simply)
✅ 1. IPC-based Answers
Uses Indian Penal Code
Gives accurate + law-based responses

👉 Not generic AI answers

📜 2. Legal Document Generator

You type:

“Create rental agreement”

It generates:
Ready-to-use .docx file

💡 Useful for:

Rental agreements
FIR drafts
Legal notices
🔍 3. Judgment Prediction (🔥 Advanced Feature)
Uses Bi-GRU Neural Network
Trained on:
Cases from 1947–2020

👉 Predicts:

Guilty / Not Guilty
Court outcome
💬 4. Chatbot Interface
Built with:
Streamlit
Simple UI to:
Ask questions
Upload files
🛠️ Tech Stack (Understand This Well 👇)
Component	Role
Gemini API	AI brain
InLegalBERT	Converts legal text → embeddings
FAISS / Redis	Fast search system
Python	Backend logic
Streamlit	UI
🧠 Important AI Concepts Used
1. 🧩 RAG Pipeline
Retrieve → Generate
2. 📊 Embeddings
Converts text → vectors
Helps AI “understand meaning”
3. 🤖 Bi-GRU Model
Deep learning model for:
Sequence prediction (legal cases)
📁 Project Structure (Simple View)
app.py                → Main app
laws_json/            → Legal data
ipc_embed_db/         → Embeddings
templates/            → UI
static/               → Generated docs
views/                → Logic files
requirements.txt      → Dependencies
