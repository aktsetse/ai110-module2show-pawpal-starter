from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def _build_owner_with_tasks() -> Owner:
    owner = Owner(name="Alex", daily_time_available=120)
    dog = Pet(name="Milo", species="Dog", age=4)
    cat = Pet(name="Luna", species="Cat", age=2)

    dog.add_task(Task(description="Long walk", duration_minutes=40, frequency="daily", priority=2))
    dog.add_task(Task(description="Quick feed", duration_minutes=10, frequency="daily", priority=1))
    cat.add_task(Task(description="Weekly brush", duration_minutes=15, frequency="weekly", priority=2, due_weekday=2))
    cat.add_task(Task(description="Puzzle toy", duration_minutes=20, frequency="as_needed", priority=3))

    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


def test_sort_tasks_by_duration_asc() -> None:
    owner = _build_owner_with_tasks()
    scheduler = Scheduler(owner)

    tasks = owner.get_all_tasks()
    sorted_tasks = scheduler.sort_tasks(tasks, mode="duration_asc")

    assert [t.description for t in sorted_tasks][:2] == ["Quick feed", "Weekly brush"]


def test_filter_by_pet_and_status() -> None:
    owner = _build_owner_with_tasks()
    scheduler = Scheduler(owner)

    tasks = owner.get_all_tasks()
    tasks[0].mark_done()

    filtered = scheduler.filter_tasks(tasks, pet_name="Milo", status="not_done")
    assert len(filtered) == 1
    assert filtered[0].description == "Quick feed"


def test_recurring_due_tasks_weekday() -> None:
    owner = _build_owner_with_tasks()
    scheduler = Scheduler(owner)

    tasks = owner.get_all_tasks()
    due_on_wed = scheduler.get_due_tasks(tasks, weekday=2, include_as_needed=False)

    names = [t.description for t in due_on_wed]
    assert "Weekly brush" in names
    assert "Puzzle toy" not in names


def test_detect_conflicts_with_preferred_times() -> None:
    owner = Owner(name="Sam", daily_time_available=90)
    pet = Pet(name="Mochi", species="Cat", age=3)

    pet.add_task(
        Task(
            description="Medication",
            duration_minutes=20,
            frequency="daily",
            priority=1,
            preferred_start_minute=8 * 60,
        )
    )
    pet.add_task(
        Task(
            description="Breakfast",
            duration_minutes=15,
            frequency="daily",
            priority=1,
            preferred_start_minute=8 * 60 + 10,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())

    assert conflicts
    assert conflicts[0] == ("Medication", "Breakfast")


def test_mark_task_complete_creates_next_daily_occurrence() -> None:
    owner = Owner(name="Kim", daily_time_available=60)
    pet = Pet(name="Nova", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        description="Daily walk",
        duration_minutes=30,
        frequency="daily",
        due_date=date.today(),
    )
    pet.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.frequency == "daily"
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert task.completed is True
    assert len(pet.tasks) == 2


def test_mark_task_complete_creates_next_weekly_occurrence() -> None:
    owner = Owner(name="Kim", daily_time_available=60)
    pet = Pet(name="Nova", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        description="Weekly bath",
        duration_minutes=20,
        frequency="weekly",
        due_date=date.today(),
    )
    pet.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.frequency == "weekly"
    assert next_task.due_date == date.today() + timedelta(days=7)
    assert task.completed is True


def test_conflict_warning_for_same_scheduled_time() -> None:
    owner = Owner(name="Pat", daily_time_available=60)
    pet_a = Pet(name="Milo", species="Dog", age=4)
    pet_b = Pet(name="Luna", species="Cat", age=2)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    pet_a.add_task(
        Task(
            description="Dog breakfast",
            duration_minutes=15,
            frequency="daily",
            scheduled_time="08:00",
        )
    )
    pet_b.add_task(
        Task(
            description="Cat breakfast",
            duration_minutes=10,
            frequency="daily",
            scheduled_time="08:00",
        )
    )

    scheduler = Scheduler(owner)
    warnings = scheduler.get_conflict_warnings(owner.get_all_tasks())

    assert warnings
    assert "Dog breakfast" in warnings[0]
    assert "Cat breakfast" in warnings[0]
