"""Core functional router: text analysis."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from text_intelligence.webserver.dependency.deps import get_analysis_service
from text_intelligence.webserver.models.analyze import AnalysisResult, AnalyzeRequest
from text_intelligence.webserver.services.analysis import AnalysisService

router = APIRouter(tags=["analyze"])


@router.post("/analyze", status_code=status.HTTP_200_OK, response_model=AnalysisResult)
async def analyze(
    payload: AnalyzeRequest,
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
) -> AnalysisResult:
    """Analyses the submitted text and returns a structured result.

    Args:
        payload: Request body carrying the text to analyse.
        service: Injected analysis service.

    Returns:
        The structured :class:`AnalysisResult`.
    """
    return await service.analyze(payload.text)
