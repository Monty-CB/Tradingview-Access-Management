from fastapi import FastAPI
from tradingview import tradingview
from pydantic import BaseModel
import json

# Crea la aplicación FastAPI
app = FastAPI()

# Definir el modelo para recibir los datos en el endpoint de /access
class AccessRequest(BaseModel):
    pine_ids: list
    duration: str

@app.get("/validate/{username}")
async def validate(username: str):
    try:
        print(username)
        tv = tradingview()
        response = tv.validate_username(username)
        return response
    except Exception as e:
        print("[X] Exception Occurred:", e)
        return {"errorMessage": "Unknown Exception Occurred"}

@app.api_route("/access/{username}", methods=["GET", "POST", "DELETE"])
async def access(username: str, request: AccessRequest):
    try:
        pine_ids = request.pine_ids
        print(pine_ids)
        tv = tradingview()
        accessList = []
        for pine_id in pine_ids:
            access = tv.get_access_details(username, pine_id)
            accessList.append(access)
        
        if request.method == 'POST':
            duration = request.duration
            dNumber = int(duration[:-1])
            dType = duration[-1:]
            for access in accessList:
                tv.add_access(access, dType, dNumber)

        if request.method == 'DELETE':
            for access in accessList:
                tv.remove_access(access)
        
        return accessList
    except Exception as e:
        print("[X] Exception Occurred:", e)
        return {"errorMessage": "Unknown Exception Occurred"}

@app.get("/")
async def main():
    return "Your bot is alive!"
