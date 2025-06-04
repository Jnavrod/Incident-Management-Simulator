from typing import Optional, Set
from incident.models import Incident
from .validator import IncidentAssignmentValidator


class IncidentDispatcher:
    
    def __init__(self, available_operators: Set[str], validator: IncidentAssignmentValidator):

        self.available_operators = available_operators
        self.validator = validator

    def assign_incident_to_operator(self, incident: Incident, operator_name: str) -> Optional[Incident]:

        if (operator_name in self.available_operators and 
            self.validator.is_assignment_valid(incident, operator_name)):
            return Incident(
                id=incident.id,
                incident_type=incident.incident_type,
                priority_level=incident.priority_level,
                description=incident.description,
                created_at=incident.created_at,
                assigned_operator=operator_name,
                status="in_progress"
            )
        return None