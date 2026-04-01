from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_changes_status() -> None:
    task = Task(description="Morning walk", duration_minutes=20, frequency="daily")

    assert task.status == "not_done"
    task.mark_complete()
    assert task.status == "done"


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Milo", species="Dog", age=4)
    initial_count = len(pet.tasks)

    pet.add_task(Task(description="Feed breakfast", duration_minutes=10, frequency="daily"))

    assert len(pet.tasks) == initial_count + 1


def test_sorting_correctness_returns_chronological_order() -> None:
    owner = Owner(name="Alex", daily_time_available=90)
    pet = Pet(name="Milo", species="Dog", age=4)
    owner.add_pet(pet)

    pet.add_task(Task(description="Late walk", duration_minutes=20, frequency="daily", scheduled_time="18:30"))
    pet.add_task(Task(description="Early feed", duration_minutes=10, frequency="daily", scheduled_time="07:45"))
    pet.add_task(Task(description="Midday meds", duration_minutes=5, frequency="daily", scheduled_time="12:00"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())

    assert [task.description for task in sorted_tasks] == ["Early feed", "Midday meds", "Late walk"]


def test_recurrence_logic_daily_completion_creates_next_day_task() -> None:
    owner = Owner(name="Jordan", daily_time_available=60)
    pet = Pet(name="Mochi", species="Cat", age=3)
    owner.add_pet(pet)

    today_task = Task(
        description="Daily play",
        duration_minutes=15,
        frequency="daily",
        due_date=date.today(),
    )
    pet.add_task(today_task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(today_task)

    assert next_task is not None
    assert next_task.description == "Daily play"
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert today_task.completed is True


def test_conflict_detection_flags_duplicate_times() -> None:
    owner = Owner(name="Pat", daily_time_available=60)
    dog = Pet(name="Milo", species="Dog", age=4)
    cat = Pet(name="Luna", species="Cat", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(description="Dog breakfast", duration_minutes=15, frequency="daily", scheduled_time="08:00"))
    cat.add_task(Task(description="Cat breakfast", duration_minutes=10, frequency="daily", scheduled_time="08:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.get_conflict_warnings(owner.get_all_tasks())

    assert warnings
    assert "Dog breakfast" in warnings[0]
    assert "Cat breakfast" in warnings[0]


def test_edge_case_pet_with_no_tasks_returns_empty_list() -> None:
    pet = Pet(name="Solo", species="Dog", age=1)

    assert pet.get_pending_tasks() == []
