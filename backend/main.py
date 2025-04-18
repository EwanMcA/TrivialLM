from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html"
    )


@app.post("/generate-trivia", response_class=HTMLResponse)
def generate_trivia():
    return """
    <html>
        <h1>Look ma! HTML!</h1>
    </html>
    """

@app.get("/leagues", response_class=HTMLResponse)
def leagues(request: Request):
    return templates.TemplateResponse(
            request=request, name="leagues.html", context={
                "leagues": [
                    {"name": "League 1", "id": 1},
                    {"name": "League 2", "id": 2}
                ]
            }
    )
