from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from model import model_instance
import io

app = FastAPI(title="Crop Health Diagnostics API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...), language: str = Form("English")):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        contents = await file.read()
        prediction_result = model_instance.predict(contents, language)
        return {
            "success": True,
            "filename": file.filename,
            "prediction": prediction_result["prediction"],
            "intervention": prediction_result["intervention"],
            "status": prediction_result["status"],
            "info": prediction_result["info"],
            "ai_analysis": prediction_result["ai_analysis"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Crop Health Diagnostics API is running!"}

import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8006))
    print(f"Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
