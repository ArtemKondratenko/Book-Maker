from dataclasses import dataclass
from typing import Literal

Outcome = Literal["first_team_win", "second_team_win", "draw"]


class Event:
  id: int
  coefficients: dict[Outcome, float]
  outcome: Outcome | None
  bets: list["Bet"]

  def __init__(self, id: int, coefficients: dict[Outcome, float]):
    self.id = id
    self.coefficients = coefficients
    self.outcome = None
    self.bets = []

  def finish(self, outcome: Outcome):
    self.outcome = outcome

  @property
  def is_finished(self) -> bool:
    return self.outcome is not None


@dataclass
class Bet:
  id: int
  money_amount: int
  outcome: Outcome
  event: Event

  def __post_init__(self):
    self.event.bets.append(self)

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
