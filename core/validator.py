from typing import Dict, Set
from incident.models import Incident


class IncidentAssignmentValidator:
    
    def __init__(self, rules_by_type: Dict[str, Set[str]]):
        self.rules_by_type = rules_by_type

    def is_assignment_valid(self, incident: Incident, operator_name: str) -> bool:
        return operator_name in self.rules_by_type.get(incident.incident_type, set())