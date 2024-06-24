from typing import Literal

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.sql.schema import ForeignKey

Outcome = Literal["first_team_win", "second_team_win", "draw"]


class Base(DeclarativeBase, MappedAsDataclass):

    def save_in_database(self, session: Session):
        session.add(self)
        session.commit()


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    first_team_win_coefficient: Mapped[float]
    second_team_win_coefficient: Mapped[float]
    draw_coefficient: Mapped[float]
    outcome: Mapped[Outcome | None] = mapped_column(default=None, init=False)
    bets: Mapped[list["Bet"]] = relationship(back_populates="event", init=False)

    @property
    def coefficients(self) -> dict[Outcome, float]:
        return {
            "first_team_win": self.first_team_win_coefficient,
            "second_team_win": self.second_team_win_coefficient,
            "draw": self.draw_coefficient,
        }

    @property
    def is_finished(self) -> bool:
        return self.outcome is not None


class Bet(Base):
    __tablename__ = "bet"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    money_amount: Mapped[int]
    outcome: Mapped[Outcome]
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    event: Mapped[Event] = relationship(back_populates="bets", init=False)

    @property
    def potential_profit(self) -> float:
        if not self.event.is_finished:
            return self.event.coefficients[self.outcome] * self.money_amount
        return 0

    @property
    def actual_profit(self) -> float:
        if self.event.is_finished and self.outcome == self.event.outcome:
            return self.event.coefficients[self.outcome] * self.money_amount
        return 0


engine = create_engine('sqlite:///')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

event = Event(first_team_win_coefficient=2.5,
              second_team_win_coefficient=3.1,
              draw_coefficient=6.7)

event.save_in_database(session)

bet = Bet(money_amount=200, outcome="first_team_win", event_id=event.id)

bet.save_in_database(session)

print(event.coefficients)

# 1. Официальная документация — это самый лучший источник информации
# 2. Использование типизации (типовых подсказок или type hints)
# 3. Функция должна решать одну конкретную задачу
# 4. Используйте JSON в SQL, когда вам нужны неструктурированные данные
