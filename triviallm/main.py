from typing import Annotated, Optional
from google import genai
from fastapi import Depends, FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import select, Session

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import create_db_and_tables, get_session
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
            ],
            "quizzes": [
                {"name": "Quiz 1", "id": 1},
                {"name": "Quiz 2", "id": 2},
            ],
        }
    )

@app.get("/page-create-quiz", response_class=HTMLResponse)
def create_quiz(request: Request):
    return templates.TemplateResponse(
        request=request, name="create_quiz.html", context={}
    )


################################################################
# Quiz Management
################################################################

class Question(BaseModel):
    question: str
    choices: list[str]
    answer: str


class Quiz(BaseModel):
    questions: list[Question]


@app.post("/generate-quiz", response_class=HTMLResponse)
def generate_quiz(
    request: Request,
    num_questions: Annotated[int, Form()],
    difficulty: Annotated[str, Form()],
    topics: Annotated[list[str], Form()],
    db_session: Annotated[Session, Depends(get_session)]
):
    response = gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=(
            f"Generate a quiz with {num_questions} questions. "
            f"Difficulty: {difficulty}. "
            "Include questions from the following categories: "
            f"{', '.join(topics)}. "
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


@app.post("/quizzes")
def store_quiz(body: Quiz, db_session: Annotated[Session, Depends(get_session)]) -> Quiz:
    quiz = Quiz(name="Quiz", questions=body.questions)
    db_session.add(quiz)
    db_session.commit()
    db_session.refresh(quiz)
    return quiz


################################################################
# League and Team Management
################################################################

@app.get("/leagues/{league_id}", response_class=HTMLResponse)
def league(
    request: Request,
    league_id: int, 
    db_session: Annotated[Session, Depends(get_session)],
):
    league = db_session.exec(select(League).where(League.id == league_id)).first()

    return templates.TemplateResponse(
        request=request, name="league.html", context={
            "league": league,
        }
    )


class LeagueCreate(BaseModel):
    name: str

@app.post("/leagues")
def create_league(body: LeagueCreate, db_session: Annotated[Session, Depends(get_session)]) -> League:
    league = League(name=body.name)
    db_session.add(league)
    db_session.commit()
    db_session.refresh(league)
    return league


class TeamCreate(BaseModel):
    name: str

@app.post("/leagues/{league_id}/teams")
def create_team(
    league_id: int,
    body: TeamCreate,
    db_session: Annotated[Session, Depends(get_session)],
) -> Team:
    league = db_session.exec(select(League).where(League.id == league_id)).first()
    if body.name in [team.name for team in league.teams]:
        raise HTTPException(status_code=409, detail="Name not available")

    team = Team(name=body.name, league_id=league_id)
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team
