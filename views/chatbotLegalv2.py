import json
from upstash_redis import Redis
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Initialize Redis with error handling
try:
    redis_client = Redis(
        url=os.getenv("UPSTASH_REDIS_URL"),
        token=os.getenv("UPSTASH_REDIS_TOKEN")
    )
except Exception as e:
    print(f"Redis connection error: {e}")
    redis_client = None

# Initialize Gemini
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
except Exception as e:
    print(f"Gemini initialization error: {e}")
    gemini_model = None

SYSTEM_PROMPT = """
You are an AI Legal Assistant specialized in Indian law. 
Provide accurate, clear, and concise answers based on the Indian Penal Code.
Keep responses brief and to the point.
"""

def gemini_generate(prompt: str) -> str:
    """Generate response using Gemini with error handling."""
    if not gemini_model:
        return "AI service temporarily unavailable. Please check API configuration."
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Unable to generate response. Please try again."

def load_chat(chat_name: str) -> dict:
    """Load chat from Redis or return empty chat."""
    if not redis_client:
        return {"generated": [], "past": []}
    
    try:
        chat_data = redis_client.get(chat_name)
        if chat_data:
            return json.loads(chat_data)
    except Exception as e:
        print(f"Load chat error: {e}")
    
    return {"generated": [], "past": []}

def save_chat(chat_name: str, chat_data: dict) -> None:
    """Save chat to Redis with error handling."""
    if not redis_client:
        return
    
    try:
        redis_client.set(chat_name, json.dumps(chat_data))
    except Exception as e:
        print(f"Save chat error: {e}")

def create_new_chat() -> str:
    """Create a new chat."""
    timestamp = int(time.time())
    new_chat_name = f"Chat_{timestamp}"
    chat_data = {"generated": [], "past": []}
    save_chat(new_chat_name, chat_data)
    return new_chat_name

def get_chat_list() -> list:
    """Get list of chat names."""
    if not redis_client:
        return []
    
    try:
        keys = redis_client.keys('Chat_*')
        return list(keys) if keys else []
    except Exception as e:
        print(f"Get chat list error: {e}")
        return []

def process_input(chat_name: str, user_input: str) -> str:
    """Process user input and return response."""
    current_chat = load_chat(chat_name)
    
    # Build conversation context (last 5 exchanges)
    recent_history = []
    start_idx = max(0, len(current_chat["past"]) - 5)
    for i in range(start_idx, len(current_chat["past"])):
        recent_history.append(f"User: {current_chat['past'][i]}")
        if i < len(current_chat["generated"]):
            recent_history.append(f"AI: {current_chat['generated'][i]}")
    
    history_text = "\n".join(recent_history) if recent_history else ""
    
    # Create prompt
    full_prompt = f"{SYSTEM_PROMPT}\n\nConversation:\n{history_text}\n\nUser: {user_input}\nAI:"
    
    # Get response
    response = gemini_generate(full_prompt)
    
    # Update chat
    current_chat["past"].append(user_input)
    current_chat["generated"].append(response)
    save_chat(chat_name, current_chat)
    
    return response