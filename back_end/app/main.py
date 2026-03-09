from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings
from .database import engine, Base, SessionLocal
from .models.models import (
    Image, EmailSettings, User, 
    ProductionLine, MeasurementData, AttributeData,
    ControlChartConfig, SamplingPlan, SamplingRecord, CapabilityAnalysis,
    ControlPlan, ControlPlanItem,
    OCAP, OCAPSignal, OCAPStep, OCAPExecution, OCAPRootCause, OCAPCorrectiveAction,
    MSAStudy, MSAPart, MSAOperator, MSAMeasurement, MSAResult
)
from .routers import api

Base.metadata.create_all(bind=engine)

db = SessionLocal()
if not db.query(EmailSettings).first():
    default_email = EmailSettings(email='2395365918@qq.com')
    db.add(default_email)
    db.commit()
db.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="通用SPC采集和监测系统 API",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.IMAGES_RESULTS_DIR, exist_ok=True)
os.makedirs(settings.THUMBNAILS_RESULTS_DIR, exist_ok=True)
os.makedirs(settings.JSON_RESULTS_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.mount("/results/images", StaticFiles(directory=settings.IMAGES_RESULTS_DIR), name="result_images")
app.mount("/results/thumbnails", StaticFiles(directory=settings.THUMBNAILS_RESULTS_DIR), name="result_thumbnails")
app.mount("/results/jsons", StaticFiles(directory=settings.JSON_RESULTS_DIR), name="result_jsons")

app.include_router(api.router)


@app.get("/")
async def root():
    dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "front_end", "dist", "index.html")
    if os.path.exists(dist_path):
        return FileResponse(dist_path)
    return {"message": "PCB缺陷检测系统 API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=5000, reload=True)
