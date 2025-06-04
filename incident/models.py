import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict


@dataclass(frozen=True, slots=True)
class Incident:
    id: str
    incident_type: str
    priority_level: str
    description: str
    created_at: datetime
    assigned_operator: Optional[str]
    status: str


def incident_to_dict(incident: Incident) -> Dict:

    return {
        "id": incident.id,
        "incident_type": incident.incident_type,
        "priority_level": incident.priority_level,
        "description": incident.description,
        "created_at": incident.created_at.isoformat(),
        "assigned_operator": incident.assigned_operator,
        "status": incident.status
    }


def clear_console() -> None:

    os.system('cls' if os.name == 'nt' else 'clear')


def validate_input(prompt_text: str, valid_options: List[str]) -> str:

    while True:
        user_input = input(prompt_text).strip().lower()
        if user_input in valid_options:
            return user_input
        print(f"Invalid input. Valid options are: {valid_options}")


def validate_integer_input(prompt_text: str) -> int:

    while True:
        try:
            return int(input(prompt_text))
        except ValueError:
            print("Please enter a valid integer.")