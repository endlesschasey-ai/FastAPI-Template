# main.py
from app import app
from app.core.config import Config

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=Config.SERVER_HOST, 
        port=Config.SERVER_PORT,
        reload=Config.DEBUG,
        workers=Config.WORKERS
    )