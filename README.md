# Incident Management System

This project is a **command-line based Incident Management System** designed using Python with clean architecture principles, modularization, and a focus on maintainability and scalability. It allows users to create, assign, escalate, resolve, and filter incidents with role-based logic.

---

## Features described

- Create and store incidents with types and priority levels.
   It receives date and time information, assign an correlative ID depending on the preloaded/previous incidents in JSON file, allows to select an specific cathegory, criticity and a brief description
- View open incidents
   It shows all incidents that are not escalated, it shows detailed information about each one
- Assign incidents to available operators depending on their respective skills.
   It doesn't consider variables like max incidents allowed per operator or operator availabilities.
- Auto-escalate unresolved incidents after a time threshold.
   It's settled in 1 minute just for test it properly, if an incident reachs treshold, the system will assign automatically a random operator with the correct skill to work on that incident. Just one observation, it depends on a brief refresh when toy view the open incidents to see the updated status.
- Resolve incidents and log history.
   It allows to solve incidents only if the incident has an operator assigned.
- Filter incidents by operator, status, dates and even internal descriptions
- Save and load incident data using local JSON storage.

Additional observations:
- Most of features or functions in the interface gives a proper feedback on each step, from inputs validations to processes done.

---

## Project Structure

```
PythonLogicModules/
├── cli/
│   ├── __init__.py
│   └── interface.py           # CLI handling and user interactions
├── core/
│   ├── __init__.py
│   ├── dispatcher.py          # Logic for assigning incidents
│   ├── escalator.py           # Handles time-based escalations
│   ├── validator.py           # Input and assignment validations
├── incident/
│   ├── __init__.py
│   ├── filters.py             # Filtering logic for incidents
│   ├── models.py              # Data classes and core logic
├── logs/
│   ├── __init__.py
├── persistence/
│   ├── __init__.py
│   ├── storage.py             # Read/write JSON persistence
├── rules/
│   ├── __init__.py
│   └── default_rules.py       # Role-based rules by incident type
├── .gitignore
├── incidents.json             # Incident storage file
├── LICENSE
├── main.py                    # Entry point and menu loop
└── README.md
```

---

## How to Run

1. Make sure you have Python 3.8 or higher installed.
2. Clone or download this project.
3. Navigate to the project root
4. Run the main application:
   ```bash
   python3 main.py
   ```

---

## Example Use Cases

- Manage IT support requests in a small team.
- Simulate real-world incident workflows in NOC/SOC teams.

---

## Key Concepts Applied

- Python `@dataclass` with `slots` and `frozen` for memory-efficient models.
- Single Responsibility & modularity via separated logic files.
- CLI built with validations and robust input handling.
- Persistent storage with JSON and minimal dependencies.
- Clear separation of business logic and I/O handling.

---

## Requirements

- Python 3.8+
- No external packages required (only `json`, `os`, `datetime`, `typing`)

---

## License

Licensed under the Creative Commons Attribution-NonCommercial 4.0 International.  
More info: https://creativecommons.org/licenses/by-nc/4.0/legalcode
