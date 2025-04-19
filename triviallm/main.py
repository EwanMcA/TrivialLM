from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import select

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import SessionDep, create_db_and_tables
from .models import League, Team


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
                {"name": "League 1", "id": 1},
                {"name": "League 2", "id": 2}
            ]
        }
    )


@app.post("/generate-trivia", response_class=HTMLResponse)
def generate_trivia():
    return """
    <html>
        <h1>Look ma! HTML!</h1>
    </html>
    """

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

