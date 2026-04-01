from pawpal_system import Pet, Task


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
