from datetime import datetime, timedelta
from typing import List, Set
from incident.models import Incident
from incident.filters import (
    filter_incidents_by_status,
    filter_incidents_by_operator,
    filter_incidents_by_date,
    filter_incidents_by_text
)
from core.dispatcher import IncidentDispatcher
from core.escalator import IncidentEscalator
from core.validator import IncidentAssignmentValidator
from rules.default_rules import INCIDENT_TYPE_ROLE_RULES
from persistence.storage import IncidentStorageHandler

class IncidentCLI:
    def __init__(self):
        self.current_incident_id = 1
        self.incidents: List[Incident] = []
        self.history_log: List[Incident] = []
        self.available_operators: Set[str] = {"alice", "bob", "carol"}
        self.validator = IncidentAssignmentValidator(INCIDENT_TYPE_ROLE_RULES)
        self.dispatcher = IncidentDispatcher(self.available_operators, self.validator)
        self.escalator = IncidentEscalator(1)
        self.storage = IncidentStorageHandler("incidents.json")
        
        loaded_incidents = self.storage.load_all_incidents_from_json()
        
        unique_incidents = {}
        for incident in loaded_incidents:
            if incident.id not in unique_incidents:
                unique_incidents[incident.id] = incident
            else:
                if incident.created_at > unique_incidents[incident.id].created_at:
                    unique_incidents[incident.id] = incident
        
        clean_incidents = list(unique_incidents.values())
        
        for incident in clean_incidents:
            if incident.status in ("pending", "in_progress", "escalated"):
                self.incidents.append(incident)
            elif incident.status == "resolved":
                self.history_log.append(incident)
        
        if clean_incidents:
            max_id = max(int(inc.id) for inc in clean_incidents)
            self.current_incident_id = max_id + 1

    def generate_incident_id(self) -> str:
        return str(self.current_incident_id).zfill(3)

    def register_new_incident(self, incident_type: str, priority_level: str, description: str) -> None:

        new_incident = Incident(
            id=self.generate_incident_id(),
            incident_type=incident_type,
            priority_level=priority_level,
            description=description,
            created_at=datetime.now(),
            assigned_operator=None,
            status="pending"
        )
        self.incidents.append(new_incident)
        self.current_incident_id += 1
        print(f"✔ Incident created with ID: {new_incident.id}")

    def show_pending_incidents_by_priority(self) -> None:

        pending_incidents = [i for i in self.incidents if i.status in ("pending", "in_progress", "escalated")]
        if not pending_incidents:
            print("No open incidents (pending, in progress, or escalated).")
            return
        
        priority_order = {"high": 1, "medium": 2, "low": 3}
        
        def sort_key(incident):
            status_priority = 0 if incident.status == "escalated" else 1
            priority_value = priority_order.get(incident.priority_level, 3)
            return (status_priority, priority_value, incident.created_at)
        
        sorted_incidents = sorted(pending_incidents, key=sort_key)
        
        for incident in sorted_incidents:
            operator_display = incident.assigned_operator if incident.assigned_operator else "Pending"
            print(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')} | [{incident.id}] {incident.incident_type} | Priority: {incident.priority_level} | Status: {incident.status} | Operator: {operator_display}")
            print(f"Description: {incident.description}")

    def show_assignable_incidents(self) -> None:

        pending_incidents = [i for i in self.incidents if i.status == "pending"]
        if not pending_incidents:
            print("No pending incidents available for assignment.")
            return
        
        for incident in sorted(pending_incidents, key=lambda i: int(i.id)):
            print(f"[{incident.id}] {incident.incident_type} | Priority: {incident.priority_level}")
            print(f"Description: {incident.description}")

    def assign_incident_to_operator_by_id(self, incident_id: str, operator_name: str) -> None:

        formatted_id = incident_id.zfill(3)
        
        incident_found = False
        for index, incident in enumerate(self.incidents):
            if incident.id == formatted_id:
                incident_found = True
                if incident.status != "pending":
                    print(f"✖ Incident {formatted_id} is not pending (current status: {incident.status}). Only pending incidents can be assigned.")
                    return
                
                updated_incident = self.dispatcher.assign_incident_to_operator(incident, operator_name)
                if updated_incident:
                    self.incidents[index] = updated_incident
                    print("✔ Assigned successfully.")
                else:
                    print("✖ Assignment failed. Operator may be unauthorized or unavailable.")
                return
        
        if not incident_found:
            print("✖ Incident not found.")

    def show_resolvable_incidents(self) -> None:

        resolvable = [i for i in self.incidents if i.status in ("in_progress", "escalated")]
        if not resolvable:
            print("No incidents available for resolution (only in_progress or escalated incidents can be resolved).")
            return
        
        print("=== Incidents available for resolution ===")

        for incident in sorted(resolvable, key=lambda i: int(i.id)):
            print(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')} | [{incident.id}] {incident.incident_type} | Priority: {incident.priority_level} | Status: {incident.status}")
            print(f"Assigned to: {incident.assigned_operator}")
            print(f"Description: {incident.description}\n")

    def resolve_incident_by_id(self, incident_id: str) -> None:

        for index, incident in enumerate(self.incidents):
            if incident.id == incident_id:
                if incident.status not in ("in_progress", "escalated"):
                    print(f"✖ Incident {incident.id} cannot be resolved (current status: {incident.status}). Only in_progress or escalated incidents can be resolved.")
                    return
                
                if not incident.assigned_operator:
                    print(f"✖ Incident {incident.id} has no assigned operator. Assign it before resolving.")
                    return
                
                resolved_incident = Incident(
                    id=incident.id,
                    incident_type=incident.incident_type,
                    priority_level=incident.priority_level,
                    description=incident.description,
                    created_at=incident.created_at,
                    assigned_operator=incident.assigned_operator,
                    status="resolved"
                )
                
                self.history_log.append(resolved_incident)
                self.incidents.pop(index)
                print(f"✔ Incident {incident_id} resolved successfully.")
                return
        
        print("✖ Incident not found.")

    def run_escalation_process(self) -> None:

        current_time = datetime.now()
        escalations_made = 0
        
        for index, incident in enumerate(self.incidents):
            escalated_incident, reason = self.escalator.escalate_if_needed(incident, current_time)
            
            if escalated_incident:

                if not escalated_incident.assigned_operator:

                    available_ops = INCIDENT_TYPE_ROLE_RULES.get(escalated_incident.incident_type, set())
                    if available_ops:

                        assigned_operator = list(available_ops)[0]
                        escalated_incident = Incident(
                            id=escalated_incident.id,
                            incident_type=escalated_incident.incident_type,
                            priority_level=escalated_incident.priority_level,
                            description=escalated_incident.description,
                            created_at=escalated_incident.created_at,
                            assigned_operator=assigned_operator,
                            status="escalated"
                        )
                
                self.incidents[index] = escalated_incident
                escalations_made += 1

    def filter_and_display_incidents_by_status(self, status: str) -> None:

        all_incidents = self.incidents + self.history_log
        filtered = list(filter_incidents_by_status(all_incidents, status))
        
        if not filtered:
            print(f"No incidents found with status: {status}")
            return
        
        print(f"=== Incidents with status: {status} ===")
        for incident in sorted(filtered, key=lambda i: int(i.id)):
            print(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')} | [{incident.id}] {incident.incident_type} | Priority: {incident.priority_level} | Status: {incident.status}")
            print(f"Assigned to: {incident.assigned_operator}")
            print(f"Description: {incident.description}\n")

    def filter_and_display_incidents_by_operator(self, operator_name: str) -> None:

        all_incidents = self.incidents + self.history_log
        filtered = list(filter_incidents_by_operator(all_incidents, operator_name))
        
        if not filtered:
            print(f"No incidents found assigned to: {operator_name}")
            return
        
        print(f"=== Incidents assigned to: {operator_name} ===")
        for incident in sorted(filtered, key=lambda i: int(i.id)):
            print(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')} | [{incident.id}] {incident.incident_type} | Priority: {incident.priority_level} | Status: {incident.status}")
            print(f"Description: {incident.description}\n")

    def filter_and_display_incidents_by_date_range(self) -> None:

        try:
            start_date_str = input("Start date (YYYY-MM-DD): ").strip()
            end_date_str = input("End date (YYYY-MM-DD): ").strip()
            
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
            
            all_incidents = self.incidents + self.history_log
            filtered = list(filter_incidents_by_date(all_incidents, start_date, end_date))
            
            if not filtered:
                print(f"No incidents found between {start_date_str} and {end_date_str}")
                return
            
            print(f"=== Incidents between {start_date_str} and {end_date_str} ===")
            for incident in sorted(filtered, key=lambda i: int(i.id)):
                print(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')} | [{incident.id}] {incident.incident_type} | Priority: {incident.priority_level} | Status: {incident.status}")
                print(f"Assigned to: {incident.assigned_operator}")
                print(f"Description: {incident.description}\n")
        
        except ValueError:
            print("✖ Invalid date format. Please use YYYY-MM-DD format.")

    def filter_and_display_incidents_by_text(self, search_pattern: str) -> None:

        try:
            all_incidents = self.incidents + self.history_log
            filtered = list(filter_incidents_by_text(all_incidents, search_pattern))
            
            if not filtered:
                print(f"No incidents found matching pattern: {search_pattern}")
                return
            
            print(f"=== Incidents matching pattern: {search_pattern} ===")
            for incident in sorted(filtered, key=lambda i: int(i.id)):
                print(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')} | [{incident.id}] {incident.incident_type} | Priority: {incident.priority_level} | Status: {incident.status}")
                print(f"Assigned to: {incident.assigned_operator}")
                print(f"Description: {incident.description}\n")
        
        except Exception as e:
            print(f"✖ Error in search pattern: {e}")

    def export_incidents_to_json(self) -> None:

        all_incidents = self.incidents + self.history_log
        self.storage.save_all_incidents_to_json(all_incidents)
        print(f"✔ All incidents exported to {self.storage.file_path}")

    def display_history(self) -> None:

        if not self.history_log:
            print("No incidents in history.")
            return
        
        print("=== Incident History (Resolved/Escalated) ===")
        for incident in sorted(self.history_log, key=lambda i: int(i.id)):
            print(f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')} | [{incident.id}] {incident.incident_type} | Priority: {incident.priority_level} | Status: {incident.status}")
            print(f"Assigned to: {incident.assigned_operator}")
            print(f"Description: {incident.description}\n")

    def save_all_incidents(self) -> None:

        all_incidents = self.incidents + self.history_log
        
        unique_incidents = {}
        for incident in all_incidents:
            if incident.id not in unique_incidents:
                unique_incidents[incident.id] = incident
            else:
                current = unique_incidents[incident.id]
                status_priority = {
                    "resolved": 4,
                    "escalated": 3, 
                    "in_progress": 2,
                    "pending": 1
                }
                if status_priority.get(incident.status, 0) >= status_priority.get(current.status, 0):
                    unique_incidents[incident.id] = incident
        
        final_incidents = list(unique_incidents.values())
        self.storage.save_all_incidents_to_json(final_incidents)