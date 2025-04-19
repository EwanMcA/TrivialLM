from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List


class TeamUser(SQLModel, table=True):
    __tablename__ = "team_user"
    
    team_id: Optional[int] = Field(
        default=None,
        foreign_key="team.id",
        primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None,
        foreign_key="user.id",
        primary_key=True
    )


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)

    teams: List["Team"] = Relationship(
        back_populates="users",
        link_model=TeamUser
    )


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    league_id: Optional[int] = Field(foreign_key="league.id")
    
    users: List[User] = Relationship(
        back_populates="teams",
        link_model=TeamUser
    )
    league: Optional["League"] = Relationship(back_populates="teams")


class League(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    teams: List[Team] = Relationship(back_populates="league")
