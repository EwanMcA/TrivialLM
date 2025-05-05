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


class QuizQuestionChoice(SQLModel, table=True):
    question_id: Optional[int] = Field(
        default=None,
        foreign_key="quizquestion.id",
        primary_key=True
    )
    choice: str
    is_answer: bool = Field(default=False)


class QuizQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    choices: List[QuizQuestionChoice] = Relationship(
        back_populates="question",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    answer: str
    quiz_id: Optional[int] = Field(foreign_key="quiz.id")

    quiz: Optional["Quiz"] = Relationship(back_populates="questions")


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    questions: List[QuizQuestion] = Relationship(
        back_populates="quiz",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    creator_id: Optional[int] = Field(foreign_key="user.id")
    
    creator: Optional[User] = Relationship(back_populates="quizzes")


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
