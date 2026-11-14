from fastapi import APIRouter

from app.api.v1 import (
    admin,
    ai,
    analytics,
    anomalies,
    applications,
    auth,
    candidates,
    crypto,
    jobs,
    logs,
    recruiters,
    resumes,
    stego,
    users,
)


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(candidates.router)
api_router.include_router(recruiters.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
api_router.include_router(applications.router)
api_router.include_router(ai.router)
api_router.include_router(admin.router)
api_router.include_router(logs.router)
api_router.include_router(crypto.router)
api_router.include_router(stego.router)
api_router.include_router(analytics.router)
api_router.include_router(anomalies.router)
