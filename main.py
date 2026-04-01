"""Temporary CLI demo for PawPal+ logic verification."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Alex", daily_time_available=60, preferences=["morning_walk"]) 

    dog = Pet(name="Milo", species="Dog", age=4, notes="High energy")
    cat = Pet(name="Luna", species="Cat", age=2, notes="Needs calm play")

    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(description="Morning walk", duration_minutes=25, frequency="daily", priority=1))
    dog.add_task(Task(description="Evening feeding", duration_minutes=10, frequency="daily", priority=1))
    cat.add_task(Task(description="Play session", duration_minutes=20, frequency="daily", priority=2))

    scheduler = Scheduler(owner)
    today_plan = scheduler.generate_plan()

    print("Today's Schedule")
    print("----------------")
    for i, task in enumerate(today_plan, start=1):
        print(
            f"{i}. {task.description} "
            f"({task.duration_minutes} min, priority {task.priority}, {task.frequency})"
        )

    print("----------------")
    print(f"Total planned time: {scheduler.get_total_minutes(today_plan)} minutes")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
