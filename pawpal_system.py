"""Core logic layer classes for PawPal+.

This module is intentionally UI-agnostic so it can be tested from CLI first.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet-care activity."""

    description: str
    duration_minutes: int
    frequency: str  # e.g., "daily", "weekly", "as_needed"
    completed: bool = False
    priority: int = 3  # 1 = highest urgency, larger = lower urgency

    def __post_init__(self) -> None:
        """Validate required task fields after initialization."""
        if not self.description.strip():
            raise ValueError("Task description cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than 0 minutes.")
        if self.priority < 1:
            raise ValueError("Task priority must be >= 1.")

    def edit_task(
        self,
        description: str | None = None,
        duration_minutes: int | None = None,
        frequency: str | None = None,
        priority: int | None = None,
    ) -> None:
        """Update task fields with optional validation."""
        if description is not None:
            if not description.strip():
                raise ValueError("Task description cannot be empty.")
            self.description = description

        if duration_minutes is not None:
            if duration_minutes <= 0:
                raise ValueError("Task duration must be greater than 0 minutes.")
            self.duration_minutes = duration_minutes

        if frequency is not None:
            self.frequency = frequency

        if priority is not None:
            if priority < 1:
                raise ValueError("Task priority must be >= 1.")
            self.priority = priority

    def mark_done(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def mark_complete(self) -> None:
        """Mark the task as completed (alias for compatibility)."""
        self.completed = True

    def mark_not_done(self) -> None:
        """Mark the task as not completed."""
        self.completed = False

    @property
    def status(self) -> str:
        """Return a string status for completion state."""
        return "done" if self.completed else "not_done"


@dataclass
class Pet:
    """Pet profile and the tasks tied to this pet."""

    name: str
    species: str
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate pet fields after initialization."""
        if not self.name.strip():
            raise ValueError("Pet name cannot be empty.")
        if self.age < 0:
            raise ValueError("Pet age cannot be negative.")

    def update_info(
        self,
        name: str | None = None,
        species: str | None = None,
        age: int | None = None,
        notes: str | None = None,
    ) -> None:
        """Update pet profile fields with basic validation."""
        if name is not None:
            if not name.strip():
                raise ValueError("Pet name cannot be empty.")
            self.name = name

        if species is not None:
            self.species = species

        if age is not None:
            if age < 0:
                raise ValueError("Pet age cannot be negative.")
            self.age = age

        if notes is not None:
            self.notes = notes

    def get_profile(self) -> str:
        """Return a short profile summary string."""
        return f"{self.name} ({self.species}, age {self.age})"

    def add_task(self, task: Task) -> None:
        """Attach a new task to this pet."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove the first task matching a description."""
        for i, task in enumerate(self.tasks):
            if task.description == description:
                del self.tasks[i]
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's incomplete tasks."""
        return [task for task in self.tasks if not task.completed]


class Owner:
    """Owner profile with one-to-many relationship to pets."""

    def __init__(
        self,
        name: str,
        daily_time_available: int,
        preferences: list[str] | None = None,
        pets: list[Pet] | None = None,
    ) -> None:
        """Create an owner with optional preferences and pets."""
        if not name.strip():
            raise ValueError("Owner name cannot be empty.")
        if daily_time_available < 0:
            raise ValueError("Daily time available cannot be negative.")

        self.name = name
        self.daily_time_available = daily_time_available
        self.preferences = preferences or []
        self.pets = pets or []

    def set_time_available(self, minutes: int) -> None:
        """Set the owner's available time for daily planning."""
        if minutes < 0:
            raise ValueError("Daily time available cannot be negative.")
        self.daily_time_available = minutes

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's planning preferences."""
        self.preferences = preferences

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's profile."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove the first pet matching the given name."""
        for i, pet in enumerate(self.pets):
            if pet.name == pet_name:
                del self.pets[i]
                return True
        return False

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all owned pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks across pets."""
        return [task for task in self.get_all_tasks() if not task.completed]


class Scheduler:
    """Task planning engine across all pets for one owner."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler bound to one owner."""
        self.owner = owner
        self.last_plan: list[Task] = []

    def retrieve_tasks(self, pending_only: bool = True) -> list[Task]:
        """Fetch owner tasks, optionally limited to incomplete ones."""
        if pending_only:
            return self.owner.get_pending_tasks()
        return self.owner.get_all_tasks()

    def sort_tasks_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority, then duration, then name."""
        # Lower priority number means more urgent. Tie-breaker: shorter tasks first.
        return sorted(tasks, key=lambda t: (t.priority, t.duration_minutes, t.description.lower()))

    def filter_by_time_limit(self, tasks: list[Task], time_limit: int) -> list[Task]:
        """Select tasks greedily without exceeding the time limit."""
        if time_limit < 0:
            raise ValueError("Time limit cannot be negative.")

        selected: list[Task] = []
        used = 0
        for task in tasks:
            if used + task.duration_minutes <= time_limit:
                selected.append(task)
                used += task.duration_minutes
        return selected

    def generate_plan(self, time_limit: int | None = None, pending_only: bool = True) -> list[Task]:
        """Build and store a daily plan from current owner tasks."""
        effective_limit = self.owner.daily_time_available if time_limit is None else time_limit

        tasks = self.retrieve_tasks(pending_only=pending_only)
        prioritized = self.sort_tasks_by_priority(tasks)
        plan = self.filter_by_time_limit(prioritized, effective_limit)
        self.last_plan = plan
        return plan

    def get_total_minutes(self, tasks: list[Task]) -> int:
        """Return the total duration of a task list in minutes."""
        return sum(task.duration_minutes for task in tasks)

    def explain_plan(self) -> str:
        """Return a plain-language explanation of the last plan."""
        if not self.last_plan:
            return "No tasks were scheduled. This can happen if there are no pending tasks or no available time."

        total = self.get_total_minutes(self.last_plan)
        limit = self.owner.daily_time_available

        lines = [
            f"Planned {len(self.last_plan)} task(s) totaling {total} minutes (limit: {limit} minutes).",
            "Tasks were selected by priority first, then by shorter duration when priorities tied.",
        ]
        return " ".join(lines)
