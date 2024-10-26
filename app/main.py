import uuid

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.routers import category, products, auth, permission, review
from loguru import logger

logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message} ", level="INFO", enqueue=True)
app = FastAPI()


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid.uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info(f"Request to {request.url.path} succeeded")
        except Exception as e:
            logger.error(f"Request to {request.url.path} failed: {e}")
            response = JSONResponse({"Success": False}, status_code=500)
        return response


@app.get("/")
async def welcome() -> dict:
    return {"message": "Me e-commerce app"}

app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(review.router)
