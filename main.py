from fastapi import FastAPI, HTTPException, Request, APIRouter
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
from stock_utils import StockDataGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Groq Chatbot API",
             description="A FastAPI-based chatbot using Groq's language models",
             version="1.0.0")

# Create API router for stocks
stocks_router = APIRouter(prefix="/api/stocks", tags=["stocks"])

@stocks_router.get("/{symbol}")
async def get_stock_data(symbol: str, days: int = 30):
    """
    Get mock stock data for a given symbol
    
    Args:
        symbol: Stock symbol (e.g., AAPL, GOOGL)
        days: Number of days of data to return (default: 30, max: 100)
    """
    try:
        # Validate input
        if not symbol or not isinstance(symbol, str):
            raise HTTPException(status_code=400, detail="Invalid stock symbol")
        
        days = max(1, min(days, 100))  # Limit days between 1 and 100
        
        # For demo purposes, we'll use a fixed initial price based on the symbol
        initial_prices = {
            "AAPL": 150.0,
            "GOOGL": 2800.0,
            "MSFT": 300.0,
            "AMZN": 120.0,
            "TSLA": 250.0,
            "META": 350.0,
            "NFLX": 450.0,
            "NVDA": 450.0,
            "INTC": 35.0,
            "AMD": 100.0
        }
        
        initial_price = initial_prices.get(symbol.upper(), 100.0)
        
        # Generate the data
        generator = StockDataGenerator(symbol, initial_price=initial_price)
        data = generator.get_formatted_data(days)
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "data": data,
            "count": len(data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating stock data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating stock data: {str(e)}"
        )

# Include the router in the app
app.include_router(stocks_router)

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
    temperature: float = 0.5
    max_tokens: int = 1024
    stream: bool = False

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Groq Chatbot API"}

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        # Log the incoming request for debugging
        logger.info(f"Received chat request: {chat_request}")
        
        if chat_request.stream:
            return StreamingResponse(
                stream_response(chat_request),
                media_type="text/event-stream"
            )
        else:
            return await get_chat_completion(chat_request)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
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
        # Return only content and role
        return {
            "content": response.choices[0].message.content,
            "role": "assistant"
        }
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
        
        full_content = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_content += content
                # Stream each chunk with the full content so far
                yield f"data: {json.dumps({'content': content, 'role': 'assistant'})}\n\n"
                await asyncio.sleep(0.01)
        
        # Send final message with complete content
        yield f"data: {json.dumps({'content': '', 'role': 'assistant', 'done': True})}\n\n"
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in stream_response: {error_msg}")
        yield f"data: {json.dumps({'content': f'Error: {error_msg}', 'role': 'assistant', 'error': True})}\n\n"



router = APIRouter(prefix="/api/stocks")

@router.get("/{symbol}")
async def get_stock_data(symbol: str, days: int = 30):
    # For demo purposes, we'll use a fixed initial price based on the symbol
    initial_prices = {
        "AAPL": 150.0,
        "GOOGL": 2800.0,
        "MSFT": 300.0,
        "AMZN": 120.0,
        "TSLA": 250.0
    }
    
    initial_price = initial_prices.get(symbol.upper(), 100.0)
    generator = StockDataGenerator(symbol, initial_price=initial_price)
    return generator.get_formatted_data(days)

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
