from fastapi import APIRouter, HTTPException
from api.services import dashboardService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/market-trends")
def get_market_trends_route():
    logger.info("Route: /api/market-trends - Request received")
    try:
        data = dashboardService.get_dashboard_data()
        return data
    except Exception as e:
        logger.critical(f"Route: /api/market-trends - Critical error: {e}")
        raise HTTPException(status_code=500, detail="שגיאה פנימית בשרת בעת עיבוד נתוני דשבורד")