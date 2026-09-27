import os, json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

BASE = Path(__file__).resolve().parent.parent
FRONTEND = BASE / "frontend"
DATA = BASE / "data"
MODEL_DIR = BASE / "ml_outputs"
MODEL_PATH = MODEL_DIR / "model.keras"
CLASSES_PATH = MODEL_DIR / "class_names.json"

app = FastAPI(title="AgriGuard AI API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_model = None
_classes = []

def load_model():
    global _model, _classes
    if not MODEL_PATH.exists():
        return
    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(MODEL_PATH)
        if CLASSES_PATH.exists():
            _classes = json.loads(CLASSES_PATH.read_text())
    except Exception:
        _model = None

load_model()

@app.get("/api/health")
def health():
    return {"status":"ok","model_loaded":_model is not None,"classes":len(_classes)}

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    if _model is None:
        return JSONResponse(status_code=503, content={"error":"Model not installed/trained yet."})
    import numpy as np
    from PIL import Image
    import tensorflow as tf
    raw = await file.read()
    image = Image.open(__import__("io").BytesIO(raw)).convert("RGB").resize((224,224))
    x = np.asarray(image, dtype=np.float32)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = np.expand_dims(x,0)
    pred = _model.predict(x, verbose=0)[0]
    idx = int(np.argmax(pred))
    return {"class_name":_classes[idx] if idx < len(_classes) else str(idx),"confidence":float(pred[idx])}

@app.get("/api/soil-defaults")
def soil_defaults(state: str, district: str = ""):
    path = DATA / "soil_defaults.json"
    if not path.exists(): return {"state":state,"district":district,"data":None}
    data = json.loads(path.read_text())
    return {"state":state,"district":district,"data":data.get(state,{}).get(district) or data.get(state,{})}

@app.get("/api/market")
def market(state: str="", district: str="", commodity: str=""):
    key=os.getenv("DATA_GOV_API_KEY","")
    resource=os.getenv("DATA_GOV_RESOURCE_ID","9ef84268-d588-465a-a308-a864a43d0070")
    if not key:
        return {"configured":False,"message":"DATA_GOV_API_KEY is not configured.","records":[]}
    import requests
    params={"api-key":key,"format":"json","limit":100}
    # Resource-specific filters may vary; send common filter names only when supplied.
    if state: params["filters[state]"]=state
    if district: params["filters[district]"]=district
    if commodity: params["filters[commodity]"]=commodity
    r=requests.get(f"https://api.data.gov.in/resource/{resource}",params=params,timeout=20)
    r.raise_for_status()
    return r.json()

app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
@app.get("/{full_path:path}")
def frontend(full_path: str):
    requested = FRONTEND / full_path
    if requested.is_file():
        return FileResponse(requested)
    return FileResponse(FRONTEND / "index.html")
