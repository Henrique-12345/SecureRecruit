from fastapi import APIRouter

from app.api.v1 import (
    admin,
    ai,
    applications,
    auth,
    candidates,
    jobs,
    logs,
    recruiters,
    resumes,
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
