from fastapi import APIRouter, HTTPException
from api.services import analysisService
from api.schemas.analysisSchemas import CVRequest
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze-cv")
def handle_cv_analysis_route(request: CVRequest):
    """
    Handles the POST request endpoint for CV analysis.
    """
    logger.info("Route: /api/analyze-cv - Request received")
    try:
        analysis_result = analysisService.analyze_cv(request.cv_text)
        return analysis_result
        
    except Exception as e:
        logger.critical(f"Route: /api/analyze-cv - Critical error: {e}")
        raise HTTPException(status_code=500, detail=f"שגיאה פנימית בשרת: {str(e)}")