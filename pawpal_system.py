"""Core logic layer classes for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str = ""

    def update_info(self, name: str, species: str, age: int, notes: str) -> None:
        pass

    def get_profile(self) -> str:
        pass


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: int
    status: str = "not_done"

    def edit_task(self, title: str, duration: int, priority: int) -> None:
        pass

    def mark_done(self) -> None:
        pass

    def mark_not_done(self) -> None:
        pass


class Owner:
    def __init__(self, name: str, daily_time_available: int, preferences: list[str] | None = None) -> None:
        self.name = name
        self.daily_time_available = daily_time_available
        self.preferences = preferences or []

    def set_time_available(self, minutes: int) -> None:
        pass

    def update_preferences(self, preferences: list[str]) -> None:
        pass


class Scheduler:
    def __init__(self, tasks: list[Task] | None = None, time_limit: int = 0) -> None:
        self.tasks = tasks or []
        self.time_limit = time_limit

    def generate_plan(self, tasks: list[Task], time_limit: int) -> list[Task]:
        pass

    def sort_tasks_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def filter_by_time_limit(self, tasks: list[Task], time_limit: int) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass
