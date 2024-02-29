import uvicorn
from app import AssistantApi

def main():
    AssistantApi()
    uvicorn.run(
        'app:AssistantApi',
        host="0.0.0.0",
        port=8000,
        reload=True,      
        log_level="info",
        loop="asyncio",
        factory=True,
    )
    
if __name__ == '__main__':
    main()