from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI(title="Nave a la deriva")

# Fijamos "navigation" que mapea a "NAV-01"
SYSTEM_NAME = "navigation"
SYSTEM_CODE = "NAV-01"


@app.get("/status")
def get_status():
    return {"damaged_system": SYSTEM_NAME}


@app.get("/repair-bay", response_class=HTMLResponse)
def get_repair_bay():
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Repair</title>
</head>
<body>
<div class="anchor-point">{SYSTEM_CODE}</div>
</body>
</html>"""
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/teapot")
def post_teapot():
    return Response(content="I'm a teapot", status_code=418)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)