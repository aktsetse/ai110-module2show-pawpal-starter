# PawPal+ Project Reflection

## 1. System Design

**Core user actions (simple version)**

- The user can add their pet and basic info (name, age, type).
- The user can add a care task, like a walk or feeding, and set how long it takes and how important it is.
- The user can see today’s plan, so they know what to do and in what order.

**a. Initial design**

- I am designing a pet care app with four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`.
- Mermaid class diagram is in `class_diagram.md`.
- `Owner` stores the pet owner's name, time available, and preferences.
- `Pet` stores each pet's profile info (name, species, age, notes).
- `Task` stores care work details (title, category, duration, priority, status).
- `Scheduler` is responsible for building a daily plan by sorting and filtering tasks based on limits.
- I separated data objects (`Pet`, `Task`) from planning logic (`Scheduler`) to keep the system organized and easier to test.

**b. Design changes**

- Yes. After an AI-style review of `#file:pawpal_system.py`, I added missing relationship structure to the skeleton.
- I added `pets` to `Owner` and an `add_pet()` method so "Owner has Pets" is explicit in code.
- I added `tasks` to `Pet` and an `add_task()` method so task ownership is tied to a pet instead of floating globally.
- I made these changes because they match the UML relationships better and reduce future scheduling confusion as the app grows.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
