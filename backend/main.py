from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routers import pages, auth, protected

app = FastAPI(title="Metabarcoding Web")

BASE_DIR = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(
    protected.router,
    prefix="/private",
    tags=["protected"]
)

# Тестовый эндпоинт для проверки
@app.get("/ping")
async def ping():
    return {"status": "ok"}