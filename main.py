import uvicorn
from app.server import app  # Importar la app FastAPI

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
