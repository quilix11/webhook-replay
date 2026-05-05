from fastapi import APIRouter, Request, Depends, HTTPException

router = APIRouter()

async def intercept_data(request: Request):
    headers = dict(request.headers)

    try:
        data = await request.json()
    except Exception:
        data = None

    return{"headers": headers, "body": data}

@router.post("/webhooks/receive")
async def receive(payload: dict = Depends(intercept_data)):
    return {
        "headers": payload["headers"],
        "body": payload["body"]
    }


