# AgriGuard AI - Multi-page English + Hindi

This version uses separate portals instead of a single scrolling dashboard.

English:
- index.html
- disease.html
- soil.html
- market.html
- crops.html
- voice.html

Hindi:
- hi/index.html
- hi/disease.html
- hi/soil.html
- hi/market.html
- hi/crops.html
- hi/voice.html

Run locally/Colab:
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000

The disease model is intentionally not included in this ZIP. Train it separately and place outputs in ml_outputs/.
