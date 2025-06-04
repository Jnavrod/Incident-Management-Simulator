import re
from datetime import datetime
from typing import List, Iterator
from .models import Incident


def filter_incidents_by_status(incidents: List[Incident], status: str) -> Iterator[Incident]:
    return (incident for incident in incidents if incident.status == status)


def filter_incidents_by_operator(incidents: List[Incident], operator_name: str) -> Iterator[Incident]:
    return (incident for incident in incidents if incident.assigned_operator == operator_name)


def filter_incidents_by_date(incidents: List[Incident], start_date: datetime, end_date: datetime) -> Iterator[Incident]:
    return (incident for incident in incidents if start_date <= incident.created_at <= end_date)

def filter_incidents_by_text(incidents: List[Incident], search_pattern: str) -> Iterator[Incident]:
    pattern = re.compile(search_pattern)
    return (incident for incident in incidents if pattern.search(incident.description))