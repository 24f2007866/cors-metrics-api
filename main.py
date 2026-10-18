
import time
import uuid
from statistics import mean

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

EMAIL = "24f2007866@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-akzu01.example.com"


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    origin = request.headers.get("origin")

    # Handle CORS preflight explicitly.
    if request.method == "OPTIONS":
        if origin == ALLOWED_ORIGIN:
            response = Response(status_code=204)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                request.headers.get("access-control-request-headers", "*")
            )
            response.headers["Access-Control-Max-Age"] = "600"
            response.headers["Vary"] = "Origin"
        else:
            response = JSONResponse(
                status_code=403,
                content={"detail": "Origin not allowed"},
            )
    else:
        response = await call_next(request)
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Vary"] = "Origin"

    elapsed = max(0.0, time.perf_counter() - start)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    return response


@app.get("/stats")
async def stats(values: str = Query(...)):
    try:
        numbers = [int(item.strip()) for item in values.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="values must be comma-separated integers",
        )

    if not numbers or not values.strip():
        raise HTTPException(status_code=400, detail="values cannot be empty")

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": mean(numbers),
    }
