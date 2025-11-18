import uvicorn
import threading
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# טעינת משתני סביבה (חובה בהתחלה)
load_dotenv()

from runUpdate import run_full_update
from api.routes.dashboard import router as dashboard_router
from api.routes.analysis import router as analysis_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal Job Market Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])
app.include_router(analysis_router, prefix="/api", tags=["Analysis"])


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_full_update, "interval", hours=1)
    scheduler.start()
    logger.info("Scheduler started.")


if __name__ == "__main__":
    logger.info("Starting API...")

    threading.Thread(target=start_scheduler, daemon=True).start()
    threading.Thread(target=run_full_update, daemon=True).start()

    # שינוי חשוב: 0.0.0.0 מאפשר גישה מבחוץ (חובה לענן)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")