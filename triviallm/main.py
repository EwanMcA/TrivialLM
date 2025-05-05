from google import genai
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import select

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import SessionDep, create_db_and_tables
from .models import League, Team


gemini = genai.Client(api_key="AIzaSyDzsWDCBIFwazCvCes0kq5ZeEZ02Z7p1-w")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
def main(request: Request):
    # TODO: Get a user's leagues from the database
    return templates.TemplateResponse(
        request=request, name="home.html", context={
            "leagues": [
                {"name": "League 1", "id": 1, "teams": [{"name": "Team 1"}, {"name": "Team 2"}]},
                {"name": "League 2", "id": 2, "teams": [{"name": "Team 1"}, {"name": "Team 2"}]},
            ]
        }
    )

@app.get("/page-create-quiz", response_class=HTMLResponse)
def create_quiz(request: Request):
    return templates.TemplateResponse(
        request=request, name="create_quiz.html", context={}
    )


class QuizCreate(BaseModel):
    num_questions: int
    difficulty: str
    topics: list[str]


class Question(BaseModel):
    question: str
    choices: list[str]
    answer: str


class Quiz(BaseModel):
    questions: list[Question]


@app.post("/generate-quiz", response_class=HTMLResponse)
def generate_quiz(request: Request, body: QuizCreate):
    response = gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=(
            f"Generate a quiz with {body['num_questions']} questions. "
            f"Difficulty: {body['difficulty']}. "
            "Include questions from the following categories (if True): "
            f"General Knowledge: {body['general_knowledge']}. "
            f"History: {body['history']}. "
            f"Science: {body['science']}. "
            f"Geography: {body['geography']}. "
            f"Entertainment (Books): {body['entertainment_books']}. "
            f"Entertainment (Film/TV): {body['entertainment_film_tv']}."
        ),
        config={
        'response_mime_type': 'application/json',
        'response_schema': Quiz,
    },
    )

    return templates.TemplateResponse(
        request=request, name="quiz.html", context={
            "quiz": response.parsed,
        }
    )


@app.get("/leagues/{league_id}", response_class=HTMLResponse)
def league(request: Request, league_id: int, session: SessionDep):
    league = session.exec(select(League).where(League.id == league_id)).first()

    return templates.TemplateResponse(
        request=request, name="league.html", context={
            "league": league,
        }
    )


class LeagueCreate(BaseModel):
    name: str

@app.post("/leagues")
def create_league(body: LeagueCreate, session: SessionDep) -> League:
    league = League(name=body.name)
    session.add(league)
    session.commit()
    session.refresh(league)
    return league


class TeamCreate(BaseModel):
    name: str

@app.post("/leagues/{league_id}/teams")
def create_team(league_id: int, body: TeamCreate, session: SessionDep) -> Team:
    league = session.exec(select(League).where(League.id == league_id)).first()
    if body.name in [team.name for team in league.teams]:
        raise HTTPException(status_code=409, detail="Name not available")

    team = Team(name=body.name, league_id=league_id)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team

