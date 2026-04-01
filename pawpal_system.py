"""Core logic layer classes for PawPal+.

This module is intentionally UI-agnostic so it can be tested from CLI first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class Task:
    """A single pet-care activity."""

    description: str
    duration_minutes: int
    frequency: str  # daily, weekly, as_needed
    completed: bool = False
    priority: int = 3  # 1 = highest urgency, larger = lower urgency
    pet_name: str = ""
    due_weekday: int | None = None  # 0=Mon ... 6=Sun, used for weekly tasks
    due_date: date | None = None
    scheduled_time: str | None = None  # HH:MM
    preferred_start_minute: int | None = None  # Minutes after midnight

    def __post_init__(self) -> None:
        """Validate required task fields after initialization."""
        if not self.description.strip():
            raise ValueError("Task description cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than 0 minutes.")
        if self.priority < 1:
            raise ValueError("Task priority must be >= 1.")

        valid_frequencies = {"daily", "weekly", "as_needed"}
        if self.frequency not in valid_frequencies:
            raise ValueError(f"Task frequency must be one of {sorted(valid_frequencies)}.")

        if self.frequency in {"daily", "weekly"} and self.due_date is None:
            self.due_date = date.today()
        if self.frequency == "weekly" and self.due_weekday is None:
            self.due_weekday = 0
        if self.due_weekday is not None and not 0 <= self.due_weekday <= 6:
            raise ValueError("due_weekday must be between 0 (Mon) and 6 (Sun).")
        if self.scheduled_time is not None:
            self._validate_scheduled_time(self.scheduled_time)
        if self.preferred_start_minute is not None and self.preferred_start_minute < 0:
            raise ValueError("preferred_start_minute must be >= 0.")

    def edit_task(
        self,
        description: str | None = None,
        duration_minutes: int | None = None,
        frequency: str | None = None,
        priority: int | None = None,
        due_weekday: int | None = None,
        due_date: date | None = None,
        scheduled_time: str | None = None,
        preferred_start_minute: int | None = None,
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
            valid_frequencies = {"daily", "weekly", "as_needed"}
            if frequency not in valid_frequencies:
                raise ValueError(f"Task frequency must be one of {sorted(valid_frequencies)}.")
            self.frequency = frequency

        if priority is not None:
            if priority < 1:
                raise ValueError("Task priority must be >= 1.")
            self.priority = priority

        if due_weekday is not None:
            if not 0 <= due_weekday <= 6:
                raise ValueError("due_weekday must be between 0 (Mon) and 6 (Sun).")
            self.due_weekday = due_weekday

        if due_date is not None:
            self.due_date = due_date

        if scheduled_time is not None:
            self._validate_scheduled_time(scheduled_time)
            self.scheduled_time = scheduled_time

        if preferred_start_minute is not None:
            if preferred_start_minute < 0:
                raise ValueError("preferred_start_minute must be >= 0.")
            self.preferred_start_minute = preferred_start_minute

    @staticmethod
    def _validate_scheduled_time(value: str) -> None:
        """Validate a time string in HH:MM 24-hour format."""
        try:
            hour_str, minute_str = value.split(":")
            hour = int(hour_str)
            minute = int(minute_str)
        except (ValueError, AttributeError):
            raise ValueError("scheduled_time must be in HH:MM format.")

        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            raise ValueError("scheduled_time must be in HH:MM format.")

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
        task.pet_name = self.name
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
        self.last_time_blocks: list[dict[str, int | str]] = []
        self.last_conflicts: list[tuple[str, str]] = []

    def retrieve_tasks(self, pending_only: bool = True) -> list[Task]:
        """Fetch owner tasks, optionally limited to incomplete ones."""
        if pending_only:
            return self.owner.get_pending_tasks()
        return self.owner.get_all_tasks()

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_name: str | None = None,
        status: str | None = None,
        frequency: str | None = None,
    ) -> list[Task]:
        """Filter tasks by pet, status, and/or frequency."""
        filtered = tasks

        if pet_name:
            filtered = [task for task in filtered if task.pet_name == pet_name]

        if status == "done":
            filtered = [task for task in filtered if task.completed]
        elif status == "not_done":
            filtered = [task for task in filtered if not task.completed]

        if frequency:
            filtered = [task for task in filtered if task.frequency == frequency]

        return filtered

    def get_due_tasks(
        self,
        tasks: list[Task],
        weekday: int | None = None,
        include_as_needed: bool = True,
    ) -> list[Task]:
        """Return tasks due for the selected weekday."""
        if weekday is None:
            weekday = datetime.today().weekday()
        today_date = date.today()

        due: list[Task] = []
        for task in tasks:
            if task.frequency == "daily" and (task.due_date is None or task.due_date <= today_date):
                due.append(task)
            elif task.frequency == "weekly" and (task.due_date is None or task.due_date <= today_date):
                due.append(task)
            elif task.frequency == "as_needed" and include_as_needed:
                due.append(task)
        return due

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task complete and auto-create next daily/weekly occurrence."""
        if task.completed:
            return None

        task.mark_complete()
        if task.frequency not in {"daily", "weekly"}:
            return None

        step_days = 1 if task.frequency == "daily" else 7
        base_due_date = task.due_date or date.today()
        next_due_date = base_due_date + timedelta(days=step_days)

        next_task = Task(
            description=task.description,
            duration_minutes=task.duration_minutes,
            frequency=task.frequency,
            completed=False,
            priority=task.priority,
            pet_name=task.pet_name,
            due_weekday=task.due_weekday,
            due_date=next_due_date,
            scheduled_time=task.scheduled_time,
            preferred_start_minute=task.preferred_start_minute,
        )

        pet = self._find_pet_by_name(task.pet_name)
        if pet is not None:
            pet.add_task(next_task)
        return next_task

    def _find_pet_by_name(self, pet_name: str) -> Pet | None:
        """Return the owner's pet matching a name, if present."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                return pet
        return None

    def sort_tasks(self, tasks: list[Task], mode: str = "priority") -> list[Task]:
        """Sort tasks by selected mode: priority or duration."""
        if mode == "priority":
            return sorted(tasks, key=lambda t: (t.priority, t.duration_minutes, t.description.lower()))
        if mode in {"duration_asc", "time", "duration"}:
            return sorted(tasks, key=lambda t: (t.duration_minutes, t.priority, t.description.lower()))
        if mode == "duration_desc":
            return sorted(tasks, key=lambda t: (-t.duration_minutes, t.priority, t.description.lower()))

        raise ValueError("Invalid sort mode. Use: priority, duration_asc, duration_desc.")

    def sort_tasks_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority, then duration, then name."""
        return self.sort_tasks(tasks, mode="priority")

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by HH:MM scheduled_time using a lambda key."""
        return sorted(
            tasks,
            key=lambda task: self._time_key(task.scheduled_time),
        )

    def filter_by_status_or_pet(
        self,
        tasks: list[Task],
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Filter tasks by completion state and/or pet name."""
        filtered = tasks
        if completed is not None:
            filtered = [task for task in filtered if task.completed == completed]
        if pet_name is not None:
            filtered = [task for task in filtered if task.pet_name == pet_name]
        return filtered

    @staticmethod
    def _time_key(scheduled_time: str | None) -> tuple[int, int]:
        """Convert HH:MM time into a sortable tuple, placing missing times last."""
        if not scheduled_time:
            return (99, 99)
        try:
            hour_str, minute_str = scheduled_time.split(":")
            return (int(hour_str), int(minute_str))
        except (ValueError, AttributeError):
            return (99, 99)

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

    def build_time_blocks(self, tasks: list[Task], day_start_minute: int = 8 * 60) -> list[dict[str, int | str]]:
        """Build simple start/end minute blocks for a task plan."""
        blocks: list[dict[str, int | str]] = []
        current = day_start_minute

        for task in tasks:
            start = task.preferred_start_minute if task.preferred_start_minute is not None else current
            if start < current:
                start = current
            end = start + task.duration_minutes
            blocks.append(
                {
                    "pet": task.pet_name,
                    "task": task.description,
                    "start_minute": start,
                    "end_minute": end,
                }
            )
            current = end

        return blocks

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[str, str]]:
        """Detect overlapping tasks using preferred or scheduled start times."""
        conflicts: list[tuple[str, str]] = []
        timed_tasks = [task for task in tasks if self._task_start_minute(task) is not None]

        for i in range(len(timed_tasks)):
            a = timed_tasks[i]
            a_start = self._task_start_minute(a)
            if a_start is None:
                continue
            a_end = a_start + a.duration_minutes

            for j in range(i + 1, len(timed_tasks)):
                b = timed_tasks[j]
                b_start = self._task_start_minute(b)
                if b_start is None:
                    continue
                b_end = b_start + b.duration_minutes

                overlaps = a_start < b_end and b_start < a_end
                if overlaps:
                    conflicts.append((a.description, b.description))

        return conflicts

    def get_conflict_warnings(self, tasks: list[Task]) -> list[str]:
        """Return lightweight warning messages for conflicting tasks."""
        warnings: list[str] = []
        for task_a, task_b in self.detect_conflicts(tasks):
            warnings.append(f"Warning: '{task_a}' conflicts with '{task_b}'.")
        return warnings

    def _task_start_minute(self, task: Task) -> int | None:
        """Return start minute from preferred_start_minute or HH:MM scheduled_time."""
        if task.preferred_start_minute is not None:
            return task.preferred_start_minute
        if task.scheduled_time is not None:
            hour, minute = self._time_key(task.scheduled_time)
            if hour == 99:
                return None
            return hour * 60 + minute
        return None

    def generate_plan(
        self,
        time_limit: int | None = None,
        pending_only: bool = True,
        pet_name: str | None = None,
        status_filter: str | None = None,
        frequency_filter: str | None = None,
        weekday: int | None = None,
        include_as_needed: bool = True,
        sort_mode: str = "priority",
    ) -> list[Task]:
        """Build and store a daily plan from current owner tasks."""
        effective_limit = self.owner.daily_time_available if time_limit is None else time_limit

        tasks = self.retrieve_tasks(pending_only=pending_only)
        tasks = self.filter_tasks(
            tasks,
            pet_name=pet_name,
            status=status_filter,
            frequency=frequency_filter,
        )
        tasks = self.get_due_tasks(tasks, weekday=weekday, include_as_needed=include_as_needed)
        prioritized = self.sort_tasks(tasks, mode=sort_mode)
        plan = self.filter_by_time_limit(prioritized, effective_limit)

        self.last_plan = plan
        self.last_time_blocks = self.build_time_blocks(plan)
        self.last_conflicts = self.detect_conflicts(plan)
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

        base = (
            f"Planned {len(self.last_plan)} task(s) totaling {total} minutes "
            f"(limit: {limit} minutes). Tasks were selected by filters and sort order."
        )

        if self.last_conflicts:
            conflict_text = ", ".join([f"{a} vs {b}" for a, b in self.last_conflicts])
            return f"{base} Preferred-time conflicts detected: {conflict_text}."

        return base
