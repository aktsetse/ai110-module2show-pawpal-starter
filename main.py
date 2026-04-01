"""Temporary CLI demo for PawPal+ logic verification."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Alex", daily_time_available=90, preferences=["morning_walk"])

    dog = Pet(name="Milo", species="Dog", age=4, notes="High energy")
    cat = Pet(name="Luna", species="Cat", age=2, notes="Needs calm play")

    owner.add_pet(dog)
    owner.add_pet(cat)

    # Intentionally out of order by HH:MM to test sorting.
    dog.add_task(
        Task(
            description="Evening feeding",
            duration_minutes=10,
            frequency="daily",
            priority=1,
            scheduled_time="07:45",
        )
    )
    dog.add_task(
        Task(
            description="Morning walk",
            duration_minutes=25,
            frequency="daily",
            priority=1,
            scheduled_time="07:45",
        )
    )
    cat.add_task(
        Task(
            description="Play session",
            duration_minutes=20,
            frequency="as_needed",
            priority=2,
            scheduled_time="12:10",
        )
    )
    cat.add_task(
        Task(
            description="Brush fur",
            duration_minutes=15,
            frequency="weekly",
            priority=2,
            due_weekday=2,
            scheduled_time="09:20",
        )
    )

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()

    print("All Tasks (Original Order)")
    print("--------------------------")
    for task in all_tasks:
        print(f"[{task.pet_name}] {task.description} at {task.scheduled_time}")

    print("\nAll Tasks (Sorted by Time)")
    print("--------------------------")
    for task in scheduler.sort_by_time(all_tasks):
        print(f"[{task.pet_name}] {task.description} at {task.scheduled_time}")

    # Mark one as complete to test status filtering.
    dog.tasks[0].mark_complete()  # Evening feeding

    print("\nFiltered Tasks (Milo + not completed)")
    print("--------------------------------------")
    filtered = scheduler.filter_by_status_or_pet(all_tasks, completed=False, pet_name="Milo")
    for task in filtered:
        print(f"[{task.pet_name}] {task.description} - {task.status}")

    print("\nConflict Warnings")
    print("-----------------")
    warnings = scheduler.get_conflict_warnings(all_tasks)
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("No task conflicts detected.")


if __name__ == "__main__":
    main()
