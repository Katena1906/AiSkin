import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io

from skin_analyzer import skin_analyzer
from smart_parser import SmartProductRecommender
from history_manager import HistoryManager
from ingredient_analyzer import IngredientAnalyzer
from product_comparator import ProductComparator


app = FastAPI(title="AI Skin Disease Classifier", version="2.0.0")

@app.get("/")
async def root():
    return {"message": "AI Skin Disease Classifier API", "docs": "/docs", "health": "/api/health"}

@app.get("/api")
async def api_root():
    return {"message": "AI Skin Disease Classifier API", "health": "/api/health"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = SmartProductRecommender()
history_manager = HistoryManager()
ingredient_analyzer = IngredientAnalyzer()
product_comparator = ProductComparator()

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": skin_analyzer.model is not None,
        "device": str(skin_analyzer.device),
        "classes": skin_analyzer.classes
    }

@app.post("/api/analyze")
async def analyze_skin(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image_bytes = io.BytesIO(contents)
        result = skin_analyzer.analyze_image(image_bytes)
        
        recommendations = await recommender.get_smart_recommendations(
            result['disease'], 
            result['confidence']
        )
        
        return {
            "success": True,
            "analysis": result,
            "recommendations": recommendations
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/history")
async def get_history():
    return history_manager.get_history()

@app.delete("/api/history/{analysis_id}")
async def delete_history_item(analysis_id: str):
    success = history_manager.delete_analysis(analysis_id)
    return {"success": success}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
