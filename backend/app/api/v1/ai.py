from uuid import UUID

from fastapi import APIRouter, Request

from app.dependencies.auth import CurrentUser, DbSession
from app.schemas.ai import (
    AIAnalysisRead,
    AnalyzeResumeRequest,
    MatchResumeJobRequest,
)
from app.services.ai_service import AIService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze-resume", response_model=AIAnalysisRead, status_code=201)
async def analyze_resume(
    payload: AnalyzeResumeRequest,
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
) -> AIAnalysisRead:
    analysis, result = await AIService(db).analyze_resume(
        user=current_user,
        resume_id=payload.resume_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AIAnalysisRead(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_id=analysis.job_id,
        analysis_text=analysis.analysis_text,
        extracted_skills=analysis.extracted_skills,
        compatibility_score=analysis.compatibility_score,
        created_at=analysis.created_at,
        result=result,
    )


@router.post("/match-resume-job", response_model=AIAnalysisRead, status_code=201)
async def match_resume_job(
    payload: MatchResumeJobRequest,
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
) -> AIAnalysisRead:
    analysis, result = await AIService(db).analyze_resume(
        user=current_user,
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AIAnalysisRead(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_id=analysis.job_id,
        analysis_text=analysis.analysis_text,
        extracted_skills=analysis.extracted_skills,
        compatibility_score=analysis.compatibility_score,
        created_at=analysis.created_at,
        result=result,
    )


@router.get("/analyses/{analysis_id}", response_model=AIAnalysisRead)
def get_analysis(
    analysis_id: UUID, current_user: CurrentUser, db: DbSession
) -> AIAnalysisRead:
    analysis, result = AIService(db).get_analysis(analysis_id, current_user)
    return AIAnalysisRead(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_id=analysis.job_id,
        analysis_text=analysis.analysis_text,
        extracted_skills=analysis.extracted_skills,
        compatibility_score=analysis.compatibility_score,
        created_at=analysis.created_at,
        result=result,
    )
