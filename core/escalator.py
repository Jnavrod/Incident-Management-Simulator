from datetime import datetime, timedelta
from typing import Optional, Tuple
from incident.models import Incident


class IncidentEscalator:
    
    def __init__(self, escalation_threshold_minutes: int):

        self.escalation_threshold = timedelta(minutes=escalation_threshold_minutes)

    def escalate_if_needed(self, incident: Incident, current_time: datetime) -> Tuple[Optional[Incident], str]:

        time_exceeded = (current_time - incident.created_at) > self.escalation_threshold
        is_eligible_status = incident.status in ("pending", "in_progress")
        
        if not is_eligible_status:
            return None, f"Incident {incident.id}: Already escalated or resolved"
        
        if not time_exceeded:
            remaining_time = self.escalation_threshold - (current_time - incident.created_at)
            minutes_left = int(remaining_time.total_seconds() / 60)
            return None, f"Incident {incident.id}: Time threshold not met (needs {minutes_left} more minutes)"
        
        escalated_incident = Incident(
            id=incident.id,
            incident_type=incident.incident_type,
            priority_level=incident.priority_level,
            description=incident.description,
            created_at=incident.created_at,
            assigned_operator=incident.assigned_operator,
            status="escalated"
        )
        return escalated_incident, f"Incident {incident.id}: Successfully escalated"