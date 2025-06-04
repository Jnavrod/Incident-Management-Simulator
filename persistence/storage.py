import json
import os
from datetime import datetime
from typing import List
from incident.models import Incident, incident_to_dict


class IncidentStorageHandler:
    
    def __init__(self, file_path: str):

        self.file_path = file_path

    def save_all_incidents_to_json(self, incident_list: List[Incident]) -> None:

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump([incident_to_dict(incident) for incident in incident_list], file, indent=4)

    def load_all_incidents_from_json(self) -> List[Incident]:

        if not os.path.exists(self.file_path):
            return []
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()
                if not content:
                    return []
                raw_data = json.loads(content)
        except json.JSONDecodeError:
            print("Warning: incidents.json is invalid or empty. Starting with an empty list.")
            return []
        
        return [
            Incident(
                id=item["id"],
                incident_type=item["incident_type"],
                priority_level=item["priority_level"],
                description=item["description"],
                created_at=datetime.fromisoformat(item["created_at"]),
                assigned_operator=item["assigned_operator"],
                status=item["status"]
            )
            for item in raw_data
        ]