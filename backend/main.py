from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routers import pages, auth, protected, analysis
from .services.database import init_db, engine
from .services.task_manager import cleanup_processes

app = FastAPI(
    title="Metabarcoding Web",
    description="Web application for metabarcoding data analysis",
    version="1.0.0",
    openapi_tags=[
        {"name": "Pages", "description": "HTML pages for user interface"},
        {"name": "Auth", "description": "Authentication and authorization"},
        {"name": "Analysis", "description": "Data analysis endpoints"},
    ]
)

BASE_DIR = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(protected.router, prefix="/private", tags=["protected"])
app.include_router(analysis.router)

@app.on_event("startup")
async def startup_event():
    init_db()
    print("База данных инициализирована")

@app.on_event("shutdown")
async def shutdown_event():
    print("Завершение дочерних процессов...")
    cleanup_processes()
    print("Закрытие соединений с базой данных...")
    engine.dispose()
    print("Сервер корректно завершает работу")

@app.get("/ping", tags=["Health"], summary="Health check")
async def ping():
    return {"status": "ok"}

# Для запуска с автоматическим подбором порта (опционально)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)