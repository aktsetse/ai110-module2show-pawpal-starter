import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner + Pets")

# Persist core objects across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_time_available=60)

owner_name = st.text_input("Owner name", value="Jordan")
daily_time = st.number_input(
    "Daily time available (minutes)", min_value=0, max_value=600, value=60
)

# Keep the stored owner in sync with UI input.
st.session_state.owner.name = owner_name
st.session_state.owner.set_time_available(int(daily_time))

with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Pet age", min_value=0, max_value=40, value=2)
    notes = st.text_input("Notes", value="")
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    new_pet = Pet(name=pet_name, species=species, age=int(age), notes=notes)
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added pet: {pet_name}")

if st.session_state.owner.pets:
    st.write("Current pets:")
    pet_rows = [
        {
            "name": pet.name,
            "species": pet.species,
            "age": pet.age,
            "notes": pet.notes,
            "task_count": len(pet.tasks),
        }
        for pet in st.session_state.owner.pets
    ]
    st.table(pet_rows)
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Tasks are now added to real Pet objects in the backend logic layer.")

if st.session_state.owner.pets:
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox(
            "Which pet is this task for?",
            [pet.name for pet in st.session_state.owner.pets],
        )
        task_description = st.text_input("Task description", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"], index=0)
        priority_label = st.selectbox("Priority", ["high", "medium", "low"], index=0)
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        priority_map = {"high": 1, "medium": 2, "low": 3}
        selected_pet = next(
            pet for pet in st.session_state.owner.pets if pet.name == selected_pet_name
        )
        selected_pet.add_task(
            Task(
                description=task_description,
                duration_minutes=int(duration),
                frequency=frequency,
                priority=priority_map[priority_label],
            )
        )
        st.success(f"Added task to {selected_pet_name}: {task_description}")

all_task_rows = []
for pet in st.session_state.owner.pets:
    for task in pet.tasks:
        all_task_rows.append(
            {
                "pet": pet.name,
                "task": task.description,
                "duration_minutes": task.duration_minutes,
                "frequency": task.frequency,
                "priority": task.priority,
                "status": task.status,
            }
        )

if all_task_rows:
    st.write("Current tasks:")
    st.table(all_task_rows)
else:
    st.info("No tasks yet. Add pets first, then add tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button now calls your Scheduler logic.")

if st.button("Generate schedule"):
    scheduler = Scheduler(st.session_state.owner)
    todays_plan = scheduler.generate_plan()

    if todays_plan:
        schedule_rows = [
            {
                "task": task.description,
                "duration_minutes": task.duration_minutes,
                "frequency": task.frequency,
                "priority": task.priority,
            }
            for task in todays_plan
        ]
        st.write("Today's Schedule:")
        st.table(schedule_rows)
        st.caption(scheduler.explain_plan())
    else:
        st.info("No tasks were scheduled. Add tasks or increase available time.")
