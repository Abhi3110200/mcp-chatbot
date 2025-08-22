from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from groq import Groq
import asyncio
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Groq Chatbot API",
             description="A FastAPI-based chatbot using Groq's language models",
             version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# Initialize Groq client
try:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    client = Groq(api_key=GROQ_API_KEY)
    logger.info("Successfully initialized Groq client")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    raise

# Models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "llama3-8b-8192"
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Groq Chatbot API"}

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        if chat_request.stream:
            return StreamingResponse(
                stream_response(chat_request),
                media_type="text/event-stream"
            )
        else:
            return await get_chat_completion(chat_request)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def get_chat_completion(chat_request: ChatRequest):
    try:
        response = client.chat.completions.create(
            messages=[msg.dict() for msg in chat_request.messages],
            model=chat_request.model,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            stream=False
        )
        return response.choices[0].message
    except Exception as e:
        logger.error(f"Error in get_chat_completion: {e}")
        raise

async def stream_response(chat_request: ChatRequest):
    try:
        response = client.chat.completions.create(
            messages=[msg.dict() for msg in chat_request.messages],
            model=chat_request.model,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
                await asyncio.sleep(0.01)  # Small delay to prevent overwhelming the client
        
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Error in stream_response: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
