from typing import Literal
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import List
from sqlalchemy.orm import Session, Mapped, DeclarativeBase
from typing import Dict
import json
from typing import Optional
from sqlalchemy import JSON


class Base(DeclarativeBase):
  pass

Outcome = Literal["first_team_win", "second_team_win", "draw"]


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    coefficients = Column(JSON)
    outcome = Column(String, nullable=True)
    bets: Mapped[List["Bet"]] =  relationship("Bet", back_populates="event")

    @property
    def coefficients_dict(self) -> Dict[Outcome, float]:
        return json.loads(str(self.coefficients))

    @coefficients_dict.setter
    def coefficients_dict(self, value: Dict[Outcome, float]):
        self.coefficients = json.dumps(value)

    @property
    def is_finished(self) -> bool:
        return self.outcome is not None

    @classmethod
    def add_event(cls,
                  coefficients_dict: Dict[Outcome, float],
                  session,
                  outcome: Optional[str] = None):
        try:
            event = cls(coefficients_dict=coefficients_dict, outcome=outcome)
            session.add(event)
            session.commit()
            print("Событие успешно добавлено в базу данных.")
        except Exception as e:
            session.rollback()
            print("Ошибка при добавлении события в базу данных:", str(e))
        finally:
            session.close()


class Bet(Base):
    __tablename__ = 'bet'
    id = Column(Integer, primary_key=True)
    money_amount: Mapped[int] = Column(Integer)
    outcome: Mapped[Outcome] = Column(String, nullable=True)
    event_id = Column(Integer, ForeignKey('event.id'))
    event: Mapped[Event] = relationship("Event", back_populates="bets")

    def __post_init__(self):
        self.event.bets.append(self)

    @property
    def coefficients_dict(self) -> Dict[Outcome, float]:
        return json.loads(str(self.coefficients))

    @coefficients_dict.setter
    def coefficients_dict(self, value: Dict[Outcome, float]):
        self.coefficients = json.dumps(value)

    @property
    def potential_profit(self) -> float:
      coefficients = self.event.coefficients_dict
      if not self.event.is_finished:
        return coefficients[self.outcome] * self.money_amount
      else:
        return 0.0

    @property
    def actual_profit(self) -> float:
      money_amount = float(self.money_amount)
      if self.event.is_finished and self.event.outcome == self.outcome:
        coefficients = self.event.coefficients_dict
        return coefficients[self.outcome] * money_amount
      else:
        return -money_amount

    def add_bet(self, session):
        session.add(self)
        session.commit()