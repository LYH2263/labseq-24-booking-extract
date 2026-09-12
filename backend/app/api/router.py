from fastapi import APIRouter

from app.api import assays, instruments, labs, reports, results, samples, workitems

api_router = APIRouter()


@api_router.get("/health")
def health():
    return {"status": "ok", "service": "labseq"}


api_router.include_router(labs.router)
api_router.include_router(assays.router)
api_router.include_router(samples.router)
api_router.include_router(workitems.router)
api_router.include_router(results.router)
api_router.include_router(instruments.router)
api_router.include_router(reports.router)
